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
    def einlaufnummer_bearbeiten(input_df: pd.DataFrame, tranche: str, in_excel_name: str) -> None or pd.DataFrame:
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
        pattern_einlauf_correct, pattern_zero, pattern_incomplete = REPAT.inschrift_re_pattern()
        # get the index number of the column inschrift
        index_no = input_df.columns.get_loc("Inschrift")
        # try to insert a new column to the right of it
        try:
            input_df.insert(index_no + 1, "Inschrift falsch", np.nan)
        # if it already exists then delete all the entries
        except ValueError:
            input_df["Inschrift falsch"] = np.nan
        for index, inschrift in input_df["Inschrift"].iteritems():
            # RegEx only works with strings. Numbers (int and float) are also treated as strings,
            # you only get a type error if it is empty
            try:
                # if the numbers are only zeros, this has to come first, as a 0 number could also match the correct RegEx
                if pattern_zero.match(inschrift):
                    input_df.loc[index, "Inschrift falsch"] = "x"
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
                    input_df.loc[index, "Inschrift"] = new_inschrift
                else:
                    input_df.loc[index, "Inschrift falsch"] = "x"
            except TypeError:
                input_df.loc[index, "Inschrift falsch"] = "x"
        # if all are correct then the column is empty
        if input_df["Inschrift falsch"].isnull().all():
            input_df.pop("Inschrift falsch")
            doc_dict = {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel_name, "Schlüssel Excel": "-",
                     "Feld": "Inschrift", "Was": "Compliance",
                     "Resultat": f"alle Angaben korrekt oder wurden korriegiert.",
                     "Output Dokument": f"{tranche}_{today}_Komplett", "Ersetzt Hauptexcel": "ja"}
            return True, input_df, doc_dict
        doc_dict = {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel_name, "Schlüssel Excel": "-",
             "Feld": "Inschrift", "Was": "Compliance", "Resultat": f"Inschriften inkorrekt",
             "Output Dokument": f"{tranche}_{today}_Komplett",
             "Ersetzt Hauptexcel": "ja"}
        return False, input_df, doc_dict

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
    def key_einlauf_completion_check(input_key_df: pd.DataFrame):
        """
        Checks whether all the mandatory information in the Excel from the TMS export is there. If used as a nested function
        it returns True if all is correct.
        :param input_key_df: df from excel TMS
        :return: True if all is good, False if values are missing and df with rows that miss values.
        """
        # none of these should be empty
        if input_key_df[["Erwerbungsart", "Objektstatus"]].isnull().any().any():
            df_nan = input_key_df[input_key_df["Erwerbungsart"].isnull()]
            df_nan = pd.concat([df_nan, input_key_df[input_key_df["Objektstatus"].isnull()]], ignore_index=True)
            # sort out the duplicates and keep the first instance
            df_nan.drop_duplicates(subset="Inventarnummer", keep='first', inplace=True, ignore_index=False)
            df_nan.sort_values(by=["Inventarnummer"], ascending=True, inplace=True, ignore_index=True)
            return False, df_nan
        else:
            return True, None

    # key_einlauf_completion_check(key_data="_Test_Excel/c_key_einlauf_completion_check_Korrekt", is_excel=True)
    # key_einlauf_completion_check(key_data="_Test_Excel/c_key_einlauf_completion_check_Fehler", is_excel=True)


if __name__ == "__main__":
    pass
