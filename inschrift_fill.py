import os
import pandas as pd
from datetime import date

import warnings
from tools.custom_exceptions import *
from tools.inschrift_tranche import Inschrift as INSCH
from tools.key_excel import KeyExcel as KE
from tools.excel_functions import ExcelFunctions as ExF

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


def einlauf_fill(in_excel: str, key_excel: str, tranche: str, abteilung: str, continue_if_nan: bool = False) -> None:
    """
    Some of the Metadata for each object is based on its Einlauf. This function adds that data based on the Einlauf
    Key Excel which is an export excel from TMS. If that Excel is incomplete or keys are missing the function will not
    continue. Otherwise the Information will be added.
    :param in_excel: tranchen excel
    :param key_excel: TMS export excel
    :param continue_if_nan: True if the information should be filled even if some Inschrift are missing in the tranche
    :param tranche: name
    :param abteilung: name
    :return: saves excel
    """
    # read in_excel to df, which is the one to fill with values
    df_in = pd.read_excel(os.path.join(current_wdir, "input", "", f"{in_excel}.xlsx"))
    # read key_excel in which will provide the dictionary
    df_key = pd.read_excel(os.path.join(current_wdir, "input", "", f"{key_excel}.xlsx"))
    # read the documentation excel
    df_doc = pd.read_excel(
        os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))
    # check that all rows have an einlaufnummer
    if df_in["Inschrift"].isnull().any():
        # if not return a document that contains the null rows
        df_nan = df_in[df_in["Inschrift"].isnull()]
        ExF.save_df_excel(df_nan, f"{tranche}_{today}_Fehlende_Einlaufnummern")
        if not continue_if_nan:
            # write documentation
            df_doc = pd.concat([df_doc, pd.DataFrame(
                {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": key_excel,
                 "Feld": "Erwerbungsart, Objektstatus",
                 "Was": f"Ergänzen gemäss Inschrift, continue_if_nan: {continue_if_nan}",
                 "Resultat": f"{len(df_nan)} Zeilen fehlten die Inschrift, Programm abgebrochen",
                 "Output Dokument": f"{tranche}_{today}_Fehlende_Einlaufnummern", "Ersetzt Hauptexcel": "zusatz"},
                index=[0])], ignore_index=True)
            ExF.save_doc_excel(df_doc, abteilung)
            # error stop the function
            raise TrancheMissingValue("Not all row contain an Inschrift.")
        else:
            # write documentation
            df_doc = pd.concat([df_doc, pd.DataFrame(
                {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": key_excel,
                 "Feld": "Erwerbungsart, Objektstatus",
                 "Was": f"Ergänzen gemäss Inschrift, continue_if_nan: {continue_if_nan}",
                 "Resultat": f"{len(df_nan)} Zeilen fehlten die Inschrift",
                 "Output Dokument": f"{tranche}_{today}_Fehlende_Einlaufnummern",
                 "Ersetzt Hauptexcel": "unterteilt es"}, index=[0])], ignore_index=True)
            df_in.dropna(subset=["Inschrift"], inplace=True)
            # if we do not reset the index, then we get an index error later, as the number
            # is greater than the size of the df
            df_in.reset_index(inplace=True)
            df_in.pop("index")  # when resetting the index it is saved as a new column
            warnings.warn("Some Inschrift are missing, NaN document saved, function continued with non NaN df.")
    # check that the df key is completely filled:
    outcome_key, df_nan = INSCH.key_einlauf_completion_check(key_data=df_key, is_excel=False)
    if not outcome_key:
        ExF.save_df_excel(df_nan, f"Schlüssel_Einlauf_Fehlende_Angaben_{today}")
        # Write documentation
        df_doc = pd.concat([df_doc, pd.DataFrame(
            {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": key_excel,
             "Feld": f"Inschrift", "Was": f"Vollständigkeit im Schlüssel Excel",
             "Resultat": f"{len(df_nan)} fehlende Angaben im Schlüssel",
             "Output Dokument": f"Schlüssel_Einlauf_Fehlende_Angaben_{today}", "Ersetzt Hauptexcel": "-"},
            index=[0])], ignore_index=True)
        ExF.save_doc_excel(df_doc, abteilung)
        # error stop the function
        raise KeyDocIncomplete("The Einlauf Key document is incomplete")
    # check whether all keys are present, in the key file, the Inschrift column is called Inventarnummer as it is a
    # TMS export, where the Einläufe are registered as a virtual object
    # we do not drop the uncontrolled as it does not exist in this file
    result_check, df_not_dict = KE.check_key_isin(in_data=df_in, in_col="Inschrift", key_data=df_key,
                                               key_col="Inventarnummer", drop_uncontrolled=False, out_excel=None,
                                               is_excel=False, tranche=None, abteilung=df_doc)
    if not result_check:
        # drop the duplicates, we only need one example
        df_not_dict.drop_duplicates(subset=["Inschrift"], keep="first", inplace=True, ignore_index=True)
        # sort the values for easier reading
        df_not_dict.sort_values(by=["Inschrift"], ascending=True, inplace=True, na_position='last', ignore_index=True)
        # save the excel
        ExF.save_df_excel(df_not_dict, f"Schlüssel_Fehlende_Inschrift_{tranche}_{today}")
        # write documentation
        df_doc = pd.concat([df_doc, pd.DataFrame(
            {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": key_excel,
             "Feld": f"Inschrift", "Was": f"Vollständigkeit im Schlüssel Excel, continue_if_nan: {continue_if_nan}",
             "Resultat": f"{len(df_not_dict)} fehlende Schlüssel",
             "Output Dokument": f"Schlüssel_Fehlende_Inschrift_{tranche}_{today}", "Ersetzt Hauptexcel": "-"},
            index=[0])], ignore_index=True)
        ExF.save_doc_excel(df_doc, abteilung)
        # raise Error
        raise MissingKey("Inschrift are missing in the key document.")
    df_key.dropna(subset=["Kontrolliert"], inplace=True)
    # fill the Erwerbungsart and Objektstatus if everything is ok
    dict_erwerb = dict(zip(df_key.Inventarnummer, df_key.Erwerbungsart))
    df_in["Erwerbungsart"] = df_in["Inschrift"].map(dict_erwerb)
    dict_objekt = dict(zip(df_key.Inventarnummer, df_key.Objektstatus))
    df_in["Objektstatus"] = df_in["Inschrift"].map(dict_objekt)
    # save the filled df to a new excel
    ExF.save_df_excel(df_in, f"{tranche}_{today}")
    # write documentation
    df_doc = pd.concat([df_doc, pd.DataFrame(
        {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": key_excel,
         "Feld": "Erwerbungsart, Objektstatus", "Was": f"Ergänzen gemäss Inschrift, continue_if_nan: {continue_if_nan}",
         "Resultat": f"Excel ergänzt", "Output Dokument": f"{tranche}_{today}", "Ersetzt Hauptexcel": "ja"},
        index=[0])], ignore_index=True)
    ExF.save_doc_excel(df_doc, abteilung)


