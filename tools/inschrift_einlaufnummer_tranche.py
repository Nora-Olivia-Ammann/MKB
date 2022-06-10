import os
from datetime import date

import numpy as np
import pandas as pd

from excel_functions import ExcelFunctions as ExF
from RegEx_patterns import RegExPattern as REPAT
from cleaning_df import CleanDF as Clean

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class Inschrift:

    @staticmethod
    def einlaufnummer_bearbeiten(in_data: str or pd.DataFrame, tranche: str or None = None,
                                 abteilung: str or None = None, is_excel: bool = False) -> None or pd.DataFrame:
        """
        Checks whether all the Einlaufnummer are in the correct format. If leading zeros are missing it fills those.
        If used as nested function it also returns a True if all is correct and the df (if leading zeros were added
        it does not appear as a fault, therefore the input df has to be overwritten), or False and the df with the column
        that marks them as such added.
        :param in_data: excel / df
        :param is_excel: True if excel
        :param tranche: name
        :param abteilung: name
        :return: True if all is correct and new tranche df, False if not correct and new tranche df and faulty df
        """
        if is_excel:
            # read in_excel to df
            df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{in_data}.xlsx"))
            # read the documentation excel
            df_doc = pd.read_excel(
                os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))
        else:
            df_in = in_data
            df_doc = abteilung
        ####################################
        pattern_einlauf_correct, pattern_zero, pattern_incomplete = REPAT.inschrift_re_pattern()
        # get the index number of the column inschrift
        index_no = df_in.columns.get_loc("Inschrift")
        # try to insert a new column to the right of it
        try:
            df_in.insert(index_no + 1, "Inschrift falsch", np.nan)
        # if it already exists then delete all the entries
        except ValueError:
            df_in["Inschrift falsch"] = np.nan
        for index, inschrift in df_in["Inschrift"].iteritems():
            # RegEx only works with strings. Numbers (int and float) are also treated as strings,
            # you only get a type error if it is empty
            try:
                # if the numbers are only zeros, this has to come first, as a 0 number could also match the correct RegEx
                if pattern_zero.match(inschrift):
                    df_in.loc[index, "Inschrift falsch"] = "x"
                # if the numbers are valid
                elif pattern_einlauf_correct.match(inschrift):
                    continue
                elif pattern_incomplete.match(inschrift):
                    # split the string
                    spl_val = inschrift.split("_")
                    # fill the number with zeros until it is four digits
                    spl_val[1] = spl_val[1].zfill(4)
                    # join the split string from the list
                    new_inschrift = "_".join(spl_val)
                    # assign the new value to the cell
                    df_in.loc[index, "Inschrift"] = new_inschrift
                else:
                    df_in.loc[index, "Inschrift falsch"] = "x"
            except TypeError:
                df_in.loc[index, "Inschrift falsch"] = "x"
        # if all are correct then the column is empty
        if df_in["Inschrift falsch"].isnull().all():
            df_in.pop("Inschrift falsch")
            if is_excel:
                ExF.save_df_excel(df_in, f"{tranche}_{today}_Komplett")
                # write documentation
                df_doc = pd.concat([df_doc, pd.DataFrame(
                    {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": "-",
                     "Feld": "Inschrift", "Was": "Compliance",
                     "Resultat": f"alle Angaben korrekt oder wurden korriegiert.",
                     "Output Dokument": f"{tranche}_{today}_Komplett", "Ersetzt Hauptexcel": "ja"},
                    index=[0])], ignore_index=True)
                ExF.save_doc_excel(df_doc, abteilung)
            else:
                return True, df_in
        else:
            if is_excel:
                ExF.save_df_excel(df_in, f"{tranche}_{today}_Komplett")
                # write documentation
                df_doc = pd.concat([df_doc, pd.DataFrame(
                    {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": "-",
                     "Feld": "Inschrift", "Was": "Compliance", "Resultat": f"Inschriften inkorrekt",
                     "Output Dokument": f"{tranche}_{today}_Komplett",
                     "Ersetzt Hauptexcel": "ja"}, index=[0])], ignore_index=True)
                ExF.save_doc_excel(df_doc, abteilung)
            else:
                return False, df_in

    # # everything is correct and all the numbers are there
    # einlaufnummer_bearbeiten(in_data="_Test_Excel/c_Test_einlaufnummer_bearbeiten_Vollständig", is_excel=True,
    #                        tranche="Test", abteilung="Test")

    # # everything is correct but some are missing
    # einlaufnummer_bearbeiten(in_data="_Test_Excel/c_Test_einlaufnummer_bearbeiten_Korrekt", is_excel=True,
    #                          tranche="Test", abteilung="Test")

    # # many different mistakes
    # einlaufnummer_bearbeiten(in_data="_Test_Excel/c_Test_einlaufnummer_bearbeiten_Fehler", is_excel=True,
    #                          tranche="Test", abteilung="Test")

    @staticmethod
    def get_unique_einlauf(in_excel: str, tranche: str) -> None:
        """
        Gets all the Einlaufnummer in column "Inschrift" once in a new excel.
        :param in_excel: excel
        :param tranche: name
        :return: saves excel
        """
        # read in_excel to df
        df_in = pd.read_excel(os.path.join(current_wdir, "input", "", f"{in_excel}.xlsx"))
        # clean the df
        df_in = Clean.strip_spaces(df_in)
        # drop null rows
        df_in.dropna(subset=["Inschrift"], inplace=True)
        # drop duplicates
        df_in.drop_duplicates(subset="Inschrift", keep='first', inplace=True, ignore_index=False)
        # get the column into a new df for saving as the rest of the information is not relevant
        df_out = pd.DataFrame({"Inschrift": df_in["Inschrift"], "TMS Bearbeitet": np.nan})
        df_out.sort_values(by=["Inschrift"], ascending=True, inplace=True, ignore_index=True)
        # save the excel
        ExF.save_df_excel(df_out, f"{tranche}_Einmalige_Einlaufnummern_{today}")

    # get_unique_einlauf("_Test_Tranche_Neu_Formatiert_Kurz", "Test")

    @staticmethod
    def add_unique_einlauf(in_excel: str, key_excel: str, out_tranche: str) -> None:
        df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{in_excel}.xlsx"))
        # clean the df
        df_in = Clean.strip_spaces(df_in)
        # read key_excel in which will provide the dictionary
        df_key = pd.read_excel(os.path.join(current_wdir, "input", f"{key_excel}.xlsx"))
        # clean the df
        df_key = Clean.strip_spaces(df_key)
        # drop null rows
        df_in.dropna(subset=["Inschrift"], inplace=True)
        # reformat the information
        df_temp = pd.DataFrame({"Inschrift": df_in["Inschrift"]})
        # sort the values
        df_temp.sort_values(by=["Inschrift"], ascending=True, inplace=True, ignore_index=True)
        df_combined = pd.concat([df_key, df_temp], ignore_index=True)
        # drop duplicates
        df_combined.drop_duplicates(subset="Inschrift", keep='first', inplace=True, ignore_index=True)
        # save excel
        ExF.save_df_excel(df_combined, f"{out_tranche}_Einmalige_Einlaufnummern_{today}")

    # add_unique_einlauf("_Test_Tranche_Neu_Formatiert_Lang", "c_Test_Einmalige_Einlaufnummern", "Test_lang")

    @staticmethod
    def key_einlauf_completion_check(key_data: pd.DataFrame or str, is_excel: bool = False):
        """
        Checks whether all the mandatory information in the Excel from the TMS export is there. If used as a nested function
        it returns True if all is correct.
        :param key_data: excel TMS / df
        :param is_excel: True if it is excel
        :return: True if all is good, False if values are missing and df with rows that miss values.
        """
        if is_excel:
            # read in_excel to df, which is the one to fill with values
            df_key = pd.read_excel(os.path.join(current_wdir, "input", "", f"{key_data}.xlsx"))
        else:
            df_key = key_data
        # none of these should be empty
        if df_key[["Erwerbungsart", "Objektstatus"]].isnull().any().any():
            df_nan = df_key[df_key["Erwerbungsart"].isnull()]
            df_nan = pd.concat([df_nan, df_key[df_key["Objektstatus"].isnull()]], ignore_index=True)
            # sort out the duplicates and keep the first instance
            df_nan.drop_duplicates(subset="Inventarnummer", keep='first', inplace=True, ignore_index=False)
            df_nan.sort_values(by=["Inventarnummer"], ascending=True, inplace=True, ignore_index=True)
            if is_excel:
                # save the df
                ExF.save_df_excel(df_nan, f"Schlüssel_Einlauf_Fehlende_Angaben_{today}")
            else:
                return False, df_nan
        else:
            if is_excel:
                print("Einlaufschlüssel Korrekt.")
            else:
                return True, None

    # key_einlauf_completion_check(key_data="_Test_Excel/c_key_einlauf_completion_check_Korrekt", is_excel=True)
    # key_einlauf_completion_check(key_data="_Test_Excel/c_key_einlauf_completion_check_Fehler", is_excel=True)


if __name__ == "__main__":
    pass
