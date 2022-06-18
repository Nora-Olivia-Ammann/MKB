import os
import warnings

import pandas as pd
import numpy as np
from datetime import date
import re

from tools.excel_functions import ExcelFunctions as ExF
from tools.cleaning_df import CleanDF as Clean


today = str(date.today())
os.chdir("")
current_wdir = os.getcwd()

############################################


class Ethnie:

    @staticmethod
    def get_unique_ethnie(in_excel: str, abteilung: str):
        """
        Gets all the values in the Column "Ethniengruppe (Nation)" and creates a new excel that can be used to change
        spelling that may have changed or racist terminology. The resulting excel is a new key excel, to which data
        should be added. Therefore, this Function should only be used once per abteilung.
        :param in_excel: tranche
        :param abteilung: name
        :return: None
        """
        # read in_excel to df
        df_in = ExF.in_excel_to_df(in_excel)
        # create a new df in which to store the info and copy the column
        df_unique_info = pd.DataFrame(
            {"Kontrolliert": "", "Ethniengruppe (Nation)": df_in["Ethniengruppe (Nation)"], "Ethnie Neu": "",
             "Bsp: Inventarnummer": df_in["Inventarnummer"], "Bsp: Ordner Bild": df_in["Ordner Bild"],
             "Bemerkungen": ""})
        # clean all the blank spaces
        df_unique_info = Clean.strip_spaces_col(df_unique_info, "Ethniengruppe (Nation)")
        # drop all the rows with nan col, modify memory
        df_unique_info.dropna(subset=["Ethniengruppe (Nation)"], inplace=True)
        # remove all the duplicate values
        # drop duplicates keeps the first occurrence
        df_unique_info.drop_duplicates(subset=["Ethniengruppe (Nation)"], keep="first", inplace=True, ignore_index=True)
        ExF.save_df_excel(df_unique_info, f"{abteilung}_Ethnie_Schlüssel_{today}")

    # get_unique_ethnie(in_excel="d_Test_get_unique_ethnie", abteilung="Test")

    @staticmethod
    def add_unique_ethnie(in_excel: str, key_excel: str, abteilung: str):
        """
        Adds new entries in the column "Ethniengruppe (Nation)" to the existing key excel of the abteilung.
        :param in_excel: tranche excel
        :param key_excel: Schlüssel_Ethnie_{abteilung}_{today}
        :param abteilung: name
        :return: None
        """
        # TO THE ALREADY EXISTING LIST OF UNIQUE ETHNIE
        # read the new excel
        df_in = ExF.in_excel_to_df(in_excel)
        # clean the df
        df_in = Clean.strip_spaces_col(df_in, "Ethniengruppe (Nation)")
        # read in the key excel
        df_key = ExF.in_excel_to_df(key_excel)
        # create a temporary df to store only the relevant columns in, that has the same structure as the other df
        temp_in = pd.DataFrame({"Kontrolliert": "", "Ethniengruppe (Nation)": df_in["Ethniengruppe (Nation)"],
                                "Ethnie Neu": "", "Bsp: Inventarnummer": df_in["Inventarnummer"],
                                "Bsp: Ordner Bild": df_in["Ordner Bild"], "Bemerkungen": ""})
        # concat the two dfs, it is important that the key df is in first place since when sorting out duplicates
        # this is the one that is kept
        df_combined = pd.concat([df_key, temp_in], ignore_index=True)
        # sort out the duplicates and keep the first instance
        df_combined.drop_duplicates(subset="Ethniengruppe (Nation)", keep='first', inplace=True, ignore_index=False)
        # save to an excel
        ExF.save_df_excel(df_combined, f"Schlüssel_Ethnie_{abteilung}_{today}")

    # add_unique_ethnie(in_excel="d_Test_add_unique_ethnie_Tranche", key_excel="d_Test_add_unique_ethnie_Schlüssel", abteilung="Test")


if __name__ == "__main__":
    pass
