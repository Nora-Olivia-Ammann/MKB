from os.path import dirname as up
import os
from datetime import date
import pandas as pd

today = str(date.today())
current_wdir = up(up(up(__file__)))

############################################


class ExcelFunctions:
    """
    This class contains only static functions that are employed imported like a module.
    """

    @staticmethod
    def in_excel_to_df(in_excel: str) -> pd.DataFrame:
        """
        Reads an excel from a designated folder.
        :param in_excel: str of the excel without the extension
        :return: df of that excel
        """
        return pd.read_excel(os.path.join(current_wdir, "input", f"{in_excel}.xlsx"))

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
    def doc_excel_to_df(abteilung: str) -> pd.DataFrame:
        """
        The documentation of the results is in another folder. That folder is hardcoded here.
        :param abteilung: The name of the current abteilung, it is part of the excel name.
        :return: df of that excel
        """
        return pd.read_excel(os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))

    @staticmethod
    def excel_save_doc(name_df: pd.DataFrame, abteilung: str) -> None:
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

    @staticmethod
    def save_doc_list(list_dict: list[dict], abteilung: str) -> None:
        """
        If a function generates several documentation lines, these will be saved in a list of dictionaries.
        From those a df will be created which then is concat with the existing documentation excel and saved.
        :param list_dict: list of dictionaries that contain new information
        :param abteilung: in order to read the correct doc excel
        :return: None
        """
        original_df = ExcelFunctions.doc_excel_to_df(abteilung)
        df_from_list = pd.DataFrame.from_records(list_dict)
        df_doc = pd.concat([original_df, df_from_list], ignore_index=True)
        ExcelFunctions.excel_save_doc(df_doc, abteilung)

    @staticmethod
    def save_doc_single(abteilung: str, doc_dict: dict) -> None:
        """
        Reads in the existing documentation, concats it with the new documentation, which is a single line and
        given as a dictionary and lastly saves it.
        :param abteilung: to read in the correct documentation excel
        :param doc_dict: dictionary to concat
        :return: None
        """
        df_doc = ExcelFunctions.doc_excel_to_df(abteilung)
        df_doc = pd.concat([df_doc, pd.DataFrame(doc_dict, index=[0])], ignore_index=True)
        ExcelFunctions.excel_save_doc(df_doc, abteilung)


if __name__ == "__main__":
    pass
