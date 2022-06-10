import os
import pandas as pd
from datetime import date

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)

if __name__ == "__main__":
    pass
