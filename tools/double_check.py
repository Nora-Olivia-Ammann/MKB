import os
import pandas as pd
from datetime import date

from cleaning_df import CleanDF as Clean
from excel_functions import ExcelFunctions as ExF

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

# TODO: complete rewrite


class DoubleCheck:

    @staticmethod
    def double_check(input_df: pd.DataFrame or str, col_name: str, tranche: str or None = None,
                     ) -> bool or None:
        # clean the df
        input_df = Clean.strip_spaces(input_df)
        df_doubles = input_df[input_df[col_name].duplicated(keep=False)]  # returns df with all the doubles
        if len(df_doubles) != 0:
            ex_name = col_name.replace(" ", "_")
            ex_name = ex_name.replace("*", "_")
            ExF.save_df_excel(df_doubles, f"{tranche}_{ex_name}_{today}")
        else:
            print("No doubles")

    # double_check("Pilot_Original", is_excel=True, col_name="ObjectID", tranche="Pilot")



if __name__ == "__main__":
    pass
