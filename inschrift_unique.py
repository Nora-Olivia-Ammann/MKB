import os
import pandas as pd
import numpy as np
from datetime import date

from tools.excel_functions import ExcelFunctions as ExF
from tools.cleaning_df import CleanDF as Clean

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


def get_unique_einlauf(in_excel: str, tranche: str) -> None:
    """
    Gets all the Einlaufnummer in column "Inschrift" once in a new excel.
    :param in_excel: excel
    :param tranche: name
    :return: saves excel
    """
    # read in_excel to df
    df_in = ExF.in_excel_to_df(in_excel)
    # clean the df
    df_in = Clean.strip_spaces_col(df_in, "Inschrift")
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


def add_unique_einlauf(in_excel: str, key_excel: str, out_tranche: str) -> None:
    df_in = ExF.in_excel_to_df(in_excel)
    # clean the df
    df_in = Clean.strip_spaces_col(df_in, "Inschrift")
    # read key_excel in which will provide the dictionary
    df_key = ExF.in_excel_to_df(key_excel)
    # clean the df
    df_key = Clean.strip_spaces_whole_df(df_key)
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
