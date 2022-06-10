import os
from datetime import date

import numpy as np
import pandas as pd

from tools.excel_functions import ExcelFunctions as ExF

# import functions from other documents


today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()
############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


def get_inventarnummer_tranche(list_in_excel: list[str]) -> None:
    """
    extracts the inventarnummer from the excels and saves them to a new one together
    :param list_in_excel:
    :return:
    """
    # read in all the excels
    df_pil = pd.read_excel(os.path.join(current_wdir, "input", f"{list_in_excel[0]}.xlsx"))
    df_1 = pd.read_excel(os.path.join(current_wdir, "input", f"{list_in_excel[1]}.xlsx"))
    df_2 = pd.read_excel(os.path.join(current_wdir, "input", f"{list_in_excel[2]}.xlsx"))
    df_pil = pd.DataFrame({"Inventarnummer": df_pil["Inventarnummer"], "Tranche": "Pilot"})
    df_1 = pd.DataFrame({"Inventarnummer": df_1["Inventarnummer"], "Tranche": "19-01"})
    df_2 = pd.DataFrame({"Inventarnummer": df_2["Inventarnummer"], "Tranche": "20-01"})
    df_out = pd.concat([df_pil, df_1, df_2], ignore_index=True)
    ExF.save_df_excel(df_out, "Oz1-3_Inventarnummern")


#get_inventarnummer_tranche(["Pilot_2022-02-08", "Metadaten_Tranche_19-01", "Metadaten_Tranche_20-01"])


def combine_excel(list_in_excel: list[str], name_out_excel: str) -> None:
    """
    Combines any number of excels. Should be of the same format
    :param list_in_excel: names of the excel that should be combined, no extension
    :param name_out_excel: name of the out excel
    :return: None
    """
    # an unknown number of excels should be read in and combined to a single excel for further processing
    # initiate an empty list to store the df in
    # for further processing we cannot use the list with the names as strings
    df_list = []
    # iterate over the excel and df name list to create df
    for ind in range(0, len(list_in_excel)):
        # turn the strings into variables to which we can assign the df
        globals()[f"df_{ind}"] = pd.read_excel(os.path.join(current_wdir, "input", "", f"{list_in_excel[ind]}.xlsx"))
        # append the variables to a list
        df_list.append(globals()[f"df_{ind}"])
    # combine the dfs into one
    df_combined = pd.concat(df_list, ignore_index=True)
    ExF.save_df_excel(df_combined, f"{name_out_excel}_{today}")


def get_unique_geo_tms(in_excel: str) -> None:
    df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{in_excel}.xlsx"))
    # get the ethno info separately
    df_ethno = pd.DataFrame({"Kultur": df_in["Kultur"], "Ethniengruppe (Nation)": df_in["Ethniengruppe (Nation)"]})
    df_ethno.drop_duplicates(subset=['Kultur', 'Ethniengruppe (Nation)'], keep='first', inplace=True)
    df_ethno.dropna(axis=0, how='all', inplace=True)
    ExF.save_df_excel(df_ethno, "Ozeanien_Ethnie_TMS")
    # remove from the general df
    df_in.drop(columns=["Kultur", "Ethniengruppe (Nation)"], inplace=True)
    # drop all the rows that are only NaN
    df_in.dropna(axis=0, how='all', inplace=True)
    # remove duplicates
    df_in.drop_duplicates(
        subset=['Herk.6: Land', 'Departement/Provinz/Kanton', "Herk.1: Ort", "Distrikt", "Bezirk/Gemeinde",
                "Herk.7: Subkontinent", "Herk.4: Grossregion/gr. Insel", "Herk.3: Gebiet/Unterregion/kl. Insel",
                "Herk.2: Landschaft/Fluss", "Herk.8: Politische Region", "Inselgruppe", "Insel"],
        keep='first', inplace=True)
    ExF.save_df_excel(df_in, "Ozeanien_Geo_TMS")


def add_dublette_check(in_excel, name_excel):
    df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{in_excel}.xlsx"))
    df_in.insert(df_in.columns.get_loc("Inventarnummer")+1, "Dublette", np.nan)
    df_in.insert(df_in.columns.get_loc("Ordner Bild")+1, "Bilddatei", np.nan)
    df_in["Dublette"] = df_in.duplicated(subset="Inventarnummer", keep=False)
    repl_dict = {True: "x", False: np.nan}
    df_in.replace(to_replace=repl_dict, inplace=True)
    ExF.save_df_excel(df_in, name_excel)



