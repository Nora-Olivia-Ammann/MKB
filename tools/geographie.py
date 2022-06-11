import os
import warnings

import pandas as pd
import numpy as np
from datetime import date
import re

from beschreibung import Beschreibung as Besch
from cleaning_df import CleanDF as Clean
from columns_to_string import ColumnsToStr as ColStr
from custom_exceptions import *
from double_check import DoubleCheck as Double
from excel_functions import ExcelFunctions as ExF
from inschrift_tranche import Inschrift as Insch
from inventarnummer import Inventarnummer as InvNr
from key_excel import KeyExcel as KE
from modify_excel import ModifyExcel as ModE
from NaN_check import NaN as NAN
from RegEx_patterns import RegExPattern as RePat
from TMS_inschrift import TMSEinlauf as TMSInsch
from unique_ID import UniqueID as UID

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
    def geo_key_completion(input_key_df: pd.DataFrame, key_excel_name: str, drop_uncontrolled: bool, write_dict: bool,
                           tranche: str or None = None, abteilung: str or None = None) \
            -> bool and pd.DataFrame or None:
        """
        There are not many columns that have to be filled for each Geo_ID, it checks those. A bool decides whether the
        uncontrolled rows should also be checked
        :param input_key_df: excel or df
        :param drop_uncontrolled: True if rows that have NaN in column "Kontrolliert" should be dropped
        :param tranche: name
        :param abteilung: name
        :return: True if all is complete or False and df with rows that miss values if not
        """
        # TODO validate
        # TODO rethink whether we want to stop the function here or not, because, if we stop it here, we may have a
        #  problem regarding the documentation that may be written if used as a nested function -> could do it with
        #  exception handling if we do it with bool we need to check it everytime, while with exception handling it is
        #  only if there is a problem, in that case it would be possible to do try: except: and then also write an
        #  a different or additional dict entry
        # check if the Key excel has any double Geo_ID this is not allowed as they must be unique.
        has_double, df_double, _ = Double.has_col_double(input_df=input_key_df, col_name="Geo_ID")
        # if it has doubles, save it and write the documentation
        if has_double:
            ExF.save_df_excel(df_double, f"Dubletten_{key_excel_name}_{today}")
            # if the function is stopped here, and it is used as a nested function we may want a different docuemntation
            if write_dict:
                ExF.doc_save_single(abteilung,
                                    {"Datum": today,
                                     "Tranche": tranche,
                                     "Input Dokument": key_excel_name,
                                     "Schlüssel Excel": key_excel_name,
                                     "Feld": "Geo_ID",
                                     "Was": "Dubletten bei der Geo_ID",
                                     "Resultat": f"Schlüssel hat {len(df_double)} Dubletten",
                                     "Output Dokument": f"Dubletten_{key_excel_name}_{today}",
                                     "Ersetzt Hauptexcel": "nein"})
            raise DoubleGeoIDError()
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
            # drop any duplicates, this because if one row has several missing fields, it would be added twice, we
            # only want one row for each Geo_ID
            df_nan.drop_duplicates(subset=["Geo_ID"], keep="first", inplace=True, ignore_index=True)
            ExF.save_df_excel(df_nan, f"Schlüssel_Geo_Fehlende_Angaben_{today}")
            if write_dict:
                ExF.doc_save_single(abteilung,
                                    {"Datum": today,
                                     "Tranche": tranche,
                                     "Input Dokument": "",
                                     "Schlüssel Excel": key_excel_name,
                                     "Feld": "Angaben Geo",
                                     "Was": "Vollständigkeit Geografie",
                                     "Resultat": f"{len(df_nan)} unvollständige Geo_ID",
                                     "Output Dokument": f"Schlüssel_Geo_Fehlende_Angaben_{today}",
                                     "Ersetzt Hauptexcel": "-"})
            raise KeyDocIncomplete("The Key document is missing some Values in the mandatory fields.")
        doc_dict = {"Datum": today,
                    "Tranche": tranche,
                    "Input Dokument": "",
                    "Schlüssel Excel": key_excel_name,
                    "Feld": "Angaben Geo",
                    "Was": "Vollständigkeit Geografie",
                    "Resultat": f"keine unvollständige Geo_ID",
                    "Output Dokument": f"-",
                    "Ersetzt Hauptexcel": "-"}
        return input_key_df, doc_dict

    # geo_key_completion(key_data="_Test_Excel/d_Test_Schlüssel_Geo_Korrekt", is_excel=True, drop_uncontrolled=False,
    #                    tranche="Test", abteilung="Test")
    #
    # geo_key_completion(key_data="_Test_Excel/d_Test_Schlüssel_Geo_Fehler", is_excel=True, drop_uncontrolled=False,
    #                    tranche="Test",abteilung="Test")


if __name__ == "__main__":
    pass
