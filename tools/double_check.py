import os
from datetime import date

import numpy as np
import pandas as pd

from sourcetree_code.tools.cleaning_df import CleanDF as Clean

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()


class DoubleCheck:

    @staticmethod
    def separate_double_col(input_df: pd.DataFrame, col_name: str, tranche: str, in_excel_name: str) \
            -> bool and None or pd.DataFrame and dict:
        """
        Checks if a column has doubles, if it does it generates a separate df with all the doubles and removes
        all the doubles from the original df.
        Test Excel: Test_inventarnummer_has_double -> with doubles
        Test Excel: Test_inventarnummer_has_no_double -> has no doubles
        :param input_df: df to check
        :param col_name: name of the column that should be checked
        :param tranche: name of the tranche
        :param in_excel_name: name of the excel that gave the df
        :return: true if double, original df without doubles, df with doubles, documentation OR False if no doubles, no
        df as nothing changed, documentation
        """
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
                            "Ersetzt Hauptexcel": "unterteilt es"}
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
        """
        Checks if a column has doubles, if it does, it adds a column that marks those with x, if it does not that column
        will be deleted.
        Test Excel: Test_double_add_x_has_col -> already has the column
        Test Excel: Test_inventarnummer_has_double -> with doubles
        Test Excel: Test_inventarnummer_has_no_double -> has no doubles
        :param input_df: df to check
        :param col_name: name of the column that should be checked
        :param tranche: name of the tranche
        :param in_excel_name: name of the excel that gave the df
        :return: true if double, original df documentation OR
            False if no doubles, no df as nothing changed, documentation
        """
        # clean the df, if the column doesn't exist we get a key error
        input_df = Clean.strip_spaces(input_df)
        try:
            # if it exists we check if it has duplicates
            if input_df[col_name].duplicated().any():
                # get the index of the column
                index = input_df.columns.get_loc(col_name)
                # add a column that adds bool for the nan
                # the in the value parameter we give that we want a bool of that column
                try:
                    input_df.insert(loc=index+1, column=f"{col_name} Dublette",
                                    value=input_df.duplicated(subset=col_name, keep=False))
                # if it already exists we get a value error, we want to overwrite it as doubles may have changed
                except ValueError:
                    input_df[f"{col_name} Dublette"] = input_df.duplicated(subset=col_name, keep=False)
                # replace all the True with 'x' and the False with np.nan
                input_df[f"{col_name} Dublette"].replace(to_replace={True: "x", False: np.nan}, inplace=True)
                doc_dict = {"Datum": today,
                            "Tranche": tranche,
                            "Input Dokument": in_excel_name,
                            "Schlüssel Excel": "-",
                            "Feld": f"{col_name}, {col_name} Dublette",
                            "Was": f"Hinzufügen von 'x' in '{col_name} Dublette'",
                            "Resultat": f"hat dubletten",
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
                            "Was": f"Dubletten",
                            "Resultat": f"hat keine Dubletten",
                            "Output Dokument": np.nan,
                            "Ersetzt Hauptexcel": "nein"}
                return False, None, doc_dict
        except KeyError:
            raise KeyError("Column doesn't exist.")


if __name__ == "__main__":
    pass

    # file_name = "Test_inventarnummer_has_no_double"
    # file_path = os.path.join("_Test_Excel", file_name)
    # df = ExF.in_excel_to_df(file_path)
    #
    # # function call
    # boo, out_df, doc = DoubleCheck.add_x_col_double(df, "Inventarnummer", "Test", "Test")
    #
    # print(boo)
    # ExF.save_doc_single("Test", doc)
    # if out_df is not None:
    #     ExF.save_df_excel(out_df, "Test")
