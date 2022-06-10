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

#df_doc = pd.concat([df_doc, pd.DataFrame({"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "", "Feld": "", "Was": "", "Resultat": f"", "Output Dokument": f"", "Ersetzt Hauptexcel": ""}, index=[0])], ignore_index=True)

#df_doc = pd.concat([df_doc, pd.DataFrame({}, index=[0])], ignore_index=True)


def create_documentation(abteilung: str) -> None:
    """
    For each Abteilung, a documentation Excel is created. Whenever a function is run, a documentation of what was
    detected and what new Excel files resulted from that function will be recorded in this file. This function saves
    an Excel document.
    :param abteilung: Abteilungsname
    :return: None
    """
    df = pd.DataFrame(columns=["Datum", "Tranche", "Input Dokument", "Schlüssel Excel", "Feld", "Was", "Resultat",
                               "Output Dokument", "Ersetzt Hauptexcel"])
    SE.save_doc_excel(df, abteilung)


#create_documentation("Test")


def append_doc(abteilung: str, tranche: str, in_excel: str) -> None:
    df_doc = pd.read_excel(os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))
    df_doc = pd.concat([df_doc, pd.DataFrame(
        {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "", "Feld": "", "Was": "",
         "Resultat": f"", "Output Dokument": f"", "Ersetzt Hauptexcel": ""}, index=[0])], ignore_index=True)
    SE.save_doc_excel(df_doc, abteilung)


#append_doc("Test", "Test", "Test")


def create_to_do() -> None:
    """
    Each new Excel that was generated, sets certain processes in motion. As one function may initiate several
    processes, this function creates an excel, in which the next steps are recorded.
    :return: None
    """
    df = pd.DataFrame(
        columns=["Erledigt", "Tranche", "Dokument", "Was", "Status", "Bemerkung"])
    SE.save_doc_excel(df, "Nora_ToDo")


if __name__ == "__main__":
    pass
