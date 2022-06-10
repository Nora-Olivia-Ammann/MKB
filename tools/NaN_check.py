import os
import warnings

import pandas as pd
import numpy as np
from datetime import date
import re

from excel_functions import ExcelFunctions as ExF

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)

# TODO: complete rewrite


class NaN:

    @staticmethod
    def has_columns_NaN(input_df: pd.DataFrame, column_list: list[str], is_excel: bool = False,
                        tranche: str or None = None, abteilung: str or None = None,
                        separate_excel_columns: bool = False) -> bool and pd.DataFrame or None:
        """
        Checks if any columns from a list have NaN values. It removes these rows from the main excel and either returns one
        excel with all the rows or for each column a separate excel. Can also be used as a nested function. Then it also
        returns a bool. True, if any columns have NaN
        :param in_data: excel / df
        :param is_excel: True if excel
        :param tranche: name
        :param abteilung: name
        :param column_list: list with the names of the column(s), has to be list even if it is only one
        :param separate_excel_columns: True, if for each column a separate excel should be created
        :return: if not excel: Bool whether there are NaN, if separate excel: list with df, list with excel name, df without
                NaN / if one excel: df with nan, name for excel and df without nan
        """
        df_not_nan = input_df.dropna(subset=column_list, how="any", inplace=False)
        # if it is not an excel we return the list of the df_f
        return_ex_name = []
        retrun_df_list = []
        # if we want a separate excel for each column
        if separate_excel_columns:
            for column in column_list:
                # create a new df with all missing elements in the chosen column
                df_nan = input_df[input_df[column].isnull()]
                # if there are NaN values save as an excel and write documentation
                if len(df_nan) != 0:
                    # if there is a blank space in the column name it would throw a file not found error
                    ex_name = column.replace(" ", "_")
                    if is_excel:
                        SE.save_df_excel(df_nan, f"{tranche}_{today}_Fehlende_{ex_name}")
                        df_doc = pd.concat([df_doc, pd.DataFrame(
                            {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": "-",
                             "Feld": f'{column}', "Was": "Vollständigkeit", "Resultat": f"{len(df_nan)} fehlen",
                             "Output Dokument": f"{tranche}_{today}_Fehlende_{ex_name} // "
                                                f"{tranche}_{today}_Angaben_Komplett",
                             "Ersetzt Hauptexcel": "unterteilt es"}, index=[0])], ignore_index=True)
                    else:
                        retrun_df_list.append(df_nan)
                        return_ex_name.append(ex_name)
                if not is_excel and len(retrun_df_list) != 0:
                    return True, retrun_df_list, return_ex_name, df_not_nan
                # otherwise, state in documentation that there were no NaN values in the specific column
                if len(df_nan) == 0:
                    if is_excel:
                        df_doc = pd.concat([df_doc, pd.DataFrame(
                            {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": "-",
                             "Feld": f'{column}', "Was": "Vollständigkeit", "Resultat": f"0 fehlen",
                             "Output Dokument": f"-", "Ersetzt Hauptexcel": "-"}, index=[0])], ignore_index=True)
                    else:
                        return False, None, None, None
        # if we only want one exel for the whole document
        else:
            # make a new df to store the NaN columns
            df_nan = pd.DataFrame({})
            for column in column_list:
                # append the NaN rows to the df
                df_nan = df_nan.append(input_df[input_df[column].isnull()], ignore_index=True)
            # drop the duplicates
            df_nan.drop_duplicates(subset=["Unique_ID"], keep="first", inplace=True, ignore_index=True)
            # if there are NaN values save as an excel and write documentation
            if len(df_nan) != 0:
                if is_excel:
                    ExF.save_df_excel(df_nan, f"{tranche}_{today}_Fehlende_Angaben")
                    # write documentation
                    df_doc = pd.concat([df_doc, pd.DataFrame(
                        {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": "-",
                         "Feld": f'{column_list}', "Was": "Vollständigkeit", "Resultat": f"{len(df_nan)} fehlen",
                         "Output Dokument": f"{tranche}_{today}_Fehlende_Angaben // {tranche}_{today}_Angaben_Komplett",
                         "Ersetzt Hauptexcel": "unterteilt es"}, index=[0])], ignore_index=True)
                else:
                    return True, df_nan, "_Fehlende_Angaben", df_not_nan
            # otherwise, state in documentation that there were no NaN values in the specific column
            else:
                if is_excel:
                    df_doc = df_doc.append(
                        {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": "-",
                         "Feld": f'{column_list}',
                         "Was": "Vollständigkeit", "Resultat": f"0 fehlen", "Output Dokument": f"-",
                         "Ersetzt Hauptexcel": "-"},
                        ignore_index=True)
                else:
                    return False, None, None, None
        if is_excel:
            ExF.save_doc_excel(df_doc, abteilung)
            ExF.save_df_excel(df_not_nan, f"{tranche}_{today}_Angaben_Komplett")

    # has_columns_NaN(in_data="a_Test_has_columns_NaN", is_excel=True, tranche="Test", abteilung="Test",
    #                 column_list=["Spalte_2", "Spalte_4"], separate_excel_columns=True)


if __name__ == "__main__":
    pass
