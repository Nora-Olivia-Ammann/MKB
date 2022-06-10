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


class TMSEinlauf:

    @staticmethod
    def key_einlauf_completion_check(key_data: pd.DataFrame or str, is_excel: bool = False) \
            -> bool and pd.DataFrame or None:
        """
        Checks whether all the mandatory information in the Excel from the TMS export is there.
        If used as a nested function it returns True if all is correct.
        :param key_data: excel TMS / df
        :param is_excel: True if it is excel
        :return: True if all is good, False if values are missing and df with rows that miss values.
        """
        if is_excel:
            # read in_excel to df, which is the one to fill with values
            df_key = pd.read_excel(os.path.join(current_wdir, "input", "", f"{key_data}.xlsx"))
        else:
            df_key = key_data
        # none of these should be empty
        if df_key[["Erwerbungsart", "Objektstatus"]].isnull().any().any():
            df_nan = df_key[df_key["Erwerbungsart"].isnull()]
            df_nan = pd.concat([df_nan, df_key[df_key["Objektstatus"].isnull()]], ignore_index=True)
            # sort out the duplicates and keep the first instance
            df_nan.drop_duplicates(subset="Inventarnummer", keep='first', inplace=True, ignore_index=False)
            df_nan.sort_values(by=["Inventarnummer"], ascending=True, inplace=True, ignore_index=True)
            if is_excel:
                # save the df
                SE.save_df_excel(df_nan, f"Schlüssel_Einlauf_Fehlende_Angaben_{today}")
            else:
                return False, df_nan
        else:
            if is_excel:
                print("Einlaufschlüssel Korrekt.")
            else:
                return True, None

    # key_einlauf_completion_check(key_data="_Test_Excel/c_key_einlauf_completion_check_Korrekt", is_excel=True)
    # key_einlauf_completion_check(key_data="_Test_Excel/c_key_einlauf_completion_check_Fehler", is_excel=True)


if __name__ == "__main__":
    pass
