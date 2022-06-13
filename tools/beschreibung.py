import pandas as pd
import os
import numpy as np
from datetime import date

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()


class Beschreibung:

    @staticmethod
    def add_str_to_beschreibung(input_df: pd.DataFrame, in_excel_name: str, source_col: str, prefix_text: str,
                                tranche: str or None = None) -> pd.DataFrame and dict:
        """
        Adds the value from one column to the Beschreibung column.
        :param in_data: excel
        :param is_excel: True: if it is excel
        :param abteilung: name
        :param tranche: name
        :param source_col: Value that should be added to Beschreibung
        :param prefix_text: if not Prefix is wished then write "", otherwise a set Prefix (e.g. "Photo: ")
        :return: if not excel: df
        """
        # iterate over the rows
        for index, source_val in input_df[source_col].iteritems():
            # if this is not done this way but with try and except to cach the errors of the NaN, it adds the 'nan' as a
            # string to the beschreibung. Therefore it will only be done if it is indeed of type string
            if type(source_val) == str:
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
            # skip the row if it contains NaN
        doc_dict = {"Datum": today,
                    "Tranche": tranche,
                    "Input Dokument": in_excel_name,
                    "Schlüssel Excel": "",
                    "Feld": "Beschreibung",
                    "Was": "Information ergänzen.",
                    "Resultat": f"Info von Spalte: '{source_col}', zu Beschreibung mit Präfix: '{prefix_text}'",
                    "Output Dokument": f"",
                    "Ersetzt Hauptexcel": "ja"}
        return input_df, doc_dict

    @staticmethod
    def add_schublade(input_df: pd.DataFrame, tranche: str, in_excel_name: str) -> pd.DataFrame and dict:
        """
        Adds the name of the Schublade, to the Beschreibung after the number of the Schublade.
        :param input_df:
        :param abteilung: name or df_doc if not excel
        :return: df or None
        """
        for index, row in input_df.iterrows():
            besch_spl = row["Beschreibung"].split(",")
            try:
                index_res = [ind for ind, word in enumerate(besch_spl) if word.startswith("(F)")][0]
            # in some cases a blank space precedes the (F) which leads to an IndexError
            except IndexError:
                index_res = [ind for ind, word in enumerate(besch_spl) if word.startswith(" (F)")][0]
            try:
                besch_spl.insert(index_res + 1, row["Schubladen Beschriftung"])
                input_df.loc[index, "Beschreibung"] = ",".join(besch_spl)
            except TypeError:
                pass
        doc_dict = {"Datum": today,
                    "Tranche": tranche,
                    "Input Dokument": in_excel_name,
                    "Schlüssel Excel": "-",
                    "Feld": "Beschreibung",
                    "Was": "Hinzufügen Schubladenname",
                    "Resultat": f"erfolgreich hinzugefügt",
                    "Output Dokument": np.nan,
                    "Ersetzt Hauptexcel": "ja"}
        return input_df, doc_dict


if __name__ == "__main__":
    pass
