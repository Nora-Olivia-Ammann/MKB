import os
from datetime import date

import pandas as pd


today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)
doc_list = []

doc_dict = {1: 1, 2: 2}
doc_list.append(doc_dict)

doc_dict = {3: 3}
doc_list.append(doc_dict)


print(doc_list)

