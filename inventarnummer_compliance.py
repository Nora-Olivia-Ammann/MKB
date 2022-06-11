import os
import pandas as pd
import numpy as np
from datetime import date

from tools.inventarnummer import Inventarnummer as InvNr
from tools.excel_functions import ExcelFunctions as ExF

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


def inventarnummer_compliance(in_excel: str, tranche: str, abteilung: str, regex_pattern):
    """
    Uses RegEx patterns to check whether the Inventarnummer is correct. The RegEx pattern for each abteilung differs,
    all the existing patterns are stored in the file: "b_RegEx_Inventarnummer". For each possible problem that is
    differentiated: Missing, Double, Leading Zero, Dummy and correct Inventarnummer, a separate excel is created.
    The ones with leading zeros (e.g. (F)Vb 0001) are automatically corrected and the outgoing excel is used to
    check whether the picture filename is also wrong.
    :param regex_pattern: function form the tools.RegEx_patterns that compiles and returns the pattern for the Abteilung
    :param df_in: excel
    :param tranche: name
    :param abteilung: name
    :return: saves separate excels for each problem if they exist
    """
    # read the excel into a dataframe
    df_in = ExF.in_excel_to_df(in_excel)
    # initiate an empty list to store the dicts with the documentation, there are many here, so it is faster
    # to concat in the end
    doc_list = []
    # NAN CHECK
    # Check if all rows have an "Inventarnummer", also one cannot perform a RegEx check on a NaN so the programme
    # would stop and throw an error
    if df_in["Inventarnummer"].isnull().any():
        # create a new df with all missing elements in the chosen column
        df_nan = df_in[df_in["Inventarnummer"].isnull()]
        # drop all the rows with nan in the in_df, modify memory
        df_in.dropna(subset=["Inventarnummer"], inplace=True)
        df_in.reset_index(inplace=True)  # reset the index
        df_in.pop("index")  # when resetting the index it is saved as a new column
        ExF.save_df_excel(df_nan, f"{tranche}_{today}_Inventarnummer_Fehlen")
        # Write documentation
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": df_in, "Schlüssel Excel": "-",
             "Feld": "Inventarnummer", "Was": "Fehlen Inventarnummer", "Resultat": f"{len(df_nan)} fehlen",
             "Output Dokument": f"{tranche}_{today}_Inventarnummer_Fehlen", "Ersetzt Hauptexcel": "unterteilt es"})
    else:
        # Write documentation
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": df_in, "Schlüssel Excel": "-",
             "Feld": "Inventarnummer", "Was": "Fehlen Inventarnummer", "Resultat": f"keine fehlen",
             "Output Dokument": f"-", "Ersetzt Hauptexcel": "unterteilt es"})
    # get the RegEx pattern
    pattern_correct, pattern_leading_zero, pattern_dummy = regex_pattern
    ###########
    # LEADING ZERO
    list_leading_zero = []
    # remove the leading zeros from Inventarnummern, this is done now as doubles may be contained
    for index, value in df_in["Inventarnummer"].iteritems():
        # RegEx only takes str if it is a int or float it will throw an error
        try:
            # check for Inventarnummer with leading zero
            if pattern_leading_zero.match(value):
                # split the Inventarnummer at the blank space
                splt_inventar = value.split(" ")
                # strip the 0 on the left side from the number and replace the old value with that
                splt_inventar[1] = splt_inventar[1].lstrip("0")
                # join the strings from the list
                joined = " ".join(splt_inventar)
                # replace the value in the in_df
                df_in.loc[index, "Inventarnummer"] = joined
                # add the new number to the documentation df
                list_leading_zero.append(
                    {"Alte Inventarnummer": value, "Neue Inventarnummer": joined, "Tranche": df_in.loc[index, "Tranche"],
                     "Ordner Bild": df_in.loc[index, "Ordner Bild"], "Unique_ID": df_in.loc[index, "Unique_ID"],
                     "Inventar Sortierbar": df_in.loc[index, "Inventar Sortierbar"], "Bilddatei kontrolliert": np.nan})
        # here we ignore the error
        except TypeError:
            continue
    if len(list_leading_zero) != 0:
        df_leading_zero = pd.DataFrame.from_records(list_leading_zero)
        # save the excel that contains the information of the changed inventarnummer
        df_leading_zero.sort_values(by=["Ordner Bild", "Inventar Sortierbar"], inplace=True, ignore_index=True)
        ExF.save_df_excel(df_leading_zero, f"{tranche}_{today}_Inventarnummer_Führende_0")
        # Write documentation
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": df_in, "Schlüssel Excel": "-",
             "Feld": "Inventarnummer", "Was": "Führende Null",
             "Resultat": f"{len(df_leading_zero)} mit führenden null wurden im Excel ersetzt",
             "Output Dokument": f"{tranche}_{today}_Inventarnummer_Führende_0", "Ersetzt Hauptexcel": "unterteilt es"})
    else:
        # Write documentation
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": df_in, "Schlüssel Excel": "-",
             "Feld": "Inventarnummer", "Was": "Führende Null", "Resultat": f"keine führende null",
             "Output Dokument": f"-", "Ersetzt Hauptexcel": "-"})
    #######################################
    # DUPLICATE CHECK
    # returns df with all the doubles
    df_doubles = df_in[df_in["Inventarnummer"].duplicated(keep=False)]
    if len(df_doubles) != 0:
        # add the columns to document the renaming of inventarnummer
        df_doubles = InvNr.add_rename_inventarnummer(in_data=df_doubles, is_excel=False, return_sorted=True, tranche=None)
        # the exact name of the picture is important as it may differ from the usual schema in order to be unique
        df_doubles.insert(1, "Name Bild", np.nan)
        ExF.save_df_excel(df_doubles, f"{tranche}_{today}_Inventarnummer_Dubletten")
        # Write documentation
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": df_in, "Schlüssel Excel": "-",
             "Feld": "Inventarnummer", "Was": "Dubletten", "Resultat": f"{len(df_doubles)} dubletten",
             "Output Dokument": f"{tranche}_{today}_Inventarnummer_Dubletten", "Ersetzt Hauptexcel": "unterteilt es"})
        # drop all the duplicates from the main df
        df_in.drop_duplicates(subset=["Inventarnummer"], keep=False, inplace=True, ignore_index=True)
    else:
        # Write documentation
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": df_in, "Schlüssel Excel": "-",
             "Feld": "Inventarnummer", "Was": "Dubletten", "Resultat": f"keine dubletten",
             "Output Dokument": f"-", "Ersetzt Hauptexcel": "unterteilt es"})
    #######################################
    # COMPLIANCE CHECK
    # iterate over the items in the column from the second row onwards col_items returns a tuple
    # first element of the tuple is the index the second the value from the column
    # initiate a list to store the rows in, from that list new df will be created
    list_correct = []  # for all the correct inventarnummer
    list_dummy = []  # for the dummy inventarnummer
    list_wrong = []  # for all the rest that do not comply to the other patterns
    for index, row in df_in.iterrows():
        try:
            # check if it is correct
            if pattern_correct.match(row["Inventarnummer"]):
                list_correct.append(row)
            # check for the dummy
            elif pattern_dummy.match(row["Inventarnummer"]):
                list_dummy.append(row)
            # for all those that do not match any pattern
            else:
                list_wrong.append(row)
        # if it is a str or float then the number is wrong therefore it is appended to that list
        except TypeError:
            list_wrong.append(row)
    #################
    # check if any of the dfs have entries and save them
    if len(list_correct) != 0:
        df_correct = pd.DataFrame.from_records(list_correct)
        # save the documentation of the changed Inventarnummer
        df_correct.sort_values(by=["Ordner Bild", "Inventar Sortierbar"], inplace=True, ignore_index=True)
        ExF.save_df_excel(df_correct, f"{tranche}_{today}_Inventarnummer_Korrekt")
        # Write documentation
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": df_in, "Schlüssel Excel": "-",
             "Feld": "Inventarnummer", "Was": "Korrektes Format", "Resultat": f"{len(df_correct)} korrekte",
             "Output Dokument": f"{tranche}_{today}_Inventarnummer_Korrekt", "Ersetzt Hauptexcel": "unterteilt es"})
    else:
        # Write documentation
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": df_in, "Schlüssel Excel": "-",
             "Feld": "Inventarnummer", "Was": "Korrektes Format", "Resultat": f"keine korrekte",
             "Output Dokument": f"-", "Ersetzt Hauptexcel": "unterteilt es"})
    # check if there are any dummy numbers
    if len(list_dummy) != 0:
        df_dummy = pd.DataFrame.from_records(list_dummy)
        # add the columns to document the renaming of inventarnummer
        df_dummy = InvNr.add_rename_inventarnummer(in_data=df_dummy, is_excel=False, return_sorted=True, tranche=None)
        # save the documentation of the changed Inventarnummer
        ExF.save_df_excel(df_dummy, f"{tranche}_{today}_Inventarnummer_Dummy")
        # Write documentation
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": df_in, "Schlüssel Excel": "-",
             "Feld": "Inventarnummer", "Was": "Dummy Nummern", "Resultat": f"{len(df_dummy)} Dummy Nummern",
             "Output Dokument": f"{tranche}_{today}_Inventarnummer_Dummy", "Ersetzt Hauptexcel": "unterteilt es"})
    else:
        # Write documentation
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": df_in, "Schlüssel Excel": "-",
             "Feld": "Inventarnummer", "Was": "Dummy Nummern", "Resultat": f"keine Dummy Nummern",
             "Output Dokument": f"-", "Ersetzt Hauptexcel": "unterteilt es"})
    # check if there are any wrong inventarnummern
    if len(list_wrong) != 0:
        df_wrong = pd.DataFrame.from_records(list_wrong)
        # add the columns to document the renaming of inventarnummer
        df_wrong = InvNr.add_rename_inventarnummer(in_data=df_wrong, is_excel=False, return_sorted=True, tranche=None)
        # save the documentation of the changed Inventarnummer
        df_wrong.sort_values(by=["Ordner Bild", "Inventar Sortierbar"], inplace=True, ignore_index=True)
        ExF.save_df_excel(df_wrong, f"{tranche}_{today}_Inventarnummer_Fehlerhafte")
        # Write documentation
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": df_in, "Schlüssel Excel": "-",
             "Feld": "Inventarnummer", "Was": "Falsche Formate", "Resultat": f"{len(df_wrong)} falsche Formate",
             "Output Dokument": f"{tranche}_{today}_Inventarnummer_Fehlerhafte", "Ersetzt Hauptexcel": "unterteilt es"})
    else:
        # Write documentation
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": df_in, "Schlüssel Excel": "-",
             "Feld": "Inventarnummer", "Was": "Falsche Formate", "Resultat": f"keine falsche Formate",
             "Output Dokument": f"-", "Ersetzt Hauptexcel": "unterteilt es"})
    ExF.doc_save_list(doc_list, abteilung)


# # EXCEL WITH WRONG INVENTARNUMMER
# inventarnummer_compliance(in_data="_Test_Excel/b_Test_inventarnummer_compliance_Fehler", tranche="Test", abteilung="Test")
#
# # EXCEL WITH ONLY CORRECT INVENTARNUMMER
# inventarnummer_compliance(in_data="_Test_Excel/b_Test_inventarnummer_compliance_Korrekt", tranche="Pilot", abteilung="Test")
# inventarnummer_compliance(in_data="Pilot_Komplett_2022-02-16", tranche="Pilot", abteilung="Test")



