import os
import pandas as pd
import numpy as np
from datetime import date

from tools.excel_functions import ExcelFunctions as ExF

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
    ExF.save_df_excel(df, "TMS_Löschen_Dokumentation")


# create_tms_delete_doc()

def tms_inventarnummer_delete(in_excel: str, inventarnummer: str) -> None:
    """
    Filters the Inventarnummer from a TMS export excel, that have too little information to be of use and should be
    deleted.
    :param in_excel: TMS Export Excel, usually one excel for one roman numeral (e.g. (F)Vb)
    :param inventarnummer: roman number of the Inventarnummer (e.g. (F)Vb if there are several with suffix)
    :return: None
    """
    # read the excel
    df_in = ExF.in_excel_to_df(in_excel)
    doc_list = []
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
        ExF.save_df_excel(df_out, f"{inventarnummer}_zu_Löschen_{today}")
        ExF.doc_save_single("TMS_Löschen_Dokumentation",
                            {"Datum": today, "Inventarnummer": inventarnummer, "Input Dokument": in_excel,
                             "Resultat": f"{len(df_out)} Inventarnummern zu Löschen",
                             "Output Dokument": f"{inventarnummer}_zu_Löschen_{today}"})
    else:
        ExF.doc_save_single("TMS_Löschen_Dokumentation",
                            {"Datum": today, "Inventarnummer": inventarnummer, "Input Dokument": in_excel,
                             "Resultat": "Keine leeren Inventarnummern", "Output Dokument": "-"})

# tms_inventarnummer_delete("III_2022-03-10", "(F)III")