# # EVERYTHING IS CORRECT
# einlauf_fill(in_excel="c_Test_einlauf_fill_Tranche_Korrekt", key_excel="c_key_einlauf_completion_check_Korrekt",
#              continue_if_nan=False, tranche="Test", abteilung="Test")
#
#
# # TRANCHE CONTAINS NAN
# # because continue_if_nan is False, the function will stop
# einlauf_fill(in_excel="c_Test_einlauf_fill_Tranche_Korr_NaN", key_excel="c_key_einlauf_completion_check_Korrekt",
#              continue_if_nan=False, tranche="Test", abteilung="Test")
#
#
# # continue_if_nan is True therefore the function will not stop, splits the excel and raises a warning
# einlauf_fill(in_excel="c_Test_einlauf_fill_Tranche_Korr_NaN", key_excel="c_key_einlauf_completion_check_Korrekt",
#              continue_if_nan=True, tranche="Test", abteilung="Test")
#
#
# # TRANCHE EXCEL HAS OTHER KEYS
# # saves an excel with the missing keys and stops the function by raising MissingKey Exception
# einlauf_fill(in_excel="_Test_Tranche_Neu_Formatiert_Kurz", key_excel="c_key_einlauf_completion_check_Korrekt",
#              continue_if_nan=True, tranche="Test", abteilung="Test")
#
#
# # KEY EXCEL IS MISSING INFORMATION
# # saves an excel with the rows that are missing information, stops the function by raising KeyDocIncomplete Error
# einlauf_fill(in_excel="c_Test_einlauf_fill_Tranche_Korrekt", key_excel="c_key_einlauf_completion_check_Fehler",
#              continue_if_nan=True, tranche="Test", abteilung="Test")

