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
from tools.general_double_check import DoubleCheck as DOUBLE
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


def new_tranche_excel(in_excel: str, tranche: str, abteilung: str, prefix_unique_ID: str, return_sorted: bool = False,
                      has_second_header: bool = False) -> None:
    """
    Transfers the data from the Excel we get from the BSB to the excel that we use to work with.
    If any "Inventarnummer" or "Beschreibung" are missing it creates an additional document, because we would need to
    contact the BSB for that information.
    If the Einlaufnummer are missing the leading zeros it adds them.
    It filters out the number of the Schublade (which is the name of the folder for the picture) and adds that to a new
    column.
    Creates and adds a Unique_ID, by which a row can be definitively identified at all times.
    For roughly correct Inventarnummer it adds leading zeros in a new column so that it can be machine sortable.
    :param in_excel: excel from BSB
    :param tranche: name from the BSB
    :param abteilung: name
    :param prefix_unique_ID: must be different for each tranche! (e.g. first Tranche Ozeanien "Oz1")
    :param return_sorted: True if it should be sorted according to Inventarnummer
    :param has_second_header: if True, then it drops the first row of the df
    :return: None
    """
    # read in the excel with the data
    df_in = pd.read_excel(os.path.join(current_wdir, "input", "", f"{in_excel}.xlsx"))
    # clean the df
    df_in = Clean.strip_spaces(df_in)
    # read the documentation excel
    df_doc = pd.read_excel(
        os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))
    if has_second_header:
        # drop the first row as it is the second header, modifies memory of df (inplace)
        df_in.drop(index=df_in.index[0], axis=0, inplace=True)
        # display a message that the row was dropped
        warnings.warn("The first row was dropped as it was indicated to be a second header.")
    # drop all the rows that are only NaN
    df_in.dropna(axis=0, how='all', inplace=True)
    df_in.reset_index(inplace=True)  # reset the index
    # create a new df to transfer the information to
    df_out = pd.DataFrame(
        columns=["Inventarnummer", "Dublette", "Tranche", "Ordner Bild", "Bilddatei", "Ethniengruppe (Nation)",
                 "Datierung", "Geo_ID",
                 "Beschreibung", "P2 Aufgenommene Person", "Inschrift", "P1 Fotograf*in/Filmer*in",
                 "T1 früherer Titel / alte Bezeichnung", "T2 Werktitel / Name der Darstellung",
                 "Schubladen Beschriftung", "Inventar Sortierbar", "Bemerkung (betr. Bearbeitung)", "Unique_ID"])
    warnings.warn("Inventarnummer Dublette check hinzufügen")
    # in order for the contents of the column to be transferred one by one as we do not want to merge we need the
    # target df to have the same row numbers, this can be achieved through reindexing
    df_out = df_out.reindex(index=list(range(0, len(df_in.index))))
    # transfer the information to the correct new columns
    in_cols = ["Inventarnummer", "Abteilung", "Person oder Institution1", "Datierung", "Beschreibung", "Inschrift"]
    out_cols = ["Inventarnummer", "Schubladen Beschriftung", "P1 Fotograf*in/Filmer*in", "Datierung", "Beschreibung",
                "Inschrift"]
    for in_col, out_col in zip(in_cols, out_cols):
        df_out[out_col] = df_in[in_col]
    # assign the tranche name, this is relevant as at a later point different tranche will be merged, while the picture
    # will stay within the folder of the tranche
    df_out["Tranche"] = tranche
    # add leading zeros to the Einlaufnummer if not already present, and add a column to mark where the einlaufnummer
    # is missing or incorrect
    _, df_out = INSCH.einlaufnummer_bearbeiten(in_data=df_out, is_excel=False, tranche=tranche, abteilung=abteilung)
    # for easier use and later processing get the folder name from the Beschreibung for each row and place it in
    # the column, iterate over the columns
    for index, value in df_out["Beschreibung"].iteritems():
        # in case any Beschreibung are missing
        try:
            # extract the name of the folder and assign the folder name to the cell
            df_out.loc[index, "Ordner Bild"] = list(filter(lambda x: x.startswith('(F)'),
                                                           value.split()))[0].replace(',', '')
        # attribute in case it is empty, as float has not split
        except AttributeError:
            continue
    # add the sortierbare Inventarnummer
    df_out = INVNR.inventar_sortierbar(in_data=df_out, is_excel=False, tranche=None, return_sorted=return_sorted)
    # as at this stage the inventarnummer may change, there is no way to uniquely identify a row
    # therefore we create our own ID, by adding leading zeros we make this number sortable and thus preserve the
    # original order
    df_out = UID.add_unique_ID(in_data=df_out, is_excel=False, tranche=None, prefix_unique_ID=prefix_unique_ID)
    # check if Inventarnummer or Beschreibung are missing any values
    if df_out[["Inventarnummer", "Beschreibung"]].isnull().any().any():
        df_nan = df_out[df_out["Inventarnummer"].isnull()]
        df_nan = df_nan.append(df_out[df_out["Beschreibung"].isnull()], ignore_index=True)
        df_nan.drop_duplicates(subset=["Unique_ID"], keep="first", inplace=True, ignore_index=True)
        SE.save_df_excel(df_nan, f"{tranche}_{today}_BSB_Angaben_Fehlen")
        df_doc = pd.concat([df_doc, pd.DataFrame(
            {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "-",
             "Feld": "Gesamtes Dokument", "Was": "Transfer von Information in Excel für die Bearbeitung",
             "Resultat": f"{len(df_nan)} Beschreibung/Inventarnummer fehlen, Zeilen auf Hauptexcel erhalten.",
             "Output Dokument": f"{tranche}_{today}_BSB_Angaben_Fehlen", "Ersetzt Hauptexcel": "neu"}, index=[0])],
                           ignore_index=True)
    # save the df
    SE.save_df_excel(df_out, f"{tranche}_Komplett_{today}")
    # write documentation
    df_doc = pd.concat([df_doc, pd.DataFrame(
        {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "-",
         "Feld": "Gesamtes Dokument", "Was": "Transfer von Information in Excel für die Bearbeitung",
         "Resultat": f"Unique_ID: {df_out.iloc[0, 15]} - {df_out.iloc[-1, 15]}",
         "Output Dokument": f"{tranche}_{today}_Komplett", "Ersetzt Hauptexcel": "neu"}, index=[0])], ignore_index=True)
    SE.save_doc_excel(df_doc, abteilung)


# # This will produce two excel one which all the data and one with rows that are missing some data
# new_tranche_excel(in_excel="a_Test_new_tranche_excel_Fehler", tranche="Test",
#                   abteilung="Test", prefix_unique_ID="T", return_sorted=False, has_second_header=True)
#
# # Here all the data there
# new_tranche_excel(in_excel="a_Test_new_tranche_excel_Korrekt", tranche="Test",
#                   abteilung="Test", prefix_unique_ID="T", return_sorted=False, has_second_header=True)


if __name__ == '__main__':
    pass