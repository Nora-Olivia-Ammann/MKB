import os
import warnings

import pandas as pd
import numpy as np
from datetime import date
import re

from excel_functions import ExcelFunctions as ExF


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

    # create_geo_key_excel("Test")

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
    def geo_key_completion(input_key_df: pd.DataFrame, drop_uncontrolled: bool, tranche: str or None = None,
                           abteilung: str or None = None) -> bool and pd.DataFrame or None:
        """
        There are not many columns that have to be filled for each Geo_ID, it checks those. A bool decides whether the
        uncontrolled rows should also be checked
        :param input_key_df: excel or df
        :param drop_uncontrolled: True if rows that have NaN in column "Kontrolliert" should be dropped
        :param tranche: name
        :param abteilung: name
        :return: True if all is complete or False and df with rows that miss values if not
        """
        warnings.warn("No double check for Geo_ID: must do")
        if drop_uncontrolled:
            # drop the uncontrolled rows, as the document is continuously worked on it may be complete for one tranche
            # even if other rows are not finished yet
            input_key_df.dropna(subset=["Kontrolliert"], inplace=True)
        # check whether any of the mandatory fields are empty
        if input_key_df[["Geo_ID", "Herk.9: Kontinent", "Herk.7: Subkontinent"]].isnull().any().any():
            # the the null rows
            df_nan = pd.concat([input_key_df[input_key_df["Herk.9: Kontinent"].isnull()],
                                input_key_df[input_key_df["Herk.7: Subkontinent"].isnull()],
                                input_key_df[input_key_df["Geo_ID"].isnull()]], ignore_index=True)
            # drop any duplicates
            df_nan.drop_duplicates(subset=["Geo_ID"], keep="first", inplace=True, ignore_index=True)
            # input_doc = pd.concat([input_doc, pd.DataFrame(
            #     {"Datum": today, "Tranche": tranche, "Input Dokument": "", "Schlüssel Excel": key_data,
            #      "Feld": "Angaben Geo", "Was": "Vollständigkeit Geografie",
            #      "Resultat": f"{len(df_nan)} unvollständige Geo_ID",
            #      "Output Dokument": f"Schlüssel_Geo_Fehlende_Angaben_{today}", "Ersetzt Hauptexcel": "-"},
            #     index=[0])], ignore_index=True)
            return False, df_nan
                # input_doc = pd.concat([input_doc, pd.DataFrame(
                #     {"Datum": today, "Tranche": tranche, "Input Dokument": "", "Schlüssel Excel": key_data,
                #      "Feld": "Angaben Geo", "Was": "Vollständigkeit Geografie",
                #      "Resultat": f"keine unvollständige Geo_ID",
                #      "Output Dokument": f"-", "Ersetzt Hauptexcel": "-"}, index=[0])], ignore_index=True)
                # ExF.save_doc_excel(input_doc, abteilung)
                # as it checkes only the completion of the keys it does not do any modifications we want to keep
                # therefore the df is not saved
                # when used in a function we want to have the df without the uncontrolled ID
        return True, None

    # geo_key_completion(key_data="_Test_Excel/d_Test_Schlüssel_Geo_Korrekt", is_excel=True, drop_uncontrolled=False,
    #                    tranche="Test", abteilung="Test")
    #
    # geo_key_completion(key_data="_Test_Excel/d_Test_Schlüssel_Geo_Fehler", is_excel=True, drop_uncontrolled=False,
    #                    tranche="Test",abteilung="Test")


if __name__ == "__main__":
    pass
