import os
import pandas as pd
from datetime import date

from tools.excel_functions import ExcelFunctions as ExF

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################

doc_list = []

#doc_list.append({"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "", "Feld": "", "Was": "", "Resultat": f"", "Output Dokument": f"", "Ersetzt Hauptexcel": ""})


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
    ExF.excel_save_doc(df, abteilung)


#create_documentation("Test")


def create_to_do() -> None:
    """
    Each new Excel that was generated, sets certain processes in motion. As one function may initiate several
    processes, this function creates an excel, in which the next steps are recorded.
    :return: None
    """
    df = pd.DataFrame(
        columns=["Erledigt", "Tranche", "Dokument", "Was", "Status", "Bemerkung"])
    ExF.excel_save_doc(df, "Nora_ToDo")


if __name__ == "__main__":
    pass
