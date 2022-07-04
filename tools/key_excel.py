import os
from datetime import date

import numpy as np
import pandas as pd

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


# TODO: validate
# Todo: write description


class KeyExcel:

    @staticmethod
    def key_all_there(input_df: pd.DataFrame, input_key_df: pd.DataFrame, key_col: str, tranche: str, in_excel_name: str,
                      key_excel_name: str, drop_uncontrolled: bool = True) \
            -> bool and pd.DataFrame or None and dict:
        # drop the uncontrolled rows
        if drop_uncontrolled:
            input_key_df.dropna(subset=["Kontrolliert"], inplace=True)
        # if not double keys exist
        # create a filter the shows false if the key is not in the in_col
        all_isin = input_df[key_col].isin(input_key_df[key_col])
        # if not all keys are there
        if not all_isin.all():
            # get the keys that are not in the key excel
            df_not_dict = input_df[all_isin == False]
            # drops all the duplicates from the col subset, keeps first instance, resets index, and overwrites df
            df_not_dict.drop_duplicates(subset=[key_col], keep="first", inplace=True, ignore_index=True)
            # sort the values
            df_not_dict.sort_values(by=[key_col], ascending=True, inplace=True, na_position='first', ignore_index=True)
            # write the documentation
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": key_excel_name,
                        "Feld": key_col,
                        "Was": f"Schlüssel vorhanden",
                        "Resultat": f"{len(df_not_dict)} Schlüssel nicht vorhanden.",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "nein"}
            # return the result
            return False, df_not_dict, doc_dict
        # else if all the keys are present
        # write the documentation
        doc_dict = {"Datum": today,
                    "Tranche": tranche,
                    "Input Dokument": in_excel_name,
                    "Schlüssel Excel": key_excel_name,
                    "Feld": key_col,
                    "Was": f"Schlüssel vorhanden",
                    "Resultat": f"Alle Schlüssel sind vorhanden.",
                    "Output Dokument": np.nan,
                    "Ersetzt Hauptexcel": "nein"}
        # return the results
        return True, None, doc_dict


if __name__ == "__main__":
    pass
