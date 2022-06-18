import os
import pandas as pd
import numpy as np
from datetime import date

from tools.excel_functions import ExcelFunctions as ExF

from tools.beschreibung import Beschreibung as Besch
from tools.cleaning_df import CleanDF as Clean
from tools.columns_to_string import ColumnsToStr as ColStr
from tools.custom_exceptions import *
from tools.double_check import DoubleCheck as Double
from tools.geographie import Geographie as Geo
from tools.inschrift_tranche import Inschrift as Insch
from tools.inventarnummer import Inventarnummer as InvNr
from tools.key_excel import KeyExcel as KE
from tools.modify_excel import ModifyExcel as ModE
from tools.NaN_check import NaN as NAN
from tools.picture_files import PictureFiles as Pic
from tools.RegEx_patterns import RegExPattern as RePat
from tools.TMS_inschrift import TMSEinlauf as TMSInsch
from tools.unique_ID import UniqueID as UID

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)

if __name__ == "__main__":
    pass

doc_list = []

"""
doc_list.append({
    "Datum": today,
    "Tranche": tranche,
    "Input Dokument": in_excel,
    "Schlüssel Excel": "",
    "Feld": "",
    "Was": "",
    "Resultat": f"",
    "Output Dokument": f"",
    "Ersetzt Hauptexcel": ""})
"""

# mit output
"""
doc_dict.update(
    {"Tranche": tranche, 
     "Input Dokument": in_excel, 
     "Schlüssel Excel": key_excel, 
     "Output Dokument": output_name})
"""

# ohne output
"""
doc_dict.update(
    {"Tranche": tranche, 
     "Input Dokument": in_excel, 
     "Schlüssel Excel": key_excel})
"""


# doc_list.append({"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "", "Feld": "", "Was": "", "Resultat": f"", "Output Dokument": f"", "Ersetzt Hauptexcel": ""})


def new_funct(in_excel, key_excel, tranche, abteilung):
    # read in the excels
    df_in = ExF.in_excel_to_df(in_excel)
    doc_list = []
    df_key = ExF.in_excel_to_df(key_excel)

    ############################################

    # save df
    ExF.save_df_excel(df_in, f"{tranche}_{today}")
    ExF.save_doc_list(doc_list, abteilung)


#####################
# NEW DF
df_in = pd.DataFrame({})
# works with a list of dicts or rows from a df
dic_list = [{}, {}]
df_out = pd.DataFrame.from_records(dic_list)
# just defining column names
df_key = pd.DataFrame(columns=["col names"])

# optional index= fills it with 100 empty rows
df = pd.DataFrame(columns=["col names"], index=range(0, 100))

# concat with only one dict
# if not index= then ValueError: If using all scalar values, you must pass an index
df_merged = pd.concat([df_in, pd.DataFrame({}, index=[0])], ignore_index=True)

#####################
# INSERT COLUMN

# index, name, value
df_in.insert(0, "Col_Name", np.nan)
# get index number of specific column by name
ind = df_in.columns.get_loc("Col_Name")

# check if column exists
if "col_name" in df_in.columns:
    raise ColExistsError("The Column already exists.")
# check if more than one column already exists
# in order for the Exception to be raised both have to already exist, if only one exists no Exception will be raised
if {"Col1", "Col2"}.issubset(df_in.columns):
    raise ColExistsError("The Column already exists.")

######################
# BOOLEAN COLUMNS

# get the index of the column we want to evaluate
index = df_in.columns.get_loc("Col")

# NaN Bool
# insert the column to the right that states true for all np.nan
df_in.insert(loc=index + 1, column=f"Col_Nan", value=df_in["Col"].isnull())

# Duplicate Bool
# makes a bool column to the right that states true for all doubles
df_in.insert(loc=index + 1, column=f"Col_Double", value=df_in.duplicated(subset="Col", keep=False))

# Replace the bool values of the column with the values according to the dict
df[f"BoolCol"].replace(to_replace={True: "x", False: np.nan}, inplace=True)

#####################
# SORTING VALUES
df_in.sort_values(by=["Inventarnummer"], ascending=True, inplace=True, na_position='first', ignore_index=True)

df_in.sort_values(by=["Ordner Bild", "Inventar Sortierbar"], inplace=True, ignore_index=True)

#####################
# SELECTING AND DROPPING
df_in["col"][1:]  # from the second row onwards

# drop first row, modifies memory of df (inplace)
df_in.drop(index=df_in.index[0], axis=0, inplace=True)

df_in.reset_index(inplace=True)  # reset the index
df_in.pop("index")  # when resetting the index it is saved as a new column

