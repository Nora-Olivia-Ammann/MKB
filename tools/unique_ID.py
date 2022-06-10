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


class UniqueID:

    @staticmethod
    def add_unique_ID(in_data: str or pd.DataFrame, prefix_unique_ID: str, is_excel: bool = False,
                      tranche: str or None = None) -> pd.DataFrame or None:
        """
        Adds a new column if not existing to a df with a Unique_ID. If not Tranche will get the same prefix, then
        the ID will be unique amongst all Tranchen. This helps to difinitively identify a row.
        :param in_data: Excel or dataframe
        :param is_excel: if in_data is an excel it is True
        :param tranche: name
        :param prefix_unique_ID: should refer to the tranche (e.g. Test -> T1)
        :return: if not excel then df otherwise None
        """
        if is_excel:
            # read in the excel with the data
            df_in = pd.read_excel(os.path.join(current_wdir, "input", "", f"{in_data}.xlsx"))
        else:
            df_in = in_data
        # as at this stage the inventarnummer may change, there is no way to uniquely identify a row
        # therefore we create our own ID, by adding leading zeros we make this number sortable and thus preserve the
        # original order
        df_in["Unique_ID"] = df_in.index + 1
        df_in["Unique_ID"] = df_in["Unique_ID"].apply(lambda x: f"{prefix_unique_ID}_{str(x).zfill(5)}")
        if is_excel:
            # save the df
            ExF.save_df_excel(df_in, f"{tranche}_{today}")
        else:
            return df_in

    # add_unique_ID(in_data="a_Test_add_Unique_ID", is_excel=True, tranche="Test", prefix_unique_ID="T1")


if __name__ == "__main__":
    pass
