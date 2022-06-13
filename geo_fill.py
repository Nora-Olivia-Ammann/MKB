import os
import pandas as pd
from datetime import date

import warnings
from tools.cleaning_df import CleanDF as Clean
from tools.custom_exceptions import *
from tools.geographie import Geographie as Geo
from tools.key_excel import KeyExcel as KE
from tools.excel_functions import ExcelFunctions as ExF
from tools.NaN_check import NaN

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()


def fill_geo(in_excel: str, key_excel: str, tranche: str, abteilung: str) -> None:
    """
    After checking whether the geo key data is complete and all geo_ID that are in the tranche are also in the key.
    It fills the Columns for the geo information in the tranche excel. If the key document has problems it will stop
    the function.
    """
    # todo: validate
    # TODO write description
    # read in_excel to df, which is the one to fill with values
    df_in = ExF.in_excel_to_df(in_excel)
    # clean the df
    df_in = Clean.strip_spaces_col(df_in, "Geo_ID")
    # read key_excel which will provide the dictionary
    df_key = ExF.in_excel_to_df(key_excel)
    # clean the df, we don't want any spaces in the whole df
    df_key = Clean.strip_spaces_whole_df(df_key)
    doc_list = []
    # check whether all rows of the tranche excel have a GeoID
    has_geo_id_nan, nan_df, doc_dict = NaN.has_columns_nan(df_in, "Geo_ID")
    if has_geo_id_nan:
        output_name = f"{tranche}_{today}_fehlende_Geo_ID"
        ExF.save_df_excel(nan_df, output_name)
        doc_dict.update(
            {"Tranche": tranche,
             "Input Dokument": in_excel,
             "Schlüssel Excel": key_excel,
             "Output Dokument": output_name})
        ExF.save_doc_single(abteilung, doc_dict)
        raise TrancheMissingValue("Not all rows have a Geo_ID")
    else:
        # write the documentation that all is ok
        doc_list.append(doc_dict.update(
            {"Tranche": tranche,
             "Input Dokument": in_excel,
             "Schlüssel Excel": key_excel}))
    # check if the Geo key is complete
    # here we have to assign several variables, as it returns a df in any case, if there are values missing
    # it returns a nan_df otherwise it returns the checked df that has the default values filled in
    geo_bad, df_bad, doc_dict = Geo.geo_key_completion(df_key)
    if geo_bad:
        output_name = f"{abteilung}_Geo_Schlüssel_{today}_Angaben_Fehlen"
        ExF.save_df_excel(df_bad, output_name)
        doc_list.append(doc_dict.update(
            {"Tranche": tranche,
             "Input Dokument": in_excel,
             "Schlüssel Excel": key_excel,
             "Output Dokument": output_name}))
        ExF.save_doc_list(doc_list, abteilung)
        raise KeyDocIncomplete("Not all mandatory fields are filled.")
    # check if all the Geo_ID are in the Key document
    key_all_there_dropped, bad_df_dropped, problem_dropped, doc_dict_dropped = KE.key_check(df_in, df_key, "Geo_ID")
    if not key_all_there_dropped:
        # check if the Geo_ID is also missing from the df that contains the unchecked Geo_IDs
        key_all_there_undropped, bad_df_undropped, problem_undropped, doc_dict_undropped = \
            KE.key_check(df_in, df_key, "Geo_ID", False)
        if not key_all_there_undropped:
            # we save the undropped one as it may contain more problems
            output_name = f"{abteilung}_Geo_Schlüssel_{today}_{problem_undropped}"
            ExF.save_df_excel(bad_df_undropped, output_name)
            doc_list.append(doc_dict_undropped.update(
                {"Tranche": tranche,
                 "Input Dokument": in_excel,
                 "Schlüssel Excel": key_excel,
                 "Output Dokument": output_name}))
            ExF.save_doc_list(doc_list, abteilung)
            # raise Error
            raise MissingKey(f"{problem_undropped} with the Key Excel.")
        # if the unchecked contains all the geo_ID we want to differentiate that in the documentation
        else:
            output_name = f"{abteilung}_Geo_Schlüssel_{today}_{problem_dropped}"
            ExF.save_df_excel(bad_df_dropped, output_name)
            doc_list.append(doc_dict_dropped.update(
                {"Tranche": tranche,
                 "Input Dokument": in_excel,
                 "Schlüssel Excel": key_excel,
                 "Output Dokument": output_name}))
            ExF.save_doc_list(doc_list, abteilung)
            # raise Error
            raise MissingKey(f"{problem_undropped} with the Key Excel.")
    df_key.dropna(subset=["Kontrolliert"], inplace=True)
    # fill the Geografiety with the default if not otherwise specified
    df_key['Geographietyp'] = df_key['Geographietyp'].fillna("Herkunft geografisch")
    # It automatically creates the columns in the in_df
    geo_col_list = ["Herk.9: Kontinent", "Herk.6: Land", "Departement/Provinz/Kanton", "Distrikt", "Herk.1: Ort",
                    "Bezirk/Gemeinde", "Herk.2: Landschaft/Fluss", "Herk. 8: Politische Region",
                    "Herk.7: Subkontinent", "Inselgruppe", "Insel", "Herk.4: Grossregion/gr. Insel",
                    "Herk.3: Gebiet/Unterregion/Kl. Insel", "Bemerkungen [Geographie]", "Geographietyp"]
    for col in geo_col_list:
        geo_dic = dict(zip(df_key["Geo_ID"], df_key[col]))
        df_in[col] = df_in["Geo_ID"].map(geo_dic)
    output_name = f"{tranche}_{today}"
    ExF.save_df_excel(df_in, output_name)
    # write documentation
    doc_list.append({"Datum": today,
                     "Tranche": tranche,
                     "Input Dokument": in_excel,
                     "Schlüssel Excel": key_excel,
                     "Feld": "Geo_ID",
                     "Was": "Ausfüllen Geografie",
                     "Resultat": f"Geografie wurde gemäss Schlüssel ausgefüllt",
                     "Output Dokument": output_name,
                     "Ersetzt Hauptexcel": "ja"})
    ExF.save_doc_list(doc_list, abteilung)


if __name__ == '__main__':
    pass
