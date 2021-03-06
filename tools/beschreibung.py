import warnings
from datetime import date

import numpy as np
import pandas as pd

today = str(date.today())


class Beschreibung:

    @staticmethod
    def add_str_to_beschreibung(input_df: pd.DataFrame, in_excel_name: str, source_col: str, prefix_text: str,
                                tranche: str) -> pd.DataFrame and dict:
        """
        This only works if the Beschreibung is enclosed in curly brackets { }
        Test_Excel: Test_add_str_to_beschreibung
        :param input_df: Tranchen Excel df
        :param in_excel_name: Name of the Excel (in_excel of the enclosing function)
        :param source_col: The string that should be added to the Beschreibung
        :param prefix_text:
        :param tranche:
        :return:
        """
        warnings.warn("Only works if the Beschreibung is enclosed in { }")
        # iterate over the rows
        for index, source_val in input_df[source_col].iteritems():
            # if this is not done this way but with try and except to cach the errors of the NaN, it adds the 'nan' as
            # a string to the beschreibung. Therefore it will only be done if it is indeed of type string
            # get the value in the Beschreibung
            besch_str = input_df["Beschreibung"][index]
            # check if they are a str, if they are empty they are not str
            if type(besch_str) == str:
                # partition at the bracket
                partitioned = list(besch_str.rpartition("}"))
                # this way no values that may come after the bracket will be lost
                # insert the information before the bracket
                partitioned.insert(1, f", {prefix_text}{source_val}")
                # join the items of the list and assign them into the Beschreibung
                input_df.loc[index, "Beschreibung"] = "".join(partitioned)
            # if the Beschreibung does not contain a string (NaN), just insert the value
            else:
                input_df.loc[index, "Beschreibung"] = f"{prefix_text}{source_val}"
        doc_dict = {"Datum": today,
                    "Tranche": tranche,
                    "Input Dokument": in_excel_name,
                    "Schl??ssel Excel": "",
                    "Feld": "Beschreibung",
                    "Was": "Information erg??nzen.",
                    "Resultat": f"Info von Spalte: '{source_col}', zu Beschreibung mit Pr??fix: '{prefix_text}'",
                    "Output Dokument": f"",
                    "Ersetzt Hauptexcel": "ja"}
        return input_df, doc_dict

    @staticmethod
    def add_schublade(input_df: pd.DataFrame, tranche: str, in_excel_name: str) -> pd.DataFrame and dict:
        """
        The Schublade Number is the same as the Number of the Ordner of the picture file. This is also added
        as additional metadata into the Beschreibung. In future Tranche this will not be necessary as we do not get
        the information as string in the Beschreibung but separately.
        :param input_df: df to modify
        :param tranche: Name of the Tranche
        :param in_excel_name: Name of the excel that provides the df
        :return: df and dictionary with documentation
        """
        for index, row in input_df.iterrows():
            besch_spl = row["Beschreibung"].split(",")
            try:
                index_res = [ind for ind, word in enumerate(besch_spl) if word.startswith("(F)")][0]
            # in some cases a blank space precedes the (F) which leads to an IndexError
            except IndexError:
                index_res = [ind for ind, word in enumerate(besch_spl) if word.startswith(" (F)")][0]
            try:
                # insert the Schubladen Info into the Beschreibung.
                besch_spl.insert(index_res + 1, row["Schubladen Beschriftung"])
                input_df.loc[index, "Beschreibung"] = ",".join(besch_spl)
            except TypeError:
                pass
        doc_dict = {"Datum": today,
                    "Tranche": tranche,
                    "Input Dokument": in_excel_name,
                    "Schl??ssel Excel": "-",
                    "Feld": "Beschreibung",
                    "Was": "Hinzuf??gen Schubladenname",
                    "Resultat": f"erfolgreich hinzugef??gt",
                    "Output Dokument": np.nan,
                    "Ersetzt Hauptexcel": "ja"}
        return input_df, doc_dict


if __name__ == "__main__":
    pass

    file_name = "Test_add_str_to_beschreibung"
    file_path = "_Test_Excel/" + file_name

    # in_df = ExF.in_excel_to_df(file_path)
    # out_df, dict_df = Beschreibung.add_str_to_beschreibung(
    #     in_df, in_excel_name="Test", source_col="Schubladen Beschriftung",
    #     prefix_text="Schublade: ", tranche="Test")


