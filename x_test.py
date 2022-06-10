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


def check_para(function_name):
    pattern_correct, pattern_leading_zero, pattern_dummy = function_name
    print(pattern_correct)


check_para(REPAT.ozeanien_re_pattern())