# get only the first row of the df (second header), does not modify df (inplace)
df_head = df_in.iloc[0, :]

# .drop() CANNOT BE USED IN A LOOP AS THE DF MAY BECOME SMALLER THAN THE INDEX NUMBER (IndexError)
# drop all the content of a df so that only the header remains
df_in.drop(index=df_in.index[:], axis=0, inplace=True)

# for usage in a loop
drop_index_list = []
for index, value in df_in["col"].iteritems():
    df_out = df_out.append(df_in.iloc[index, :], ignore_index=True)
    drop_index_list.append(index)
df_in.drop(index=drop_index_list, axis="index", inplace=True)

df_in.drop(columns=["col list"], inplace=True)  # dropping a list of columns

df_in.pop("col")  # dropping a single column, does not work for multiples, changes df in memory

#####################
# FILLING COLUMNS
# fill from the second col onwards with nan
df_in["col"][1:] = np.nan

# fill from the second col onwards with value
df_in["col"][1:] = "value"

# fill NaN with specific value
df_in["col"] = df_in["col"].fillna("value")

# adding nan rows so that df_out has as many rows as df_in
df_out = df_out.reindex(index=list(range(0, len(df_in.index))))

#####################
# DUPLICATES
df_doubles = df_in[df_in["Col"].duplicated(keep=False)]  # returns df with all the doubles

# drops all the duplicates from the col subset, keeps no duplicates, resets index, and overwrites df
df_in.drop_duplicates(subset=["col"], keep=False, inplace=True, ignore_index=True)

# drop duplicates keeps the first occurrence
df_in.drop_duplicates(subset=["col"], keep="first", inplace=True, ignore_index=True)

# Drop duplicates based on several columns (all column values have to be identical), removes and resets index
df_in.drop_duplicates(subset=['Col1', 'Col2'], keep='first', inplace=True)

# assigns boolean array to column with true if a value in the specified column appears several times
df_in["Dublette"] = df_in.duplicated(subset="Dublette_Check_Col", keep=False)

#####################
# NULL CHECK
df_in["Col"].isnull()  # bool True if null
df_in["Col"].isnull().any()  # True if any are null in that col
df_in["Col"].isnull().all()  # true if all are null in that col

df_in[["A", "B"]].isnull().any()  # gives bool for each col
df_in[["A", "B"]].isnull().any().any()  # one bool, true if any of the cols are nan

df_nan = df_in[df_in["Col"].isnull()]  # create a new df with all missing elements in the chosen column
# df_nan.pop("index")  # the index is added as a column which we drop

# drop all the rows with nan in a specific col and save in a new df
df_not_nan = df_in.dropna(subset=["col"], inplace=False)

# drop all the rows with nan in specific col, modify memory
df_in.dropna(subset=["col"], inplace=True)

# drop all the rows that are only NaN
df_in.dropna(axis=0, how='all', inplace=True)

#####################
# FILTER
# create a boolean filter which assigns false to all values that are not present in the key_excel
einlauf_filter = df_in["Inschrift"].isin(df_key["Inschrift"])
# check if any are False
if not einlauf_filter.all():
    # create a df to store the results in
    df_out = pd.DataFrame(columns=["col"])
    # as we want the values that are new we need to have the False values, the default would result in a df
    # that contains the values that are present in both df
    df_out["Inschrift"] = df_in[einlauf_filter == False]

#####################
# ITERATION
# ITERATE OVER COLUMN
for index, value in df_in["col"].iteritems():
    print("do something")

# ITERATE OVER ROW
for index, row in df_in.iterrows():
    print(row)

#####################
# MAP A COLUMN
# Map only NaN rows in column
# make a dictionary with the columns from the df
# we want to fill in the date, if there is not already a value in place
map_dict = dict(zip(df_key["Key_word"], df_key["Key_Value"]))

# as we do not want to overwrite existing values we use the fillna function
df_in["Value_Col"] = df_in["Value_Col"].fillna(df_in["Key_col"].map(map_dict))

# Map and overwrite
df_in["Value_Col"] = df_in["Key_col"].map(map_dict)

#####################
# REPLACE
df_in.replace(to_replace=map_dict, inplace=True)

#####################
# CONCAT DATAFRAMES
df_list = [df_head, df_in, df_nan]
df_combined = pd.concat(df_list, ignore_index=True)

#####################
# RENAMING A COLUMN
df_in.rename(columns={"Col_Old": "Col_New"}, inplace=True)

#####################
# ADDING A NEW COLUMN
df_in.insert(index, "ColName", "col_content")

# new column in the first place without content
df_in.insert(0, "ColName", np.nan)
