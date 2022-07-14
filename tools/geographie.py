import os
from datetime import date

import numpy as np
import pandas as pd

from mkb_code.tools.excel_functions import ExcelFunctions as ExF

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class Geographie:

    @staticmethod
    def create_geo_key_excel(abteilung: str):
        """
        For each Abteilung a new key excel for the geography will be created, as the geography may repeat itself in one
        Abteilung, but never across Abteilungen.
        :param abteilung: Name der Abteilung
        :return: None
        """
        df = pd.DataFrame(
            columns=["Kontrolliert", "Inventarnummer", "Ordner Bild", "Angabe Gemäss Excel BSB", "Geo_ID", "Kommentar",
                     "Herk.9: Kontinent", "Herk.7: Subkontinent", "Herk.6: Land", "Herk. 8: Politische Region",
                     "Herk.4: Grossregion/gr. Insel", "Inselgruppe", "Herk.3: Gebiet/Unterregion/Kl. Insel",
                     "Departement/Provinz/Kanton", "Distrikt", "Insel", "Herk.2: Landschaft/Fluss", "Bezirk/Gemeinde",
                     "Herk.1: Ort", "Bemerkungen [Geographie]", "Geographietyp"])
        ExF.save_df_excel(df, f"{abteilung}_Geo_Schlüssel")

    @staticmethod
    def geo_key_fill_geografietyp(input_key_df: pd.DataFrame):
        """
        Fills the column "Geographietyp" in the key excel with the default value.
        :param input_key_df: df geo key
        :return: key df
        """
        input_key_df['Geographietyp'] = input_key_df['Geographietyp'].fillna("Herkunft geografisch")
        return input_key_df

    @staticmethod
    def geo_key_completion(input_key_df: pd.DataFrame, tranche: str, in_excel_name: str,
                           drop_uncontrolled: bool = True) -> bool and pd.DataFrame or None and dict:
        """
        There are not many columns that have to be filled for each Geo_ID, it checks those. A bool decides whether the
        uncontrolled rows should also be checked
        """
        # TODO validate, write parameter description
        if drop_uncontrolled:
            # drop the uncontrolled rows, as the document is continuously worked on it may be complete for one tranche
            # even if other rows are not finished yet
            input_key_df.dropna(subset=["Kontrolliert"], inplace=True)
        # check whether any of the mandatory fields are empty
        if input_key_df[["Geo_ID", "Herk.9: Kontinent", "Herk.7: Subkontinent"]].isnull().any().any():
            # concat the df with null rows
            df_nan = pd.concat([input_key_df[input_key_df["Herk.9: Kontinent"].isnull()],
                                input_key_df[input_key_df["Herk.7: Subkontinent"].isnull()],
                                input_key_df[input_key_df["Geo_ID"].isnull()]], ignore_index=True)
            # If fields are missing drop any duplicates, this because if one row has several missing fields,
            # it would be added twice, we only want one row for each Geo_ID
            df_nan.drop_duplicates(subset=["Geo_ID"], keep="first", inplace=True, ignore_index=True)
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "",
                        "Feld": "Angaben Geo",
                        "Was": "Vollständigkeit Geografie",
                        "Resultat": f"{len(df_nan)} unvollständige Geo_ID",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "nein"}
            return False, df_nan, doc_dict
        else:
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schlüssel Excel": "",
                        "Feld": "Angaben Geo",
                        "Was": "Vollständigkeit Geografie",
                        "Resultat": f"Keine unvollständige Geo_ID",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "nein"}
            # return True as everyting is good, and no df as there aren't faulty entries
            return True, None, doc_dict


if __name__ == "__main__":
    pass
