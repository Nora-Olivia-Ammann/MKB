import os
import pandas as pd
import numpy as np
from datetime import date
import warnings
import random
from tools.excel_functions import ExcelFunctions as ExF

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


def add_barcode_BSB(in_excel: str) -> None:
    # read in the excels
    df_in = ExF.in_excel_to_df(in_excel)
    len_df = len(df_in)
    df_in.insert(0, "Barcode_BSB", np.nan)
    random_set = set(x for x in random.sample(range(1111111, 9999999), 50))
    while len(random_set) < 50:
        random_set.update(random.sample(range(1111111, 9999999), 1))
    start = 0
    stop = 5
    for x in random_set:
        while start <= stop and start != len_df:
            df_in.loc[start, "Barcode_BSB"] = x
            start += 1
        else:
            stop += 30
    # save df
    ExF.save_df_excel(df_in, f"Test_Pilot_Barcode")


#add_barcode_BSB("Pilot_Original")


def get_unique_barcode(in_excel: str) -> None:
    df_in = ExF.in_excel_to_df(in_excel)
    df_out = pd.DataFrame(columns=["Barcode_BSB", "Besch_Karteikarte"], index=range(0, len(df_in)))
    df_out["Barcode_BSB"] = df_in["Barcode_BSB"]
    df_out.drop_duplicates(subset=["Barcode_BSB"], keep="first", inplace=True, ignore_index=True)
    ExF.save_df_excel(df_out, "_Test_Unique_Barcode_BSB")


#get_unique_barcode("_Test_add_barcode_BSB_Excel_BSB")


def map_barcode_tranche(in_excel: str, bsb_excel: str, tranche: str) -> None:
    df_tranche = ExF.in_excel_to_df(in_excel)
    df_bsb = ExF.in_excel_to_df(bsb_excel)
    map_dict = dict(zip(df_bsb["Inventarnummer"], df_bsb["Barcode_BSB"]))
    df_tranche.insert(0, "Barcode_BSB", np.nan)
    df_tranche["Barcode_BSB"] = df_tranche["Inventarnummer"].map(map_dict)
    if df_tranche["Barcode_BSB"].isnull().any():
        warnings.warn("An Inventarnummer is missing.")
        df_nan = df_tranche[df_tranche["Barcode_BSB"].isnull()]
        ExF.save_df_excel(df_nan, f"{tranche}_Fehlende_Barcode")
    ExF.save_df_excel(df_tranche, f"{tranche}_{today}")


#map_barcode_tranche("Pilot_Komplett_2022-02-16", "_Test_add_barcode_BSB_Excel_BSB", "Test")


def map_kk_content_barcode(in_excel: str, key_excel: str, tranche: str) -> None:
    df_in = ExF.in_excel_to_df(in_excel)
    df_key = ExF.in_excel_to_df(key_excel)
    # TODO: check if all in dict
    map_dict = dict(zip(df_key["Barcode_BSB"], df_key["Besch_Karteikarte"]))
    df_in["Besch_KarteiKarte"] = df_in["Barcode_BSB"].map(map_dict)
    ExF.save_df_excel(df_in, f"{tranche}_{today}")


#map_kk_content_barcode("_Test_Tranche_Barcode", "_Test_Schlüssel_Barcode_BSB", "Test")

