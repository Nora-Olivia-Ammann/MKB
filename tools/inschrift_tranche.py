import os
from datetime import date

import numpy as np
import pandas as pd

from mkb_code.tools.RegEx_patterns import RegExPattern as RePat

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class Inschrift:

    @staticmethod
    def add_x_inschrift_incorrect(input_df: pd.DataFrame, tranche: str, in_excel_name: str) -> bool and pd.DataFrame and dict:
        """
        Checks whether all the Einlaufnummer are in the correct format. If leading zeros are missing it fills those.
        If used as nested function it also returns a True if all is correct and the df (if leading zeros were added
        it does not appear as a fault, therefore the input df has to be overwritten), or False and the df with the column
        that marks them as such added.
        Test Excel: Test_inschrift_compliance_Fehler -> will have x, fills some leading zeroes
        Test Excel: Test_inschrift_compliance_Korrekt -> all correct, fills some leading zeroes
        :param input_df: df that will be changed
        :param tranche: name of tranche
        :param in_excel_name: name of excel
        :return: new df, documentation
        """
        pattern_einlauf_correct, pattern_zero, pattern_incomplete = RePat.inschrift_re_pattern()
        # get the index number of the column inschrift
        index_no = input_df.columns.get_loc("Inschrift")
        # try to insert a new column to the right of it
        try:
            input_df.insert(index_no + 1, "Inschrift falsch", np.nan)
        # if it already exists then delete all the entries
        except ValueError:
            input_df["Inschrift falsch"] = np.nan
        for index, inschrift in input_df["Inschrift"].iteritems():
            # RegEx only works with strings. Numbers (int and float) are also treated as strings,
            # you only get a type error if it is empty, meaning a np.nan
            try:
                # if the numbers are only zeros, this has to come first,
                # as a 0 number could also match the correct RegEx
                if pattern_zero.match(inschrift):
                    input_df.loc[index, "Inschrift falsch"] = "x"
                # if the numbers are valid (most will be)
                elif pattern_einlauf_correct.match(inschrift):
                    continue
                elif pattern_incomplete.match(inschrift):
                    # split the string
                    spl_val = inschrift.split("_")
                    # fill the number with zeros until it is four digits
                    spl_val[1] = spl_val[1].zfill(4)
                    # join the split string from the list
                    new_inschrift = "_".join(spl_val)
                    # assign the new value to the cell
                    input_df.loc[index, "Inschrift"] = new_inschrift
                else:
                    input_df.loc[index, "Inschrift falsch"] = "x"
            except TypeError:
                input_df.loc[index, "Inschrift falsch"] = "x"
        # if all are correct then the column is empty
        if input_df["Inschrift falsch"].isnull().all():
            input_df.pop("Inschrift falsch")
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schl??ssel Excel": "-",
                        "Feld": "Inschrift",
                        "Was": "Compliance",
                        "Resultat": f"alle Angaben korrekt oder wurden korrigiert.",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "ja"}
            return True, input_df, doc_dict
        else:
            doc_dict = {"Datum": today,
                        "Tranche": tranche,
                        "Input Dokument": in_excel_name,
                        "Schl??ssel Excel": "-",
                        "Feld": "Inschrift",
                        "Was": "Compliance",
                        "Resultat": f"Einige Inschriften inkorrekt.",
                        "Output Dokument": np.nan,
                        "Ersetzt Hauptexcel": "ja"}
            return False, input_df, doc_dict


if __name__ == "__main__":
    pass

    # file_name = "Test_inschrift_compliance_Korrekt"
    # file_path = os.path.join("_Test_Excel", file_name)
    # df = ExF.in_excel_to_df(file_path)
    #
    # # function call
    # boo, out_df, doc = Inschrift.add_x_inschrift_incorrect(df, "Test", "Test")
    #
    # print(boo)
    # ExF.save_doc_single("Test", doc)
    # if out_df is not None:
    #     ExF.save_df_excel(out_df, "Test")
