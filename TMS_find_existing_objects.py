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


def find_existing_objects(tranchen_excel: str, tms_excel: str, tranche: str, abteilung: str) -> None:
    df_tranche = pd.read_excel(os.path.join(current_wdir, "input", f"{tranchen_excel}.xlsx"))
    df_tms = pd.read_excel(os.path.join(current_wdir, "input", f"{tms_excel}.xlsx"))
    # read the documentation excel
    df_doc = pd.read_excel(
        os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))
    ##########################
    # convert the inventarnummer column from the tms df to a list
    tms_list = df_tms["Inventarnummer"].tolist()
    # making a dict from that list (it is significantly faster to search a dict, even including construction time)
    tms_dict = {}
    for inv in tms_list:
        tms_dict[inv] = inv
    # initiate two empty list to store the rows in
    in_tms_list = []
    not_tms_list = []
    # iterate over the tranche df
    for index, row in df_tranche.iterrows():
        # if the inventarnummer is in the list, append to list
        if row["Inventarnummer"] in tms_dict:
            in_tms_list.append(row)
        # if it is not in the tms
        else:
            not_tms_list.append(row)
    # if the list has no entries, we only need the documentation, no new excel is needed (as it would be identical)
    if len(in_tms_list) == 0:
        df_doc = pd.concat([df_doc, pd.DataFrame(
            {"Datum": today, "Tranche": tranche, "Input Dokument": tranchen_excel, "Schlüssel Excel": "-",
             "Feld": "-", "Was": "Abgleich mit bereits im TMS vorhandenen Datensätzen",
             "Resultat": f"keine Daten sind bereits vorhanden.", "Output Dokument": f"-",
             "Ersetzt Hauptexcel": "kein neues excel"}, index=[0])], ignore_index=True)
        # save excel because the function stops
        SE.save_doc_excel(df_doc, abteilung)
        return
    else:
        doc_list = []
        # save the df
        df_in_tms = pd.DataFrame.from_records(in_tms_list)
        SE.save_df_excel(df_in_tms, f"{tranche}_im_TMS_vorhanden_{today}")
        # Write doc
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": tranchen_excel, "Schlüssel Excel": "-",
             "Feld": "-", "Was": "Abgleich mit bereits im TMS vorhandenen Datensätzen",
             "Resultat": f"{len(in_tms_list)} Daten sind bereits vorhanden.",
             "Output Dokument": f"{tranche}_im_TMS_vorhanden_{today}", "Ersetzt Hauptexcel": "unterteilt es"})
        # save the df
        df_not_tms = pd.DataFrame.from_records(not_tms_list)
        SE.save_df_excel(df_not_tms, f"{tranche}_nicht_im_TMS_vorhanden_{today}")
        # write doc
        doc_list.append(
            {"Datum": today, "Tranche": tranche, "Input Dokument": tranchen_excel, "Schlüssel Excel": "-",
             "Feld": "-", "Was": "Abgleich mit bereits im TMS vorhandenen Datensätzen",
             "Resultat": f"{len(not_tms_list)} Daten sind nicht vorhanden.",
             "Output Dokument": f"{tranche}_nicht_im_TMS_vorhanden_{today}", "Ersetzt Hauptexcel": "unterteilt es"})
    # save doc
    doc_tranche = pd.concat([df_doc, pd.DataFrame.from_records(doc_list)], ignore_index=True)
    SE.save_doc_excel(doc_tranche, abteilung)


# # with double entries
# find_existing_objects(tranchen_excel="l_Test_find_existing_objects_Tranche_mit_Überschneidung",
#                       tms_excel="l_Test_find_existing_objects_TMS_Export_Objects (Concise)",
#                       tranche="Test", abteilung="Test")

# # without double entries
# find_existing_objects(tranchen_excel="l_Test_find_existing_objects_Tranche_ohne_Überschneidung",
#                       tms_excel="l_Test_find_existing_objects_TMS_Export_Objects (Concise)",
#                       tranche="Test", abteilung="Test")


# find_existing_objects(tranchen_excel="Oz1-3_Inventarnummern", tms_excel="(F)Vabc_2022-03-10",
#                       tranche="Oz1-3", abteilung="Test")
