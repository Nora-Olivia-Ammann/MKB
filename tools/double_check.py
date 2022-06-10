import os
import warnings

import pandas as pd
import numpy as np
from datetime import date
import re

from save_excel import SaveExcel as SE
from cleaning_df import CleanDF as Clean

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class DoubleCheck:

    @staticmethod
    def double_check(in_data: pd.DataFrame or str, col_name: str, tranche: str or None = None,
                     is_excel: bool = False) -> bool or None:
        if is_excel:
            # read the excel into a dataframe
            df_in = pd.read_excel(io=os.path.join(current_wdir, "input", f"{in_data}.xlsx"))
        else:
            df_in = in_data
        # clean the df
        df_in = Clean.strip_spaces(df_in)
        df_doubles = df_in[df_in[col_name].duplicated(keep=False)]  # returns df with all the doubles
        if len(df_doubles) != 0:
            ex_name = col_name.replace(" ", "_")
            ex_name = ex_name.replace("*", "_")
            SE.save_df_excel(df_doubles, f"{tranche}_{ex_name}_{today}")
        else:
            print("No doubles")

    # double_check("Pilot_Original", is_excel=True, col_name="ObjectID", tranche="Pilot")



if __name__ == "__main__":
    pass
