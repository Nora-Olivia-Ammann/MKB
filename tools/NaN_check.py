import os
from datetime import date
import pandas as pd

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()


class NaN:

    @staticmethod
    def has_columns_nan(input_df: pd.DataFrame, column: str) -> bool and pd.DataFrame or None and dict:
        # todo write description
        # todo validate
        if input_df[column].isnull.any():
            df_nan = input_df[input_df[column].isnull()]
            doc_dict = {"Datum": today,
                        "Tranche": "",
                        "Input Dokument": "",
                        "Schlüssel Excel": "",
                        "Feld": column,
                        "Was": "Vollständigkeit",
                        "Resultat": f"Bei {len(df_nan)} Zeilen fehlen Angaben",
                        "Output Dokument": f"",
                        "Ersetzt Hauptexcel": "zusatz"}
            return True, df_nan, doc_dict
        else:
            doc_dict = {"Datum": today,
                        "Tranche": "",
                        "Input Dokument": "",
                        "Schlüssel Excel": "",
                        "Feld": column,
                        "Was": "Vollständigkeit",
                        "Resultat": f"Keine Angaben fehlen",
                        "Output Dokument": f"-",
                        "Ersetzt Hauptexcel": "-"}
            return False, None, doc_dict


if __name__ == "__main__":
    pass
