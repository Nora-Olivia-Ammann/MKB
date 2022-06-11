import os
import warnings

import pandas as pd
import numpy as np
from datetime import date
import re

from excel_functions import ExcelFunctions as ExF

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class TMSEinlauf:

    @staticmethod
    def key_einlauf_completion_check(input_key_df: pd.DataFrame, key_excel_name: str, in_excel_name: str,
                                     tranche: str) -> (bool and pd.DataFrame and dict) or (bool, None, dict):
        """
        Checks whether all the mandatory information in the Excel from the TMS export is there.
        If used as a nested function it returns True if all is correct.
        :param input_key_df: Dataframe that is to be checked
        :return: True if all is good, False if values are missing and df with rows that miss values.
        """
        # none of these should be empty
        if input_key_df[["Erwerbungsart", "Objektstatus"]].isnull().any().any():
            df_nan = input_key_df[input_key_df["Erwerbungsart"].isnull()]
            df_nan = pd.concat([df_nan, input_key_df[input_key_df["Objektstatus"].isnull()]], ignore_index=True)
            # sort out the duplicates and keep the first instance
            df_nan.drop_duplicates(subset="Inventarnummer", keep='first', inplace=True, ignore_index=False)
            df_nan.sort_values(by=["Inventarnummer"], ascending=True, inplace=True, ignore_index=True)
            doc_dict = {
                "Datum": today,
                "Tranche": tranche,
                "Input Dokument": in_excel_name,
                "Schlüssel Excel": key_excel_name,
                "Feld": "Erwerbungsart, Objektstatus",
                "Was": "Information vollständig.",
                "Resultat": f"Es fehlend bei {len(df_nan)} Inschriften Angaben.",
                "Output Dokument": f"Fehlen_Angaben_{key_excel_name}_{today}",
                "Ersetzt Hauptexcel": "-"}
            return False, df_nan, doc_dict
        else:
            doc_dict = {
                "Datum": today,
                "Tranche": tranche,
                "Input Dokument": in_excel_name,
                "Schlüssel Excel": key_excel_name,
                "Feld": "Erwerbungsart, Objektstatus",
                "Was": "Information vollständig.",
                "Resultat": f"Es fehlend keine Inschriften Angaben.",
                "Output Dokument": f"-",
                "Ersetzt Hauptexcel": "-"}
            return True, None, doc_dict

    # key_einlauf_completion_check(key_data="_Test_Excel/c_key_einlauf_completion_check_Korrekt", is_excel=True)
    # key_einlauf_completion_check(key_data="_Test_Excel/c_key_einlauf_completion_check_Fehler", is_excel=True)


if __name__ == "__main__":
    pass
