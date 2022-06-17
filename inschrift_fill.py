import os
import pandas as pd
from datetime import date

import warnings
from tools.custom_exceptions import *
from tools.inschrift_tranche import Inschrift as Insch
from tools.key_excel import KeyExcel as KE
from tools.excel_functions import ExcelFunctions as ExF

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


def einlauf_fill(in_excel: str, key_excel: str, tranche: str, abteilung: str) -> None:
    """
    Some of the Metadata for each object is based on its Einlauf. This function adds that data based on the Einlauf
    Key Excel which is an export excel from TMS. If that Excel is incomplete or keys are missing the function will not
    continue. Otherwise the Information will be added.
    """
    # read in_excel to df, which is the one to fill with values
    df_in = ExF.in_excel_to_df(in_excel)
    # read key_excel in which will provide the dictionary
    df_key = ExF.in_excel_to_df(key_excel)
    doc_list = []
    # check that all rows have an einlaufnummer
    if df_in["Inschrift"].isnull().any():
        # if not return a document that contains the null rows
        df_nan = df_in[df_in["Inschrift"].isnull()]
        ExF.save_df_excel(df_nan, f"{tranche}_{today}_Fehlende_Einlaufnummern")
        # write documentation
        ExF.save_doc_single(
            abteilung, {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel,
                        "Schlüssel Excel": key_excel,
                        "Feld": "Erwerbungsart, Objektstatus",
                        "Was": f"",
                        "Resultat": f"{len(df_nan)} Zeilen fehlten die Inschrift, Programm abgebrochen",
                        "Output Dokument": f"{tranche}_{today}_Fehlende_Einlaufnummern",
                        "Ersetzt Hauptexcel": "zusatz"})
        # error stop the function
        raise TrancheMissingValue("Not all row contain an Inschrift.")
    # check that the df key is completely filled:
    # TODO: revise
    outcome_key, df_nan = Insch.key_einlauf_completion_check(key_data=df_key, is_excel=False)
    if not outcome_key:
        ExF.save_df_excel(df_nan, f"Schlüssel_Einlauf_Fehlende_Angaben_{today}")
        # Write documentation
        doc_list.append({"Datum": today,
                         "Tranche": tranche,
                         "Input Dokument": in_excel,
                         "Schlüssel Excel": key_excel,
                         "Feld": f"Inschrift",
                         "Was": f"Vollständigkeit im Schlüssel Excel",
                         "Resultat": f"{len(df_nan)} fehlende Angaben im Schlüssel",
                         "Output Dokument": f"Schlüssel_Einlauf_Fehlende_Angaben_{today}",
                         "Ersetzt Hauptexcel": "-"})
        ExF.save_doc_list(doc_list, abteilung)
        # error stop the function
        raise KeyDocIncomplete("The Einlauf Key document is incomplete")
    # check whether all keys are present, in the key file, the Inschrift column is called Inventarnummer as it is a
    # TMS export, where the Einläufe are registered as a virtual object
    # we do not drop the uncontrolled as it does not exist in this file
    # TODO: revise
    # TODO: drop uncontrolled check
    result_check, df_not_dict = KE.key_all_there(in_data=df_in, key_data=df_key,
                                                 drop_uncontrolled=False, is_excel=False, abteilung=df_doc)
    if not result_check:
        # drop the duplicates, we only need one example
        df_not_dict.drop_duplicates(subset=["Inschrift"], keep="first", inplace=True, ignore_index=True)
        # sort the values for easier reading
        df_not_dict.sort_values(by=["Inschrift"], ascending=True, inplace=True, na_position='last', ignore_index=True)
        # save the excel
        ExF.save_df_excel(df_not_dict, f"Schlüssel_Fehlende_Inschrift_{tranche}_{today}")
        # write documentation
        doc_list.append({"Datum": today,
                         "Tranche": tranche,
                         "Input Dokument": in_excel,
                         "Schlüssel Excel": key_excel,
                         "Feld": f"Inschrift",
                         "Was": f"Vollständigkeit im Schlüssel Excel",
                         "Resultat": f"{len(df_not_dict)} fehlende Schlüssel",
                         "Output Dokument": f"Schlüssel_Fehlende_Inschrift_{tranche}_{today}",
                         "Ersetzt Hauptexcel": "-"})
        ExF.save_doc_list(doc_list, abteilung)
        # raise Error
        raise MissingKey("Inschrift are missing in the key document.")
    df_key.dropna(subset=["Kontrolliert"], inplace=True)
    # fill the Erwerbungsart and Objektstatus if everything is ok
    dict_erwerb = dict(zip(df_key.Inventarnummer, df_key.Erwerbungsart))
    df_in["Erwerbungsart"] = df_in["Inschrift"].map(dict_erwerb)
    dict_objekt = dict(zip(df_key.Inventarnummer, df_key.Objektstatus))
    df_in["Objektstatus"] = df_in["Inschrift"].map(dict_objekt)
    # save the filled df to a new excel
    ExF.save_df_excel(df_in, f"{tranche}_{today}")
    # write documentation
    doc_list.append({"Datum": today,
                     "Tranche": tranche,
                     "Input Dokument": in_excel,
                     "Schlüssel Excel": key_excel,
                     "Feld": "Erwerbungsart, Objektstatus",
                     "Was": f"Ergänzen gemäss Inschrift",
                     "Resultat": f"Excel ergänzt",
                     "Output Dokument": f"{tranche}_{today}",
                     "Ersetzt Hauptexcel": "ja"})
    ExF.save_doc_list(doc_list, abteilung)


if __name__ == '__main__':
    pass
