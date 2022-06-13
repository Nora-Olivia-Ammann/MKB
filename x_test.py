import os
from datetime import date

import numpy as np
import pandas as pd

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)

a = False
b = False

if all(result == False for result in (a, b)):
    print("All False")
else:
    print("Not all False")
