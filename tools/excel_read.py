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

class ReadExcel:

    @staticmethod
    def in_excel_to_df(in_excel: str) -> pd.DataFrame:
        return pd.read_excel(os.path.join(current_wdir, "input", f"{in_excel}.xlsx"))

    def doc_excel_to_df(abteilung: str) -> pd.DataFrame:
        return pd.read_excel(os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))


if __name__ == "__main__":
    pass
