import os
import warnings

import pandas as pd
import numpy as np
from datetime import date
import re

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class SaveExcel:
    """
    This class contains only static functions that are employed imported like a module.
    """

    @staticmethod
    def save_df_excel(name_df: pd.DataFrame, name_excel: str) -> None:
        """
        Saves an excel of a given dataframe in the output folder.
        :param name_df: name of the dataframe
        :param name_excel: name of the outgoing excel without the .xlsx extension
        :return: None
        """
        writer = pd.ExcelWriter(os.path.join(current_wdir, "output", f"{name_excel}.xlsx"))
        name_df.to_excel(writer, sheet_name=" ", index=False)
        writer.save()

    @staticmethod
    def save_doc_excel(name_df: pd.DataFrame, abteilung: str) -> None:
        """
        Saves the documentation excel in the _documentation folder within the output folder.
        :param name_df: name of the dataframe
        :param abteilung: abteilung, which makes up the documentation name
        :return: None
        """
        writer = pd.ExcelWriter(
            os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))
        name_df.to_excel(writer, sheet_name=" ", index=False)
        writer.save()


if __name__ == "__main__":
    pass
