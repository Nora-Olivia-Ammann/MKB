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
    def add_inventar_sortierbar(input_df: pd.DataFrame, return_sorted: bool) -> pd.DataFrame and dict:
        """
        Adds a new column with a sortable Inventarnummer. The correct one which we use in the TMS has no leading zeros,
        and cannot be sorted by excel or df correctly so that 2 follows 1 instead of 10. Because there may still be
        faulty Inventarnummer, of a format we may not be able to anticipate, we only add the zeros to ones that are
        roughly in the correct format. Once Inventarnummern have been corrected this program can be run again.
        """
        # TODO: validate
        # clean the df
        input_df = Clean.strip_spaces_col(input_df, "Inventarnummer")
        # if it exists we want to overwrite the existing column with the new Inventarnummer
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
                else:
                    continue
            # skip the row if it is NaN
            except ValueError:
                continue
            except TypeError:
                continue
        # Sort the values if wished
        if return_sorted:
            input_df.sort_values(by=["Ordner Bild", "Inventar Sortierbar"], inplace=True, ignore_index=True)
        doc_dict = {"Datum": today,
                    "Tranche": "",
                    "Input Dokument": "",
                    "Schlüssel Excel": "-",
                    "Feld": "Inventar Sortierbar",
                    "Was": "Hinzufügen des Feldes",
                    "Resultat": f"",
                    "Output Dokument": f"",
                    "Ersetzt Hauptexcel": "ja"}
        return input_df, doc_dict

    @staticmethod
    def add_rename_inventarnummer(input_df: pd.DataFrame, return_sorted: bool) -> pd.DataFrame and dict:
        """
        Adds columns to df, that are used when having to rename any Inventarnummer. Can be used as a nested function.
        """
        # TODO: validate, description
        if "Alt Inventarnummer" in input_df.columns:
            raise ColExistsError("The Column already exists.")
        # get the index of the Inventarnummer Column
        index = input_df.columns.get_loc("Inventarnummer")
        # add a new column to store the new Inventarnummer
        input_df.insert(index + 1, "Inventarnummer Alt", np.nan)
        # add a new column to mark whether the Bilddatei was also renamed
        if return_sorted:
            # if the column does not exist we would get an error
            try:
                input_df.sort_values(by=["Inventar Sortierbar"], inplace=True, ignore_index=True)
            except KeyError:
                pass
        # write documentation
        doc_dict = {"Datum": today,
                    "Tranche": "",
                    "Input Dokument": "",
                    "Schlüssel Excel": "-",
                    "Feld": "Inventarnummer",
                    "Was": "Hinzufügen von Spalte: Alt Inventarnummer",
                    "Resultat": f"Neue spalte für ",
                    "Output Dokument": f"-",
                    "Ersetzt Hauptexcel": "ja"}
        return input_df, doc_dict

    # TODO: make regex format_inventarnummer


if __name__ == "__main__":
    pass
