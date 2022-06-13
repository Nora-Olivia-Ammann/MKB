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


class UniqueID:

    @staticmethod
    def add_unique_id(input_df: pd.DataFrame, prefix_unique_id: str, in_excel_name: str,
                      tranche: str) -> pd.DataFrame or None:
        """
        Adds a new column if not existing to a df with a Unique_ID. If not Tranche will get the same prefix, then
        the ID will be unique amongst all Tranchen. This helps to difinitively identify a row.
        """
        if "Unique_ID" in input_df.columns:
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "-",
                        "Feld": "Unique_ID",
                        "Was": f"Spalte existiert bereits",
                        "Resultat": f"-",
                        "Output Dokument": f"-",
                        "Ersetzt Hauptexcel": "nein"}
            warnings.warn("Unique_ID existiert bereits.")
            return input_df, doc_dict
        # as at this stage the inventarnummer may change, there is no way to uniquely identify a row
        # therefore we create our own ID, by adding leading zeros we make this number sortable and thus preserve the
        # original order
        input_df["Unique_ID"] = input_df.index + 1
        input_df["Unique_ID"] = input_df["Unique_ID"].apply(lambda x: f"{prefix_unique_id}_{str(x).zfill(5)}")
        doc_dict = {"Datum": today,
                    "Tranche": tranche,
                    "Input Dokument": in_excel_name,
                    "Schlüssel Excel": "-",
                    "Feld": "Unique_ID",
                    "Was": f"Feld hinzugefügt und Unique_ID generiert mit Präfix: {prefix_unique_id}",
                    "Resultat": f"-",
                    "Output Dokument": np.nan,
                    "Ersetzt Hauptexcel": "ja"}
        return input_df, doc_dict


if __name__ == "__main__":
    pass
