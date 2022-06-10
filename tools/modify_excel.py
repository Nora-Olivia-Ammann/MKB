import os
import warnings

import pandas as pd
import numpy as np
from datetime import date
import re

from save_excel import SaveExcel as SE

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class ModifyExcel:

    @staticmethod
    def combine_excel(list_in_excel: list[str], tranche: str, name_out_excel: str, abteilung: str) -> None:
        """
        Combines any number of excels. Should be of the same format
        :param list_in_excel: names of the excel that should be combined, no extension
        :param tranche: tranchen, that will be combined (e.g. T1-T3)
        :param name_out_excel: name of the out excel
        :param abteilung: name of the Abteilung
        :return: None
        """
        # read the documentation excel
        df_doc = pd.read_excel(
            os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))
        # an unknown number of excels should be read in and combined to a single excel for further processing
        # initiate an empty list to store the df in
        # for further processing we cannot use the list with the names as strings
        df_list = []
        # iterate over the excel and df name list to create df
        for ind in range(0, len(list_in_excel)):
            # turn the strings into variables to which we can assign the df
            globals()[f"df_{ind}"] = pd.read_excel(
                os.path.join(current_wdir, "input", "", f"{list_in_excel[ind]}.xlsx"))
            # append the variables to a list
            df_list.append(globals()[f"df_{ind}"])
        # combine the dfs into one
        df_combined = pd.concat(df_list, ignore_index=True)
        SE.save_df_excel(df_combined, f"{name_out_excel}_{today}")
        # write documentation
        """df_doc = pd.concat([df_doc, pd.DataFrame(
            {"Datum": today, "Tranche": tranchen, "Input Dokument": list_in_excel, "Schlüssel Excel": "-", "Feld": "-",
             "Was": "Zusammenfügen der Excel", "Resultat": f"", "Output Dokument": f"{name_out_excel}_{today}",
             "Ersetzt Hauptexcel": "fügt mehrere zusammen"}, index=[0])], ignore_index=True)"""
        df_doc = pd.concat([df_doc, pd.DataFrame(
            {"Datum": today, "Tranche": tranche, "Input Dokument": list_in_excel, "Schlüssel Excel": "",
             "Feld": "", "Was": "",
             "Resultat": f"", "Output Dokument": f"", "Ersetzt Hauptexcel": ""}, index=[0])], ignore_index=True)
        SE.save_doc_excel(df_doc, abteilung)

    # combine_excel(list_in_excel=["a_Test_combine_excel_1", "a_Test_combine_excel_2", "a_Test_combine_excel_3"],
    #               tranche="Test", name_out_excel="T1-3", abteilung="Test")

    @staticmethod
    def shorten_tranchen_excel(in_excel: str, num_rows: int, out_excel: str) -> None:
        """
        Saves an excel with a specified number of rows, it will only contain rows that have a correct Inventarnummer,
        Beschreibung and Inschrift and no duplicates. The resulting excel will be used to test other functions.
        :param in_excel: exel to shorten
        :param num_rows: number of rows that the new excel should have
        :param out_excel: name of the new excel
        :return: None
        """
        # read in_excel to df, which is the one to fill with values
        df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{in_excel}.xlsx"))
        # drop columns that are nan in required fields
        df_in.dropna(subset=["Inventarnummer"], inplace=True)
        df_in.dropna(subset=["Beschreibung"], inplace=True)
        df_in.dropna(subset=["Inschrift"], inplace=True)
        # if it is not re-indexed at this stage we will get an IndexError when checking for the RegEx Pattern
        df_in.reset_index(inplace=True)  # reset the index
        df_in.pop("index")  # when resetting the index it is saved as a new column
        # we only want rows that have a correct inventarnummer and do not miss mandatory information
        # the correct pattern
        correct_pattern = re.compile(r"^\(F\)[IV]{1,3}[abcde]?\s[1-9][0-9]*[a-z]?$")
        for index, value in df_in["Inventarnummer"].iteritems():
            if not correct_pattern.match(value):
                df_in.drop(index=index, axis=0, inplace=True)
        df_in.reset_index(inplace=True)  # reset the index
        # drop duplicates
        df_in.drop_duplicates(subset=["Inventarnummer"], keep="first", inplace=True, ignore_index=True)
        df_in.pop("index")  # when resetting the index it is saved as a new column
        df_in.drop(index=df_in.index[num_rows + 1:], axis=0, inplace=True)
        SE.save_df_excel(df_in, out_excel)

    # shorten_tranchen_excel(in_excel="a_Test_shorten_excel", num_rows=20, out_excel="Test_Shortened")

    @staticmethod
    def excel_identical_check(excel_one: str, excel_two: str):
        """
        Checks if two excels are identical.
        :param excel_one: First excel
        :param excel_two: Second excel
        :return: bool
        """
        df_one = pd.read_excel(os.path.join(current_wdir, "input", f"{excel_one}.xlsx"))
        df_two = pd.read_excel(os.path.join(current_wdir, "input", f"{excel_two}.xlsx"))
        return df_one.equals(df_two)


if __name__ == "__main__":
    pass
