import os
from datetime import date

import pandas as pd

from tools.RegEx_patterns import RegExPattern as REPAT

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


def check_para(function_name: str or None):
    if function_name:
        print(function_name)
    else:
        print(None)


check_para(None)

