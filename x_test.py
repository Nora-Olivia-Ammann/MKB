import os
from datetime import date

import numpy as np
import pandas as pd


today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

from tools.RegEx_patterns import RegExPattern as RePat
from tools.inventarnummer import Inventarnummer

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)

input_df = pd.DataFrame({"Inventarnummer": ["(F)VB 16670", " (F)V 123", "(F) Vb 123", "(F)Vb 01245", "(F)bs 12356 ",
                                      "(F)Vb Vb 123", "Vb 1235",
                                      "(F)Vb DU-0118", "(F)Vb DU-0", "(F)Vb 0", "(F)Vb DU-", "", "(F)Vc 00",
                                      "(F)Vc 001"]})

pattern_correct, pattern_leading_zero, pattern_dummy = RePat.general_re_pattern()

index = input_df.columns.get_loc("Inventarnummer")
input_df.insert(index + 1, "Führende 0", np.nan)

# iterate over the df
for index, invnr in input_df["Inventarnummer"].iteritems():
    # RegEx only takes str if it is an int or float it will throw an error
    if pattern_leading_zero.match(invnr):
        # get the new value
        new_invnr = Inventarnummer.remove_leading_zero(invnr)
        # replace the value in the in_df
        input_df.loc[index, "Inventarnummer"] = new_invnr
        input_df.loc[index, "Führende 0"] = "x"

print(1)
