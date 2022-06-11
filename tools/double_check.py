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
    def has_col_double(input_df: pd.DataFrame, col_name: str, tranche: str or None = None,
                       in_excel_name: str or None = None, write_doc: bool = False) -> \
            bool and None or pd.DataFrame and None or dict:
        # TODO: validate write description
        # clean the df
        input_df = Clean.strip_spaces_col(input_df, col_name)
        try:
            df_doubles = input_df[input_df[col_name].duplicated(keep=False)]  # returns df with all the doubles
        except KeyError:
            raise KeyError("Column doesn't exist.")
        if len(df_doubles) != 0:
            if write_doc:
                doc_dict = {"Datum": today,
                            "Tranche": tranche,
                            "Input Dokument": in_excel_name,
                            "Schlüssel Excel": "-",
                            "Feld": col_name,
                            "Was": "Dubletten",
                            "Resultat": f"{len(df_doubles)} dubletten",
                            "Output Dokument": f"-",
                            "Ersetzt Hauptexcel": "-"}
            else:
                doc_dict = None
            return True, df_doubles, doc_dict
        else:
            if write_doc:
                doc_dict = {"Datum": today,
                            "Tranche": tranche,
                            "Input Dokument": in_excel_name,
                            "Schlüssel Excel": "-",
                            "Feld": col_name,
                            "Was": "Dubletten",
                            "Resultat": f"Keine dubletten",
                            "Output Dokument": f"-",
                            "Ersetzt Hauptexcel": "-"}
            else:
                doc_dict = None
            return False, None, doc_dict

    @staticmethod
    def add_col_double_x(input_df: pd.DataFrame, col_name: str, tranche: str or None = None,
                         in_excel_name: str or None = None, write_doc: bool = False) \
            -> bool and pd.DataFrame and None or dict:
        # TODO: validate
        # TODO: write description
        # check if the column has double
        has_double, _, _ = DoubleCheck.has_col_double(input_df, col_name, tranche, in_excel_name, False)
        # if it has doubles add the column that documents it
        # no exception handling is necessary as that is done in the has_col_double
        if has_double:
            index = input_df.columns.get_loc(col_name)
            input_df.insert(loc=index+1, column=f"{col_name} Dublette",
                            value=input_df.duplicated(subset=col_name, keep=False))
            # replace all the True with 'x' and the False with np.nan
            input_df[f"{col_name} Dublette"].replace(to_replace={True: "x", False: np.nan}, inplace=True)
            if write_doc:
                doc_dict = {"Datum": today,
                            "Tranche": tranche,
                            "Input Dokument": in_excel_name,
                            "Schlüssel Excel": "-",
                            "Feld": f"{col_name}, {col_name} Dublette",
                            "Was": f"Hinzufügen von 'x' in '{col_name} Dublette'",
                            "Resultat": f"-",
                            "Output Dokument": f"-",
                            "Ersetzt Hauptexcel": "-"}
                # return df and doc list
                return input_df, doc_dict
            else:
                return input_df, None
        # if it doesn't have doubles
        else:
            if write_doc:
                doc_dict = {"Datum": today,
                            "Tranche": tranche,
                            "Input Dokument": in_excel_name,
                            "Schlüssel Excel": "-",
                            "Feld": f"{col_name}",
                            "Was": f"hat keine Dubletten",
                            "Resultat": f"-",
                            "Output Dokument": f"-",
                            "Ersetzt Hauptexcel": "-"}
                return input_df, doc_dict
            else:
                return input_df, None


if __name__ == "__main__":
    pass
