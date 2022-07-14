import os
from datetime import date

import numpy as np
import pandas as pd

from mkb_code.tools.RegEx_patterns import RegExPattern as RePat
from mkb_code.tools.cleaning_df import CleanDF as Clean
from mkb_code.tools.custom_exceptions import *

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class Inventarnummer:

    @staticmethod
    def add_inventar_sortierbar(input_df: pd.DataFrame, tranche: str, in_excel_name: str, return_sorted: bool = False) \
            -> pd.DataFrame and dict:
        """
        Adds a new column with a sortable Inventarnummer. The correct one which we use in the TMS has no leading zeros,
        and cannot be sorted by excel or df correctly so that 2 follows 1 instead of 10. Because there may still be
        faulty Inventarnummer, of a format we may not be able to anticipate, we only add the zeros to ones that are
        roughly in the correct format. Once Inventarnummern have been corrected this program can be run again.
        Test Excel: Test_inventarnummer_compliance_Fehler
        :param input_df: df that gets Inventarnummer sortierbar
        :param tranche: Name of Tranche
        :param in_excel_name: Str name of excel
        :param return_sorted: True if yes, default False
        :return: altered df and dictionary with documentation
        """
        # clean the df
        input_df = Clean.strip_spaces(input_df)
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
    def add_inventarnummer_alt(input_df: pd.DataFrame, tranche: str, in_excel_name: str) \
            -> pd.DataFrame and dict:
        """
        Adds columns to df, that are used when having to rename any Inventarnummer. Can be used as a nested function.
        :param input_df: df that should be transformed
        :param tranche: str of tranche
        :param in_excel_name: name of excel
        :return: df with added column, dict with documentation
        """
        if "Inventarnummer Alt" in input_df.columns:
            raise ColumnExistsError("The Column already exists.")
        # get the index of the Inventarnummer Column
        index = input_df.columns.get_loc("Inventarnummer")
        # add a new column to store the new Inventarnummer
        input_df.insert(index + 1, "Inventarnummer Alt", np.nan)
        # write documentation
        doc_dict = {"Datum": today,
                    "Tranche": tranche,
                    "Input Dokument": in_excel_name,
                    "Schlüssel Excel": "-",
                    "Feld": "Inventarnummer",
                    "Was": "Hinzufügen von Spalte: Inventarnummer Alt",
                    "Resultat": f"Neue Spalte",
                    "Output Dokument": np.nan,
                    "Ersetzt Hauptexcel": "ja"}
        return input_df, doc_dict

    @staticmethod
    def remove_leading_zero(inventarnummer: str) -> str:
        """
        It takes a string which is an inventarnummer of the format with leading zeroes, removes those and returns
        the Inventarnummer in the correct format. This does not have error handling for NaN or Inventarnummer that do
        not match the pattern as it should only be applied when the RegEx is done, therefore eliminating that
        possibility.
        :param inventarnummer: string of an Inventarnummer, eg. (F)Vb 000008
        :return: string of correct Inventarnummer, eg. (F)Vb 8
        """
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
        """
        Generates a separate df with the Inventarnummern from which leading zeros (eg. (F)Vb 00001) were removed from
        the main df. The input df still has the numbers without the leading zeros (eg. (F)Vb 1), the separate df
        is for documentary purposes and so that the picture filenames can be checked.
        Test Excel: Test_inventarnummer_compliance_Fehler
        Test Excel: Test_inventarnummer_compliance_Korrekt
        :param input_df: df with zeros
        :param tranche: Name of tranche
        :param in_excel_name: name of excel
        :param regex_function: name of the RegEx function (the whole function has to be imported)
        :return: bool (True if leading zeros were present), df without the leading zeros, df lists of leading zeros,
            documentation dict
            if there were no leading zeros then no dfs will be returns just the documentation
        """
        # clean the df
        input_df = Clean.strip_spaces(input_df)
        # get the RegEx pattern for leading zero
        _, pattern_leading_zero, _ = regex_function
        list_leading_zero = []
        # remove the leading zeros from Inventarnummer
        for index, invnr in input_df["Inventarnummer"].iteritems():
            # RegEx only takes str if it is an int or float it will throw an error
            try:
                # check for Inventarnummer with leading zero
                if pattern_leading_zero.match(invnr):
                    # get the new invnr
                    new_invnr = Inventarnummer.remove_leading_zero(invnr)
                    # replace the invnr in the in_df
                    input_df.loc[index, "Inventarnummer"] = new_invnr
                    # add the new number to the documentation df
                    list_leading_zero.append(
                        {"Bilddatei kontrolliert": np.nan,
                         "Alte Inventarnummer": invnr,
                         "Neue Inventarnummer": new_invnr,
                         "Tranche": input_df.loc[index, "Tranche"],
                         "Ordner Bild": input_df.loc[index, "Ordner Bild"],
                         "Unique_ID": input_df.loc[index, "Unique_ID"],
                         "Inventar Sortierbar": input_df.loc[index, "Inventar Sortierbar"]})
            # in case of np.nan
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
        """
        Checks for Inventarnummer with leading zero (eg. (F)Vb 0001), they have to have the general correct pattern, so
        if something else is wrong like a space after the (F) then it won't be recognised. It then adds a column to mark
        those with an x, removes the leading zeroes and replaces it in the column, then saves the old number in the
        column with the Inventarnummer alt. It overwrites the 'x' in the leading zero column as we only want the new
        ones.
        Test Excel: Test_inventarnummer_compliance_Fehler
        Test Excel: Test_Inventarnummer_add_x_already_some -> error handling test and adding new
        :param input_df:
        :param tranche:
        :param in_excel_name:
        :param regex_function:
        :return:
        """
        # clean the column
        input_df = Clean.strip_spaces(input_df)
        # get the RegEx pattern for leading zero
        _, pattern_leading_zero, _ = regex_function
        # get the index of the Inventarnummer Column
        index = input_df.columns.get_loc("Inventarnummer")
        # insert a column next to the inventarnummer to mark with an x
        try:
            input_df.insert(index + 1, "Führende 0", np.nan)
        # if the column exists we get a value error, in that case we simply overwrite the results as it may have changed
        # and we only want to have those marked who are new
        except ValueError:
            input_df["Führende 0"] = np.nan
        # add a column to document the old inventarnummer
        try:
            input_df, _ = Inventarnummer.add_inventarnummer_alt(
                input_df=input_df, in_excel_name=in_excel_name, tranche=tranche)
        # if the column exists we do not want to overwrite it as it may contain important data
        except ColumnExistsError:
            pass
        # iterate over the df
        for index, invnr in input_df["Inventarnummer"].iteritems():
            # RegEx only takes str if it is an int or float it will throw an error
            try:
                # check for Inventarnummer with leading zero
                if pattern_leading_zero.match(invnr):
                    # get the new invnr
                    new_invnr = Inventarnummer.remove_leading_zero(invnr)
                    # replace the invnr in the in_df
                    input_df.loc[index, "Inventarnummer"] = new_invnr
                    input_df.loc[index, "Inventarnummer Alt"] = invnr
                    input_df.loc[index, "Führende 0"] = "x"
            # if it is nan it raises a type error
            except TypeError:
                pass
        # check if all the columns are NaN meaning there are no leading zeros
        if input_df["Führende 0"].isnull().all():
            # remove the column
            input_df.pop("Führende 0")
            # write the documentation
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
            # write the documentation
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
        """
        It checks if the Inventarnummer is of the correct format. Inventarnummer with leading zeros are also marked
        therefore if both are used then this one should come after as otherwise they are marked in both columns.
        If columns Inventarnummer Alt and Falsch do not exist it adds those. If Inventarnummer Falsch exists then
        it overwrites the values as we only want new ones.
        Test Excel: Test_inventarnummer_compliance_Korrekt -> check that nothing happens
        Test Excel: Test_inventarnummer_compliance_Fehler -> check that it adds everything correctly
        Test Excel: Test_Inventarnummer_add_x_already_some -> check that it doesn't overwrite
        :param input_df: df to be checked
        :param tranche: name of tranche
        :param in_excel_name: name of excel of the df
        :param regex_function: regex function to be used. If using a specific Abteilung function then it will mark the
        'correct' ones with another abteilung prefix also as wrong.
        :return: bool if there are any, df if there are any, documentation dict
        """
        # clean the column
        input_df = Clean.strip_spaces(input_df)
        # get the RegEx pattern
        pattern_correct, _, _ = regex_function
        # add or overwrite the column (maybe error handling?) that marks the Inventarnummer where something is wrong
        try:
            input_df, _ = Inventarnummer.add_inventarnummer_alt(
                input_df=input_df, in_excel_name=in_excel_name, tranche=tranche)
        # if the column exists we do not want to overwrite it as it may contain important data
        except ColumnExistsError:
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

    # file_name = "Test_inventarnummer_compliance_Fehler"
    # file_path = os.path.join("_Test_Excel", file_name)
    #
    # df = ExF.in_excel_to_df(file_path)
    #
    # boo, out_df, doc = Inventarnummer.add_x_wrong_inventarnummer(
    #     df, "Test", in_excel_name="Test", regex_function=RePat.general_re_pattern())
    #
    # ExF.save_df_excel(out_df, "Test")
    # ExF.save_doc_single("Test", doc)
