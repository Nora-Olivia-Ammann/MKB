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
from double_check import DoubleCheck as Double

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class Inventarnummer:

    @staticmethod
    def add_inventar_sortierbar(input_df: pd.DataFrame, return_sorted: bool, tranche: str, in_excel_name: str) \
            -> pd.DataFrame and dict:
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
                    "Tranche": tranche,
                    "Input Dokument": in_excel_name,
                    "Schlüssel Excel": "-",
                    "Feld": "Inventar Sortierbar",
                    "Was": "Hinzufügen des Feldes",
                    "Resultat": f"",
                    "Output Dokument": np.nan,
                    "Ersetzt Hauptexcel": "ja"}
        return input_df, doc_dict

    @staticmethod
    def add_inventarnummer_alt(input_df: pd.DataFrame, return_sorted: bool, tranche: str, in_excel_name: str) \
            -> pd.DataFrame and dict:
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
                # if it doesn't exist we add the column
                new_df, _ = Inventarnummer.add_inventar_sortierbar(input_df, True, tranche, in_excel_name)
        # if we added the new column we write a different doc and return the other df
        # as the variable only exists if the KeyError happened we check if it does
        # it is easier if we write both info in one doc as we must otherwise return a list or several which makes it
        # more complicated later on
        if "new_df" in locals():
            # write documentation
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "-",
                        "Feld": "Inventarnummer, Inventarnummer Sortierbar",
                        "Was": "Hinzufügen von Spalten",
                        "Resultat": f"Neue Spalten",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "ja"}
            return new_df, doc_dict
        # if the variable does not exist we continue as normal
        else:
            # write documentation
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "-",
                        "Feld": "Inventarnummer",
                        "Was": "Hinzufügen von Spalte: Alt Inventarnummer",
                        "Resultat": f"Neue Spalte",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "ja"}
            return input_df, doc_dict

    @staticmethod
    def remove_leading_zero(inventarnummer: str) -> str:
        # TODO: validate, write description
        # split the Inventarnummer at the blank space
        splt_inventar = inventarnummer.split(" ")
        # strip the 0 on the left side from the number and replace the old value with that
        splt_inventar[1] = splt_inventar[1].lstrip("0")
        # join the strings from the list
        joined = " ".join(splt_inventar)
        return joined

    @staticmethod
    def separate_leading_zero(input_df: pd.DataFrame, tranche: str, in_excel_name: str, regex_function) \
            -> bool and pd.DataFrame and pd.DataFrame or None and dict:
        # clean the df
        input_df = Clean.strip_spaces_col(input_df, "Inventarnummer")
        # get the RegEx pattern for leading zero
        _, pattern_leading_zero, _ = regex_function
        list_leading_zero = []
        # remove the leading zeros from Inventarnummer
        for index, value in input_df["Inventarnummer"].iteritems():
            # RegEx only takes str if it is an int or float it will throw an error
            try:
                # check for Inventarnummer with leading zero
                if pattern_leading_zero.match(value):
                    # get the new value
                    new_invnr = Inventarnummer.remove_leading_zero(value)
                    # replace the value in the in_df
                    input_df.loc[index, "Inventarnummer"] = new_invnr
                    # add the new number to the documentation df
                    list_leading_zero.append(
                        {"Alte Inventarnummer": value,
                         "Neue Inventarnummer": new_invnr,
                         "Tranche": input_df.loc[index, "Tranche"],
                         "Ordner Bild": input_df.loc[index, "Ordner Bild"],
                         "Unique_ID": input_df.loc[index, "Unique_ID"],
                         "Inventar Sortierbar": input_df.loc[index, "Inventar Sortierbar"],
                         "Bilddatei kontrolliert": np.nan})
            except TypeError:
                continue
        if len(list_leading_zero) != 0:
            df_leading_zero = pd.DataFrame.from_records(list_leading_zero)
            # save the excel that contains the information of the changed inventarnummer
            df_leading_zero.sort_values(by=["Ordner Bild", "Inventar Sortierbar"], inplace=True, ignore_index=True)
            # write documentation
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "-",
                        "Feld": "Inventarnummer",
                        "Was": "Führende 0",
                        "Resultat": f"{len(df_leading_zero)} Inventarnummern wurden geändert und zusatz excel erstellt",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "ja"}
            return True, input_df, df_leading_zero, doc_dict
        else:
            # write documentation
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "-",
                        "Feld": "Inventarnummer",
                        "Was": "Führende 0",
                        "Resultat": f"Keine Inventarnummern haben führende 0.",
                        "Output Dokument": "-",
                        "Ersetzt Hauptexcel": "nein"}
            return False, None, None, doc_dict

    @staticmethod
    def add_x_leading_zero(input_df: pd.DataFrame, tranche: str, in_excel_name: str, regex_function) \
            -> bool and pd.DataFrame or None and dict:
        # TODO validate, write description
        # clean the column
        input_df = Clean.strip_spaces_col(input_df, "Inventarnummer")
        # get the RegEx pattern for leading zero
        _, pattern_leading_zero, _ = regex_function
        # get the index of the Inventarnummer Column
        index = input_df.columns.get_loc("Inventarnummer")
        # insert a column next to the inventarnummer to mark with an x
        try:
            input_df.insert(index + 1, "Führende 0", np.nan)
        # if the column exists we get a value error, in that case we simply overwrite the results as it may have changed
        except ValueError:
            input_df["Führende 0"] = np.nan
        try:
            input_df = Inventarnummer.add_inventarnummer_alt(input_df=input_df, in_excel_name=in_excel_name,
                                                             tranche=tranche, return_sorted=False)
        # if the column exists we do not want to overwrite it as it may contain important data
        except ColExistsError:
            pass
        # iterate over the df
        for index, value in input_df["Inventarnummer"].iteritems():
            # RegEx only takes str if it is an int or float it will throw an error
            try:
                # check for Inventarnummer with leading zero
                if pattern_leading_zero.match(value):
                    # get the new value
                    new_invnr = Inventarnummer.remove_leading_zero(value)
                    # replace the value in the in_df
                    input_df.loc[index, "Inventarnummer"] = new_invnr
                    input_df.loc[index, "Führende 0"] = "x"
            # if it is nan it raises a type error
            except TypeError:
                continue
        # check if all the columns are NaN meaning there are no leading zeros
        if input_df["Führende 0"].isnull().all():
            # remove the column
            input_df.pop("Führende 0")
            # write the documentaiton
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "-",
                        "Feld": "Inventarnummer",
                        "Was": "Führende 0",
                        "Resultat": f"Keine Inventarnummern mit führenden 0",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "nein"}
            return False, None, doc_dict
        else:
            # write the documentaiton
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "-",
                        "Feld": "Inventarnummer, Führende 0",
                        "Was": "Führende 0",
                        "Resultat": f"Führende 0 gefunden und markiert.",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "ja"}
            return True, input_df, doc_dict

    @staticmethod
    def add_x_wrong_inventarnummer(input_df: pd.DataFrame, tranche: str, in_excel_name: str, regex_function) \
            -> bool and pd.DataFrame and pd.DataFrame or None and list[dict]:
        # TODO: validate add description
        # clean the column
        input_df = Clean.strip_spaces_col(input_df, "Inventarnummer")
        # get the RegEx pattern
        pattern_correct, _, _ = regex_function
        # add or overwrite the column (maybe error handling?) that marks the Inventarnummer where something is wrong
        try:
            input_df = Inventarnummer.add_inventarnummer_alt(input_df=input_df, in_excel_name=in_excel_name,
                                                             tranche=tranche, return_sorted=False)
        # if the column exists we do not want to overwrite it as it may contain important data
        except ColExistsError:
            pass
        # get the index of the Inventarnummer Column
        index = input_df.columns.get_loc("Inventarnummer")
        # add a new column to store the new Inventarnummer
        try:
            input_df.insert(index + 1, "Inventarnummer Falsch", np.nan)
        # if the column exists we get a value error, in that case we simply overwrite the results as it may have changed
        except ValueError:
            input_df["Inventarnummer Falsch"] = np.nan
        # check if the Inventarnummer matches
        for index, value in input_df["Inventarnummer"].iteritems():
            try:
                # check for Inventarnummer that are not the correct pattern
                if not pattern_correct.match(value):
                    input_df.loc[index, "Inventarnummer Falsch"] = "x"
            # if it is nan it raises a type error we want to mark it too as this is problematic too
            except TypeError:
                input_df.loc[index, "Inventarnummer Falsch"] = "x"
        # check if all the columns are NaN meaning there are no leading zeros
        if input_df["Inventarnummer Falsch"].isnull().all():
            # remove the column
            input_df.pop("Inventarnummer Falsch")
            # write the documentation
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "-",
                        "Feld": "Inventarnummer",
                        "Was": "Inventarnummer Falsch",
                        "Resultat": f"Alle Inventarnummern sind korrekt.",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "nein"}
            return False, None, doc_dict
        else:
            # write the documentation
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "-",
                        "Feld": "Inventarnummer Falsch",
                        "Was": "Inventarnummer Falsch",
                        "Resultat": f"Falsche Inventarnummern markiert.",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "ja"}
            return True, input_df, doc_dict


if __name__ == "__main__":
    pass
