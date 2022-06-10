import os
import pandas as pd
import numpy as np
from datetime import date

import re
import warnings
from tools.beschreibung import Beschreibung as BE
from tools.cleaning_df import CleanDF as Clean
from tools.columns_to_string import ColumnsToStr as COLSTR
from tools.custom_exceptions import *
from tools.ethnie import Ethnie as ETHN
from tools.general_double_check import DoubleCheck as DOUBLE
from tools.geographie import Geographie as GEO
from tools.inschrift_einlaufnummer_tranche import Inschrift as INSCH
from tools.inventarnummer import Inventarnummer as INVNR
from tools.key_excel import KeyExcel as KE
from tools.modify_excel import ModifyExcel as MODEX
from tools.NaN_check import NaN as NAN
from tools.RegEx_patterns import RegExPattern as REPAT
from tools.save_excel import SaveExcel as SE
from tools.TMS_einlauf import TMSEinlauf as TMSEINL
from tools.unique_ID import UniqueID as UID


today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


def fill_geo(in_excel: str, key_excel: str, tranche: str, abteilung: str, continue_if_nan: bool = False) -> None:
    """
    After checking whether the geo key data is complete and all geo_ID that are in the tranche are also in the key.
    It fills the Columns for the geo information in the tranche excel. If the key document has problems it will stop
    the function.
    :param in_excel: tranche excel
    :param key_excel: key excel
    :param continue_if_nan: True: if any rows have NaN in column "Geo_ID" the function separates those but continues
                            to fill out the rest. False: will stop the function if NaN present
    :param tranche: name
    :param abteilung: name
    :return: None
    """
    # read in_excel to df, which is the one to fill with values
    df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{in_excel}.xlsx"))
    # clean the df
    df_in = Clean.strip_spaces(df_in)
    # read the documentation excel
    df_doc = pd.read_excel(os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))
    # read key_excel in which will provide the dictionary
    df_key = pd.read_excel(os.path.join(current_wdir, "input", "", f"{key_excel}.xlsx"))
    # clean the df
    df_key = Clean.strip_spaces(df_key)
    # check whether all rows have a GeoID
    if df_in["Geo_ID"].isnull().any():
        # if there are save them in a new df
        df_nan = df_in[df_in["Geo_ID"].isnull()]
        SE.save_df_excel(df_nan, f"{tranche}_{today}_Fehlende_GeoID")
        if not continue_if_nan:
            df_in.dropna(subset=["Geo_ID"], inplace=True)
            SE.save_df_excel(df_in, f"{tranche}_{today}_Vollständige_GeoID")
            # write documentation
            df_doc = pd.concat([df_doc, pd.DataFrame(
                {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "",
                 "Feld": "Geo_ID", "Was": "Vollständigkeit", "Resultat": f"{len(df_nan)} Geo_ID fehlen",
                 "Output Dokument": f"{tranche}_{today}_Fehlende_GeoID", "Ersetzt Hauptexcel": "zusatz"},
                index=[0])], ignore_index=True)
            SE.save_doc_excel(df_doc, abteilung)
            # raise Error
            raise TrancheMissingValue("Not all rows have a Geo_ID")
        else:
            # write documentation
            df_doc = pd.concat([df_doc, pd.DataFrame(
                {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "",
                 "Feld": "Geo_ID", "Was": "Vollständigkeit", "Resultat": f"{len(df_nan)} Geo_ID fehlen",
                 "Output Dokument": f"{tranche}_{today}_Fehlende_GeoID", "Ersetzt Hauptexcel": "unterteilt es"},
                index=[0])], ignore_index=True)
            df_in.dropna(subset=["Geo_ID"], inplace=True)
            warnings.warn("Some Geo_ID are missing, NaN document saved, function continued with non NaN df.")

    # check if the Geo key is complete
    # here we have to assign two variables, as it returns a df in any case, if there are values missing
    # it returns a nan_df otherwise it returns the checked df that has the default values filled in
    result_check, df_not_complete = GEO.geo_key_completion(
        key_data=df_key, is_excel=False, drop_uncontrolled=True, tranche=None, abteilung=df_doc)
    if not result_check:
        SE.save_df_excel(df_not_complete, f"Schlüssel_Geo_Fehlende_Angaben_{today}")
        df_doc = pd.concat([df_doc, pd.DataFrame(
            {"Datum": today, "Tranche": tranche, "Input Dokument": "", "Schlüssel Excel": key_excel,
             "Feld": "Angaben Geo", "Was": "Vollständigkeit Geografie",
             "Resultat": f"{len(df_not_complete)} unvollständige Geo_ID",
             "Output Dokument": f"Schlüssel_Geo_Fehlende_Angaben_{today}", "Ersetzt Hauptexcel": "-"},
            index=[0])], ignore_index=True)
        SE.save_doc_excel(df_doc, abteilung)
        # raise error
        raise KeyDocIncomplete("Not all mandatory fields in the key document are filled.")

    # check if all the Geo_ID are in the Key document
    result_isin_check, df_not_dict = KE.check_key_isin(
        in_data=df_in, in_col="Geo_ID", key_data=df_key, key_col="Geo_ID", drop_uncontrolled=True,
        out_excel=None, is_excel=False, tranche=None, abteilung=df_doc)
    if not result_isin_check:
        df_key = pd.read_excel(os.path.join(current_wdir, "input", "", f"{key_excel}.xlsx"))
        # check if the Geo_ID is also missing from the df that contains the unchecked Geo_IDs
        all_geo_isin, df_not_all_dict = KE.check_key_isin(
            in_data=df_in, in_col="Geo_ID", key_data=df_key, key_col="Geo_ID", drop_uncontrolled=False,
            out_excel=None, is_excel=False, tranche=None, abteilung=df_doc)
        if not all_geo_isin:
            SE.save_df_excel(df_not_all_dict, f"Schlüssel_Fehlende_Geo_ID_{tranche}_{today}")
            # write documentation
            df_doc = pd.concat([df_doc, pd.DataFrame(
                {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": key_excel,
                 "Feld": f"Geo_ID", "Was": f"Vollständigkeit im Schlüssel Excel",
                 "Resultat": f"{len(df_not_all_dict)} fehlende Schlüssel",
                 "Output Dokument": f"Schlüssel_Fehlende_Geo_ID_{tranche}_{today}", "Ersetzt Hauptexcel": "-"},
                index=[0])], ignore_index=True)
            SE.save_doc_excel(df_doc, abteilung)
            # raise Error
            raise MissingKey("Not all necessary Geo_ID are in the key document.")
        # if the unchecked contains all the geo_ID we want to differentiate that in the documentation
        else:
            SE.save_df_excel(df_not_dict, f"Schlüssel_Geo_Unkontrollierte_Angaben_{tranche}_{today}")
            df_doc = pd.concat([df_doc, pd.DataFrame(
                {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": key_excel,
                 "Feld": f"Geo_ID", "Was": f"Vollständigkeit im Schlüssel Excel",
                 "Resultat": f"{len(df_not_dict)} unkontrollierte, notwendige Geo_ID",
                 "Output Dokument": f"Schlüssel_Geo_Unkontrollierte_Angaben_{tranche}_{today}",
                 "Ersetzt Hauptexcel": "-"}, index=[0])], ignore_index=True)
            SE.save_doc_excel(df_doc, abteilung)
            raise MissingKey("Not all necessary Geo_ID were controlled.")
    df_key.dropna(subset=["Kontrolliert"], inplace=True)
    # fill the Geografiety with the default if not otherwise specified
    df_key['Geographietyp'] = df_key['Geographietyp'].fillna("Herkunft geografisch")
    # IF EVERYTHING IS OK FILL THE GEO COLUMNS
    # It automatically creates the columns in the in_df
    geo_col_list = ["Herk.9: Kontinent", "Herk.6: Land", "Departement/Provinz/Kanton", "Distrikt", "Herk.1: Ort",
                    "Bezirk/Gemeinde", "Herk.2: Landschaft/Fluss", "Herk. 8: Politische Region",
                    "Herk.7: Subkontinent", "Inselgruppe", "Insel", "Herk.4: Grossregion/gr. Insel",
                    "Herk.3: Gebiet/Unterregion/Kl. Insel", "Bemerkungen [Geographie]", "Geographietyp"]
    for col in geo_col_list:
        geo_dic = dict(zip(df_key["Geo_ID"], df_key[col]))
        df_in[col] = df_in["Geo_ID"].map(geo_dic)
    SE.save_df_excel(df_in, f"{tranche}_{today}")
    # write documentation
    df_doc = pd.concat([df_doc, pd.DataFrame(
        {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": key_excel, "Feld": "Geo_ID",
         "Was": "Ausfüllen Geografie", "Resultat": f"Geografie wurde gemäss Schlüssel ausgefüllt",
         "Output Dokument": f"{tranche}_{today}", "Ersetzt Hauptexcel": "ja"}, index=[0])], ignore_index=True)
    SE.save_doc_excel(df_doc, abteilung)


fill_geo("Metadaten_Test_Import", "Ozeanien_Geo_Schlüssel", continue_if_nan=True, tranche="Test", abteilung="Test")

# # ALL CORRECT
# fill_geo(in_excel="_Test_Excel/d_Test_Tranche_Geo_Auszufüllen_Komplett",
#          key_excel="_Test_Excel/d_Test_Schlüssel_Geo_Korrekt", continue_if_nan=False, tranche="Test", abteilung="Test")
#
# # GEO KEY HAS FAULTS
# # stops function, saves excel with the faulty keys
# fill_geo(in_excel="d_Test_Tranche_Geo_Auszufüllen_Komplett", key_excel="d_Test_Schlüssel_Geo_Fehler",
#          continue_if_nan=False, tranche="Test", abteilung="Test")
#
#
# # TRANCHE HAS MISSING GEO_ID
# # stops function, saves excel with missing
# fill_geo(in_excel="d_Test_Tranche_Geo_Auszufüllen_Fehlen", key_excel="d_Test_Schlüssel_Geo_Korrekt",
#          continue_if_nan=False, tranche="Test", abteilung="Test")


if __name__ == '__main__':
    pass