import os
import warnings

import pandas as pd
import numpy as np
from datetime import date
import re

from save_excel import SaveExcel as SE
from RegEx_patterns import RegExPattern as REPAT
from cleaning_df import CleanDF as Clean

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class Inventarnummer:

    @staticmethod
    def inventar_sortierbar(in_data: pd.DataFrame or str, return_sorted: bool, is_excel: bool = False,
                            tranche: str or None = None) -> pd.DataFrame or None:
        """
        Adds a new column with a sortable Inventarnummer. The correct one which we use in the TMS has no leading zeros,
        and cannot be sorted by excel or df correctly so that 2 follows 1 instead of 10. Because there may still be
        faulty Inventarnummer, of a format we may not be able to anticipate, we only add the zeros to ones that are
        roughly in the correct format. Once Inventarnummern have been corrected this program can be run again.
        :param in_data: excel or df
        :param is_excel: if it is an excel: True
        :param tranche: name
        :param return_sorted: if it should return sorted according to the inventarnummer: True
        :return: df or None
        """
        if is_excel:
            in_df = pd.read_excel(os.path.join(current_wdir, "input", f"{in_data}.xlsx"))
        else:
            in_df = in_data
        # clean the df
        in_df = Clean.strip_spaces(in_df)
        # overwrite the existing column with the new Inventarnummer
        in_df["Inventar Sortierbar"] = in_df["Inventarnummer"]
        # we only want to format roughly correct inventarnummer, as the true compliance check comes later
        # for the incorrect ones there is too much variation in the others to take them all into account,
        # therefore we will ignore those that do not fit
        pattern_no_letter, pattern_letter, pattern_letter_blank = REPAT.inventar_sortierbar_re_pattern()
        for index, value in in_df["Inventar Sortierbar"].iteritems():
            # exclude NaN cells
            # since it is very uncommon to have a missing Inventarnummer this is faster than checking if it is present
            try:
                # check if it is correct
                if pattern_no_letter.match(value) or pattern_letter_blank.match(value):
                    spl_val = value.split(" ")
                    spl_val[1] = spl_val[1].zfill(6)
                    joined = " ".join(spl_val)
                    in_df.loc[index, "Inventar Sortierbar"] = joined
                elif pattern_letter.match(value):
                    spl_val = value.split(" ")
                    spl_val[1] = spl_val[1].zfill(7)
                    joined = " ".join(spl_val)
                    in_df.loc[index, "Inventar Sortierbar"] = joined
            # skip the row if it is NaN
            except ValueError:
                continue
            except TypeError:
                continue
        # Sort the values if wished
        if return_sorted:
            in_df.sort_values(by=["Ordner Bild", "Inventar Sortierbar"], inplace=True, ignore_index=True)
        # if it is an excel we want an excel saved
        if is_excel:
            SE.save_df_excel(in_df, f"{tranche}_{today}")
        else:
            return in_df

    # inventar_sortierbar(indata="a_Test_inventar_sortierbar", is_excel=True, tranche="Test", return_sorted=False)

    @staticmethod
    def add_rename_inventarnummer(in_data: pd.DataFrame or str, return_sorted: bool, is_excel: bool = False,
                                  tranche: str or None = None) -> pd.DataFrame or None:
        """
        Adds columns to df, that are used when having to rename any Inventarnummer. Can be used as a nested function.
        :param in_data: df / excel
        :param is_excel: True if Excel
        :param return_sorted: True if it should be sorted according to Inventar Sortierbar
        :param tranche: name
        :return: df / None
        """
        if is_excel:
            df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{in_data}.xlsx"))
        else:
            df_in = in_data
        # rename the column with the old inventarnummer
        df_in.rename(columns={"Inventarnummer": "Alt Inventarnummer"}, inplace=True)
        # add a new column to store the new Inventarnummer in
        df_in.insert(0, "Inventarnummer", np.nan)
        # add a new column to mark whether the Bilddatei was also renamed
        df_in.insert(0, "Bild umbennennt", np.nan)
        if return_sorted:
            df_in.sort_values(by=["Inventar Sortierbar"], inplace=True, ignore_index=True)
        if is_excel:
            SE.save_df_excel(df_in, f"{tranche}_{today}")
        else:
            return df_in

    # add_rename_inventarnummer(in_data="a_Test_rename_inventarnummer", is_excel=True, return_sorted=False,
    # tranche="Test")

    @staticmethod
    def has_inventarnummer_double(in_data: pd.DataFrame or str, is_excel: bool = False, tranche: str or None = None,
                                  abteilung: str or None = None) -> pd.DataFrame or None:
        """
        Checks whether there are any double in the column "Inventarnummer". If not excel, also returns a bool.
        :param in_data: excel / df
        :param is_excel: True if excel
        :param tranche: name
        :param abteilung: name or df_documentation if not excel
        :return: if not excel: True if any double, df with doubles and df without, otherwise False
        """
        if is_excel:
            # read the excel into a dataframe
            df_in = pd.read_excel(os.path.join(current_wdir, "input", f"{in_data}.xlsx"))
            # read the documentation excel
            df_doc = pd.read_excel(os.path.join(current_wdir, "output", "_dokumentation",
                                                f"{abteilung}_Dokumentation.xlsx"))
        else:
            df_in = in_data
            df_doc = abteilung
        #############################
        # clean the df
        df_in = Clean.strip_spaces(df_in)
        # returns df with all the doubles
        df_doubles = df_in[df_in["Inventarnummer"].duplicated(keep=False)]
        if len(df_doubles) != 0:
            # add new columns for adding new Inventarnummer
            df_doubles = Inventarnummer.add_rename_inventarnummer(
                in_data=df_doubles, is_excel=False, return_sorted=True, tranche=None)
            df_in.drop_duplicates(subset=["Inventarnummer"], keep=False, inplace=True, ignore_index=True)
            if is_excel:
                SE.save_df_excel(df_doubles, f"{tranche}_{today}_Inventarnummer_Dubletten")
                SE.save_df_excel(df_in, f"{tranche}_{today}_Inventarnummer_Keine_Dubletten")
                # Write documentation
                df_doc = pd.concat([df_doc, pd.DataFrame(
                    {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": "-",
                     "Feld": "Inventarnummer", "Was": "Dubletten", "Resultat": f"{len(df_doubles)} dubletten",
                     "Output Dokument": f"{tranche}_{today}_Inventarnummer_Dubletten // "
                                        f"{tranche}_{today}_Inventarnummer_Keine_Dubletten",
                     "Ersetzt Hauptexcel": "unterteilt es"}, index=[0])], ignore_index=True)
                SE.save_doc_excel(df_doc, abteilung)
            else:
                return True, df_doubles, df_in
        else:
            if is_excel:
                # Write documentation
                df_doc = pd.concat([df_doc, pd.DataFrame(
                    {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": "-",
                     "Feld": "Inventarnummer", "Was": "Dubletten", "Resultat": f"keine dubletten",
                     "Output Dokument": f"-", "Ersetzt Hauptexcel": "-"}, index=[0])], ignore_index=True)
                SE.save_doc_excel(df_doc, abteilung)
            else:
                return False, None, None

    # # Version with doubles
    # has_inventarnummer_double(in_data="a_Test_has_inventarnummer_double_Doppelt", is_excel=True, tranche="Test",
    #                           abteilung="Test")
    #
    # # Version witout doubles
    # has_inventarnummer_double(in_data="a_Test_has_inventarnummer_double_keine_Doppel", is_excel=True, tranche="Test",
    #                           abteilung="Test")


if __name__ == "__main__":
    pass