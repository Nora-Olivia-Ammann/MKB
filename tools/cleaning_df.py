import os
from datetime import date

import pandas as pd

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################


class CleanDF:

    @staticmethod
    def strip_spaces(in_df: pd.DataFrame) -> pd.DataFrame:
        """
        This removes all the leading and trailing blank spaces in the df. This is important so that two values that
        are identical are not mistaken for different ones because of leading and trailing blank spaces.
        :param in_df: df that should be cleaned
        :return: cleaned df
        """
        return in_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

