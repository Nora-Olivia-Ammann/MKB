import os
import warnings

import pandas as pd
import numpy as np
from datetime import date
import re

from excel_functions import ExcelFunctions as ExF
from RegEx_patterns import RegExPattern as RePat
from cleaning_df import CleanDF as Clean
from custom_exceptions import *

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class Inventarnummer:

    @staticmethod
    def inventar_sortierbar(input_df: pd.DataFrame or str, in_excel_name: str, return_sorted: bool,
                            tranche: str or None = None) -> pd.DataFrame or None:
        """
        Adds a new column with a sortable Inventarnummer. The correct one which we use in the TMS has no leading zeros,
        and cannot be sorted by excel or df correctly so that 2 follows 1 instead of 10. Because there may still be
        faulty Inventarnummer, of a format we may not be able to anticipate, we only add the zeros to ones that are
        roughly in the correct format. Once Inventarnummern have been corrected this program can be run again.
        :param in_data: excel or df
        :param is_excel: if it is an excel: True
        :param tranche: name
        :param return_sorted: if it should return sorted according to the inventarnummer: True
        :return: df or None
        """
        # clean the df
        input_df = Clean.strip_spaces_whole_df(input_df)
        # overwrite the existing column with the new Inventarnummer
        input_df["Inventar Sortierbar"] = input_df["Inventarnummer"]
        # we only want to format roughly correct inventarnummer, as the true compliance check comes later
        # for the incorrect ones there is too much variation in the others to take them all into account,
        # therefore we will ignore those that do not fit
        pattern_no_letter, pattern_letter, pattern_letter_blank = RePat.inventar_sortierbar_re_pattern()
        for index, value in input_df["Inventar Sortierbar"].iteritems():
            # exclude NaN cells
            # since it is very uncommon to have a missing Inventarnummer this is faster than checking if it is present
            try:
                # check if it is correct
                if pattern_no_letter.match(value) or pattern_letter_blank.match(value):
                    spl_val = value.split(" ")
                    spl_val[1] = spl_val[1].zfill(6)
                    joined = " ".join(spl_val)
                    input_df.loc[index, "Inventar Sortierbar"] = joined
                elif pattern_letter.match(value):
                    spl_val = value.split(" ")
                    spl_val[1] = spl_val[1].zfill(7)
                    joined = " ".join(spl_val)
                    input_df.loc[index, "Inventar Sortierbar"] = joined
            # skip the row if it is NaN
            except ValueError:
                continue
            except TypeError:
                continue
        # Sort the values if wished
        if return_sorted:
            input_df.sort_values(by=["Ordner Bild", "Inventar Sortierbar"], inplace=True, ignore_index=True)
        doc_dict = {"Datum": today,
                    "Tranche": tranche,
                    "Input Dokument": in_excel_name,
                    "Schlüssel Excel": "-",
                    "Feld": "Inventar Sortierbar",
                    "Was": "Hinzufügen des Feldes",
                    "Resultat": f"-",
                    "Output Dokument": f"-",
                    "Ersetzt Hauptexcel": "-"}
        return input_df, doc_dict

    # inventar_sortierbar(indata="a_Test_inventar_sortierbar", is_excel=True, tranche="Test", return_sorted=False)

    @staticmethod
    def add_rename_inventarnummer(input_df: pd.DataFrame, return_sorted: bool, tranche: str, in_excel_name: str) \
            -> pd.DataFrame or None:
        """
        Adds columns to df, that are used when having to rename any Inventarnummer. Can be used as a nested function.
        :param in_data: df / excel
        :param is_excel: True if Excel
        :param return_sorted: True if it should be sorted according to Inventar Sortierbar
        :param tranche: name
        :return: df / None
        """
        # TODO: exception handling
        if "Alt Inventarnummer" in input_df.columns:
            raise ColExistsError("The Column already exists.")
        # rename the column with the old inventarnummer
        input_df.rename(columns={"Inventarnummer": "Alt Inventarnummer"}, inplace=True)
        # add a new column to store the new Inventarnummer in
        input_df.insert(0, "Inventarnummer", np.nan)
        # add a new column to mark whether the Bilddatei was also renamed
        if return_sorted:
            input_df.sort_values(by=["Inventar Sortierbar"], inplace=True, ignore_index=True)
        doc_dict = {"Datum": today,
                    "Tranche": tranche,
                    "Input Dokument": in_excel_name,
                    "Schlüssel Excel": "-",
                    "Feld": "Inventarnummer",
                    "Was": "Hinzufügen von Spalte: Alt Inventarnummer",
                    "Resultat": f"-",
                    "Output Dokument": f"-",
                    "Ersetzt Hauptexcel": "-"}
        return input_df, doc_dict

    # add_rename_inventarnummer(in_data="a_Test_rename_inventarnummer", is_excel=True, return_sorted=False,
    # tranche="Test")



if __name__ == "__main__":
    pass
