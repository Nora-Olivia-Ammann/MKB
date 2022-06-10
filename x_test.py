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



