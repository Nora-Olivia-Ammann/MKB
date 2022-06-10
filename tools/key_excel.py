import os
import warnings

import pandas as pd
import numpy as np
from datetime import date
import re

from save_excel import SaveExcel as SE

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class KeyExcel:

    @staticmethod
    def check_key_isin(in_data: str or pd.DataFrame, in_col: str, key_data: str or pd.DataFrame, key_col: str,
                       drop_uncontrolled: bool, is_excel: bool = False, tranche: str or None = None,
                       abteilung: str or None = None, out_excel: str or None = None) -> None or bool and pd.DataFrame:
        """
        This function checks whether the key excel contains all the keys that are in the tranchen excel. If not used
        as a nested function it also writes the documentation.
        :param in_data: tranche excel
        :param in_col: column name of the key
        :param key_data: key excel
        :param key_col: column name of the key (it may differ)
        :param drop_uncontrolled: True: drops all rows where 'Kontrolle' Column is empty
        :param is_excel: True: if it is excel
        :param tranche: name
        :param abteilung: name
        :param out_excel: name of the out excel
        :return: if is_excel False: Bool True if all keys are present or Bool False and a df with the missing keys
        """
        # some keys are too long to add to the excel name, therefore we have this additional parameter
        if is_excel:
            # read in_excel to df
            df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{in_data}.xlsx"))
            # read the documentation excel
            df_doc = pd.read_excel(
                os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))
            # read key_excel in which will provide the dictionary
            key_df = pd.read_excel(os.path.join(current_wdir, "input", f"{key_data}.xlsx"))
        else:
            df_in = in_data
            key_df = key_data
            df_doc = abteilung
        # drop the uncontrolled rows
        if drop_uncontrolled:
            key_df.dropna(subset=["Kontrolliert"], inplace=True)
        # TODO: checks for duplicate keys, return document with the keys and stop the function
        raise KeyError("Please write the code to check for duplicate keys.")
        # create a filter the shows false if the key is not in the in_col
        isin_filter = df_in[in_col].isin(key_df[key_col])
        # check if all are there
        if not isin_filter.all():
            # get all the rows with the missing key information
            df_not_dict = df_in[isin_filter == False]
            # we only need one example of the key
            # drops all the duplicates from the col subset, keeps first instance, resets index, and overwrites df
            df_not_dict.drop_duplicates(subset=[key_col], keep="first", inplace=True, ignore_index=True)
            # sort the values
            df_not_dict.sort_values(by=[key_col], ascending=True, inplace=True, na_position='first', ignore_index=True)
            if is_excel:
                # save the excel
                SE.save_df_excel(df_not_dict, f"Schlüssel_Fehlende_{out_excel}_{tranche}_{today}")
                # write documentation
                df_doc = pd.concat([df_doc, pd.DataFrame(
                    {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": key_data,
                     "Feld": f"{key_col}", "Was": f"Vollständigkeit im Schlüssel Excel, "
                                                  f"drop_uncontroled: {drop_uncontrolled}",
                     "Resultat": f"{len(df_not_dict)} fehlende Schlüssel",
                     "Output Dokument": f"Schlüssel_Fehlende_{out_excel}_{tranche}_{today}", "Ersetzt Hauptexcel": "-"},
                    index=[0])], ignore_index=True)
                SE.save_doc_excel(df_doc, abteilung)
            else:
                return False, df_not_dict
        else:
            if is_excel:
                # write documentation
                df_doc = pd.concat([df_doc, pd.DataFrame(
                    {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": key_data,
                     "Feld": f"{key_col}", "Was": f"Vollständigkeit im Schlüssel Excel, "
                                                  f"drop_uncontroled: {drop_uncontrolled}",
                     "Resultat": f"Keine fehlende Schlüssel", "Output Dokument": f"-", "Ersetzt Hauptexcel": "-"},
                    index=[0])], ignore_index=True)
                SE.save_doc_excel(df_doc, abteilung)
            else:
                return True, None


    # # MISSING KEYS
    # # here some keys that are in the Tranche Excel are missing in the key excel
    # check_key_isin(in_data="a_Test_check_key_isin_Tranche", in_col="Schlüssel_Info",
    #                key_data="a_Test_check_key_isin_Schlüssel_Fehlen", key_col="Schlüssel_Info", drop_uncontrolled=True,
    #                is_excel=True, tranche="Test", abteilung="Test", out_excel="Schlüssel_Info")
    #
    #
    # # KEYS UNCONTROLLED
    # # here the all the keys are in the key excel but they are not controlled, therfore treated as missing because
    # # the parameter drop_uncontrolled is true, therfore the keys will be labled as missing
    # check_key_isin(in_data="a_Test_check_key_isin_Tranche", in_col="Schlüssel_Info",
    #                key_data="a_Test_check_key_isin_Schlüssel_Korrekt_Unkontrolliert", key_col="Schlüssel_Info",
    #                drop_uncontrolled=True, is_excel=True, tranche="Test", abteilung="Test", out_excel="Schlüssel_Info")
    #
    # # this is the same as above, except that drop_uncontrolled is False, this will not return an excel
    # check_key_isin(in_data="a_Test_check_key_isin_Tranche", in_col="Schlüssel_Info",
    #                key_data="a_Test_check_key_isin_Schlüssel_Korrekt_Unkontrolliert", key_col="Schlüssel_Info",
    #                drop_uncontrolled=False, is_excel=True, tranche="Test", abteilung="Test", out_excel="Schlüssel_Info")
    #
    # # ALL CORRECT
    # # here everyting is correct, it will not return an excel
    # check_key_isin(in_data="a_Test_check_key_isin_Tranche", in_col="Schlüssel_Info",
    #                key_data="a_Test_check_key_isin_Schlüssel_Korrekt", key_col="Schlüssel_Info",
    #                drop_uncontrolled=True, is_excel=True, tranche="Test", abteilung="Test", out_excel="Schlüssel_Info")


if __name__ == "__main__":
    pass
