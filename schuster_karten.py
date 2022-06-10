import os
import pandas as pd
import numpy as np
from datetime import date

import re
import warnings
from tools.beschreibung import Beschreibung as BE
from tools.cleaning_df import CleanDF as Clean
from tools.columns_to_string import ColumnsToStr as COLSTR
from tools.custom_exceptions import *
from tools.ethnie import Ethnie as ETHN
from tools.double_check import DoubleCheck as DOUBLE
from tools.geographie import Geographie as GEO
from tools.inschrift_einlaufnummer_tranche import Inschrift as INSCH
from tools.inventarnummer import Inventarnummer as INVNR
from tools.key_excel import KeyExcel as KE
from tools.modify_excel import ModifyExcel as MODEX
from tools.NaN_check import NaN as NAN
from tools.RegEx_patterns import RegExPattern as REPAT
from tools.save_excel import SaveExcel as SE
from tools.TMS_einlauf import TMSEinlauf as TMSEINL
from tools.unique_ID import UniqueID as UID


today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


def add_transcript_schuster(in_excel: str) -> None:
    """
    Joins the geo info and creates a transcript that can be added to the Beschreibung
    :param in_excel: Schuster main excel
    :return: None
    """
    # combine all the geo info and save them in a new column
    df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{in_excel}.xlsx"))
    # make a list of the column name
    col_list = ["Herk.7: Subkontinent", "Herk.4: Grossregion/gr. Insel", "Herk.3: Gebiet/Unterregion/Kl. Insel",
                 "Herk.6: Land", "Herk.1: Ort", "Kultur"]
    # make a list of the prefixes that should appear in the string corresponding to each column
    name_list = ["Subkontinet", "Grossregion", "Gebiet/Unterregion", "Land", "Ort", "Kultur"]
    # iterate over the rows
    for index, row in df_in.iterrows():
        # initiate an empty list
        besch = []
        # with a range iterate over the lists
        for i in range(0, 6):
            # check if the col is empty
            if row[col_list[i]] is not np.nan:
                # if not: extract the information
                val = row[col_list[i]]
                # format the information and add it to the list
                besch.append(f"{name_list[i]}: {val}")
        # if there is only one element extract it
        if len(besch) == 1:
            b_str = besch[0]
        # if there is none assign nan
        elif len(besch) == 0:
            b_str = np.nan
        # join elements of list to form a string
        else:
            b_str = "; ".join(besch)
        # add the string to that row
        df_in.loc[index, "Original Geo Neu"] = b_str
    # save excel
    SE.save_df_excel(df_in, f"Schuster_Karten_{today}")


#add_transcript_schuster("Karten_Schuster_2022-03-10")


def get_geo_schuster(in_excel: str) -> None:
    """
    Creates geo key excel for Schuster excel.
    :param in_excel: Schuster Main Excel
    :return:
    """
    # read in_excel to df
    df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{in_excel}.xlsx"))
    # transfer the geo info into the format of the key excel
    df_out = pd.DataFrame({
        "Kontrolliert": "", "Inventarnummer": df_in["Inventarnummer"], "Geo_ID": "", "Kultur": df_in["Kultur"],
        "Herk.9: Kontinent": "", "Herk.7: Subkontinent": df_in["Herk.7: Subkontinent"],
        "Herk.6: Land": df_in["Herk.6: Land"], "Herk. 8: Politische Region": "",
        "Herk.4: Grossregion/gr. Insel": df_in["Herk.4: Grossregion/gr. Insel"], "Inselgruppe": "",
        "Herk.3: Gebiet/Unterregion/Kl. Insel": df_in["Herk.3: Gebiet/Unterregion/Kl. Insel"],
        "Departement/Provinz/Kanton": df_in["Departement/Provinz/Kanton"], "Distrikt": "", "Insel": "",
        "Herk.2: Landschaft/Fluss": "", "Bezirk/Gemeinde": "", "Herk.1: Ort": df_in["Herk.1: Ort"],
        "Bemerkungen [Geographie]": "", "Geographietyp": "", "Original_Geo": df_in["Original_Geo"]})
    # all these columns must be identical in order for it to be considered a duplicate
    drop_list = ["Herk.7: Subkontinent", "Herk.4: Grossregion/gr. Insel", "Herk.3: Gebiet/Unterregion/Kl. Insel",
                 "Herk.6: Land", "Departement/Provinz/Kanton", "Herk.1: Ort", "Kultur"]
    # drop the duplicates
    df_out.drop_duplicates(subset=drop_list, keep='first', inplace=True)
    # save the excel
    SE.save_df_excel(df_out, f"Schuster_Geo_Schlüssel_{today}")


#get_geo_schuster("Karten_Schuster_2022-03-10")


def fill_geo_ID(schuster: str, schuster_key: str) -> None:
    """
    From the Geo key fill the geo ID in the schuster Excel.
    :param schuster: Schuster excel
    :param schuster_key: Schuster geo key excel
    :return:
    """
    df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{schuster}.xlsx"))
    df_key = pd.read_excel(os.path.join(current_wdir, "input", f"{schuster_key}.xlsx"))
    # create a dict so that we can fill the Geo_ID according to the values in the column Original_Geo
    map_dict = dict(zip(df_key["Original_Geo"], df_key["Geo_ID"]))
    # map the df according to the key
    df_in["Geo_ID"] = df_in["Original_Geo"].map(map_dict)
    SE.save_df_excel(df_in, f"Schuster_Karten_{today}")


#fill_geo_ID("Schuster_Karten_2022-03-25", "Schuster_Geo_Schlüssel_2022-03-10")


def replace_transcript(schuster: str, schuster_key: str) -> None:
    df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{schuster}.xlsx"))
    df_key = pd.read_excel(os.path.join(current_wdir, "input", f"{schuster_key}.xlsx"))
    df_in.drop_duplicates(subset=["Original Geo Neu"], keep="first", inplace=True, ignore_index=True)
    df_in.dropna(subset=["Original Geo Neu"], inplace=True)
    replace_dict = dict(zip(df_in["Original_Geo"], df_in["Original Geo Neu"]))
    df_key["Original_Geo"].replace(to_replace=replace_dict, inplace=True)
    SE.save_df_excel(df_key, f"Schuster_Geo_Schlüssel_{today}")


#replace_transcript("Schuster_Karten_2022-03-25", "Schuster_Geo_Schlüssel_2022-03-10")


if __name__ == "__main__":
    pass
