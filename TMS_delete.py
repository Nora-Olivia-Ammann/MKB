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


def create_tms_delete_doc() -> None:
    """
    Some Fotokarteikarten already were digitised and extensively researched previously and therefore already exist.
    At some point a decision was made to create empty Inventarnummer in the TMS, the reasoning behind that was not sound
    as already existing Inventarnummer create a problem when importing new data.
    If certain fields are empty it is deemed little enough information so that they can be deleted. This creates a
    documentation to show which Inventarnummer has been checked for empty rows.
    :return: saves Excel
    """
    df = pd.DataFrame(columns=["Datum", "Inventarnummer", "Input Dokument", "Resultat", "Output Dokument"])
    SE.save_df_excel(df, "TMS_Löschen_Dokumentation")


#create_tms_delete_doc()


def tms_inventarnummer_delete(in_excel: str, inventarnummer: str) -> None:
    """
    Filters the Inventarnummer from a TMS export excel, that have too little information to be of use and should be
    deleted.
    :param in_excel: TMS Export Excel, usually one excel for one roman numeral (e.g. (F)Vb)
    :param inventarnummer: roman number of the Inventarnummer (e.g. (F)Vb if there are several with suffix)
    :return: None
    """
    # read the excel
    df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{in_excel}.xlsx"))
    # read the documentation excel
    df_doc = pd.read_excel(os.path.join(current_wdir, "output", "_dokumentation", "TMS_Löschen_Dokumentation.xlsx"))
    # drop the columns that are filled even in cases where there are no usable information in the system
    # by using inplace=True, changes are made in the df
    df_in.drop(columns=["Vom System vergebene Nr.", "Sortiernummer", "Objekt (Kurzbezeichnung)", "Bearbeitet von"],
               inplace=True)
    out_list = []
    # iterate over the rows
    for index, row in df_in.iterrows():
        # check if the row from column index 2 onwards are empty and the field of Medien is zero
        if row[["Material & Technik", "Maße", "Beschreibung", "Hersteller / Fotograf"]].isnull().all() \
                and row["Medien"] == 0:
            # append the rows, there is no inplace with append in df therefore we have to assign it again
            out_list.append(row)
    if len(out_list) != 0:
        df_out = pd.DataFrame.from_records(out_list)
        # add a column to mark the progress when deleting
        df_out.insert(0, "Gelöscht", np.nan)
        # we do not need this column
        df_out.pop("Medien")
        # save the df as an excel which will be used to delete the Inventarnummer in the system
        SE.save_df_excel(df_out, f"{inventarnummer}_zu_Löschen_{today}")
        df_doc = pd.concat([df_doc, pd.DataFrame(
            {"Datum": today, "Inventarnummer": inventarnummer, "Input Dokument": in_excel,
             "Resultat": f"{len(df_out)} Inventarnummern zu Löschen",
             "Output Dokument": f"{inventarnummer}_zu_Löschen_{today}"}, index=[0])], ignore_index=True)
    else:
        df_doc = pd.concat([df_doc, pd.DataFrame(
            {"Datum": today, "Inventarnummer": inventarnummer, "Input Dokument": in_excel,
             "Resultat": "Keine leeren Inventarnummern", "Output Dokument": "-"}, index=[0])], ignore_index=True)
    SE.save_doc_excel(df_doc, "TMS_Löschen")


#tms_inventarnummer_delete("III_2022-03-10", "(F)III")


