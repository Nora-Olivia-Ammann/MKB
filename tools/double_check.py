import os
import pandas as pd
from datetime import date
import numpy as np

from cleaning_df import CleanDF as Clean
from excel_functions import ExcelFunctions as ExF

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()


class DoubleCheck:

    @staticmethod
    def separate_double_col(input_df: pd.DataFrame, col_name: str, tranche: str, in_excel_name: str) \
            -> bool and None or pd.DataFrame and dict:
        # TODO: validate, write description
        # clean the df
        input_df = Clean.strip_spaces(input_df)
        try:
            if input_df[col_name].duplicated().any():
                # returns df with all the doubles
                df_doubles = input_df[input_df[col_name].duplicated(keep=False)]
                # drop all the doubles form the original df
                input_df.drop_duplicates(subset=[col_name], keep=False, inplace=True, ignore_index=True)
                doc_dict = {"Datum": today,
                            "Tranche": tranche,
                            "Input Dokument": in_excel_name,
                            "Schlüssel Excel": "-",
                            "Feld": col_name,
                            "Was": "Dubletten",
                            "Resultat": f"{len(df_doubles)} dubletten",
                            "Output Dokument": np.nan,
                            "Ersetzt Hauptexcel": ""}
                return True, input_df, df_doubles, doc_dict
            else:
                doc_dict = {"Datum": today,
                            "Tranche": tranche,
                            "Input Dokument": in_excel_name,
                            "Schlüssel Excel": "-",
                            "Feld": col_name,
                            "Was": "Dubletten",
                            "Resultat": f"Keine dubletten",
                            "Output Dokument": np.nan,
                            "Ersetzt Hauptexcel": "nein"}
                return False, None, None, doc_dict
        except KeyError:
            raise KeyError("Column doesn't exist.")

    @staticmethod
    def add_x_col_double(input_df: pd.DataFrame, col_name: str, tranche: str, in_excel_name: str) \
            -> bool and pd.DataFrame or None and dict:
        # TODO: validate
        # TODO: write description
        # clean the df, if the column doesn't exist we get a key error
        input_df = Clean.strip_spaces(input_df)
        try:
            # if it exists we check if it has duplicates
            if input_df[col_name].duplicated().any():
                # get the index of the column
                index = input_df.columns.get_loc(col_name)
                # add a column that adds bool for the nan
                # the in the value parameter we give that we want a bool of that column
                input_df.insert(loc=index+1, column=f"{col_name} Dublette",
                                value=input_df.duplicated(subset=col_name, keep=False))
                # replace all the True with 'x' and the False with np.nan
                input_df[f"{col_name} Dublette"].replace(to_replace={True: "x", False: np.nan}, inplace=True)
                doc_dict = {"Datum": today,
                            "Tranche": tranche,
                            "Input Dokument": in_excel_name,
                            "Schlüssel Excel": "-",
                            "Feld": f"{col_name}, {col_name} Dublette",
                            "Was": f"Hinzufügen von 'x' in '{col_name} Dublette'",
                            "Resultat": f"-",
                            "Output Dokument": np.nan,
                            "Ersetzt Hauptexcel": "ja"}
                # return df and doc list
                return True, input_df, doc_dict
            # if it doesn't have doubles
            else:
                doc_dict = {"Datum": today,
                            "Tranche": tranche,
                            "Input Dokument": in_excel_name,
                            "Schlüssel Excel": "-",
                            "Feld": f"{col_name}",
                            "Was": f"hat keine Dubletten",
                            "Resultat": f"-",
                            "Output Dokument": np.nan,
                            "Ersetzt Hauptexcel": "nein"}
                return False, None, doc_dict
        except KeyError:
            raise KeyError("Column doesn't exist.")


if __name__ == "__main__":
    pass
