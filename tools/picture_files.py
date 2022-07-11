import os
from datetime import date

import numpy as np
import pandas as pd

from mkb_code.tools.custom_exceptions import *
from mkb_code.tools.excel_functions import ExcelFunctions as ExF

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()


###############################


class PictureFiles:

    @staticmethod
    def add_old_picture_name(input_df: pd.DataFrame, tranche: str, in_excel_name: str) \
            -> pd.DataFrame and dict or None:
        """
        Adds the column where the old name of the picture file can be stored, if it already exists it raises an error.
        Test Excel: Test_inventarnummer_compliance_Fehler -> both col do not exist
        Test Excel: Test_picture_files_col_exists -> already exists we do not want to overwrite
        Test Excel: Test_picture_files_Bilddatei_Exists -> only col Bilddatei exists
        :param input_df: df that is modified
        :param tranche: name of tranche
        :param in_excel_name: name of excel
        :return: the df with the new column, documentation
        """
        # check if the column exists, we do not want to overwrite anything
        if "Bilddatei Alt" in input_df.columns:
            raise ColumnExistsError("The Column already exists.")
        try:
            index = input_df.columns.get_loc("Bilddatei")
        except KeyError:
            index = input_df.columns.get_loc("Inventarnummer")
            input_df.insert(index + 1, "Bilddatei", np.nan)
            index += 1
        # add the new column
        input_df.insert(index + 1, "Bilddatei Alt", np.nan)
        doc_dict = {"Datum": today,
                    "Tranche": tranche,
                    "Input Dokument": in_excel_name,
                    "Schlüssel Excel": "-",
                    "Feld": "Bilddatei Alt",
                    "Was": "hinzugefügt",
                    "Resultat": f"-",
                    "Output Dokument": np.nan,
                    "Ersetzt Hauptexcel": "ja"}
        return input_df, doc_dict


if __name__ == '__main__':
    pass

    file_name = "Test_picture_files_Bilddatei_Exists"
    file_path = os.path.join("_Test_Excel", file_name)
    df = ExF.in_excel_to_df(file_path)

    # function call
    out_df, doc = PictureFiles.add_old_picture_name(df, "Test", "Test")

    ExF.save_doc_single("Test", doc)
    ExF.save_df_excel(out_df, "Test")
