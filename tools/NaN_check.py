import os
import re
from datetime import date

import numpy as np
import pandas as pd

from cleaning_df import CleanDF as Clean

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

# this means that all empty strings (eg. "") are also considered nan
pd.options.mode.use_inf_as_na = True


class NaN:

    @staticmethod
    def separate_nan_col(input_df: pd.DataFrame, column: str, tranche: str, in_excel_name: str) \
            -> bool and pd.DataFrame or None and dict:
        # todo write description
        # todo validate
        if input_df[column].isnull.any():
            df_nan = input_df[input_df[column].isnull()]
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "-",
                        "Feld": column,
                        "Was": "Vollständigkeit",
                        "Resultat": f"Bei {len(df_nan)} Zeilen fehlen Angaben",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "zusatz"}
            return True, df_nan, doc_dict
        else:
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "-",
                        "Feld": column,
                        "Was": "Vollständigkeit",
                        "Resultat": f"Keine Angaben fehlen",
                        "Output Dokument": f"-",
                        "Ersetzt Hauptexcel": "-"}
            return False, None, doc_dict

    @staticmethod
    def add_x_nan_col(input_df: pd.DataFrame, column: str, tranche: str, in_excel_name: str) \
            -> bool and pd.DataFrame or None and dict:
        # todo write description
        # todo validate
        # this RegEx is true for all columns that are empty (but not nan) or only contains spaces
        # * stands for zero or more of the \s
        empty_re = re.compile(r"^\s*$")
        # iterate over the columns to replace them with nan if they are only blank
        for index, value in input_df[column].iteritems():
            # try to match it
            try:
                if empty_re.match(value):
                    # if it matches replace with nan
                    input_df.loc[index, column] = np.nan
            # as RegEx only works with str, it throws a TypeError if a value is nan
            except TypeError:
                continue
        # check if any values are nan
        if input_df[column].isnull().values.any():
            # get the index of the column
            index = input_df.columns.get_loc(column)
            # add a column that adds bool for the nan
            # the in the value parameter we give that we want a bool of that column
            input_df.insert(loc=index + 1, column=f"{column} Leer",
                            value=input_df[column].isnull())
            # replace all the True with 'x' and the False with np.nan
            input_df[f"{column} Leer"].replace(to_replace={True: "x", False: np.nan}, inplace=True)
            # write the documentation
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "-",
                        "Feld": f"{column}, {column} Leer",
                        "Was": f"Hinzufügen von 'x' in '{column} Leer'",
                        "Resultat": f"-",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "ja"}
            # return df and doc list
            return True, input_df, doc_dict
        # if it doesn't have nan
        else:
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "-",
                        "Feld": f"{column}",
                        "Was": f"hat keine Leeren Felder",
                        "Resultat": f"-",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "nein"}
            return False, None, doc_dict


if __name__ == "__main__":
    pass

    df = pd.DataFrame(
        {"Col1": [np.nan, "C1_R1", "    ", "", np.nan], "Col2": ["C2_R1", "C2_R2", "C2_R3", "C2_R4", "C2_R5"],
         "Col3": ["C3_R1", "C3_R2", "C3_R3", "C3_R4", "C3_R5"], "Col4": ["C4_R1", "C4_R2", "C4_R3", "C4_R4", "C4_R5"],
         "Col5": ["C5_R1", "C5_R2", "C5_R3", "C5_R4", "C5_R5"]})

    NaN.add_x_nan_col(df, "Col1", "", "")
