import os
import pandas as pd
import numpy as np
from datetime import date

from tools.inventarnummer import Inventarnummer as InvNr
from tools.excel_functions import ExcelFunctions as ExF
from tools.picture_files import PictureFiles as Pic
from tools.custom_exceptions import *
from tools.double_check import DoubleCheck as Double

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


def add_x_inventarnummer_compliance(in_excel: str, tranche: str, abteilung: str, regex_pattern) -> None:
    # todo: validate, add description
    # TODO: this is used when re-validating the inventarnummer, not in the first step as it saves and excel
    # read in the excel
    df_in = ExF.in_excel_to_df(in_excel)
    # initiate a doc list
    doc_list = []
    # we do not need to clean as it is done in the functions
    # add the new column for picture rename (this way it gets pushed towards after all the compliance
    try:
        df_in, picture_doc = Pic.add_rename_picture_col(df_in, tranche, in_excel)
        doc_list.append(picture_doc)
    # if the column already exists we do not want to overwrite it
    except ColumnExistsError:
        pass
    # first check for leading zeros, this is done first as there may be 'hidden' doubles
    has_zero, zero_df, zero_doc = InvNr.add_x_leading_zero(df_in, tranche, in_excel, regex_pattern)
    # if it has zeros replace the df
    if has_zero:
        df_in = zero_df
    # append the documentation
    doc_list.append(zero_doc)
    # then mark the doubles
    has_double, double_df, double_doc = Double.add_x_col_double(df_in, "Inventarnummer", tranche, in_excel)
    if has_double:
        df_in = double_df
    # append documentation
    doc_list.append(double_doc)
    # now check for all the wrong inventarnummern
    has_wrong, wrong_df, wrong_doc = InvNr.add_x_wrong_inventarnummer(df_in, tranche, in_excel, regex_pattern)
    if has_wrong:
        df_in = wrong_df
    doc_list.append(wrong_doc)
    # check if all are false, if that is the case then no changes were made and no new excel must be saved
    if all(result == False for result in (has_zero, has_double, has_wrong)):
        # write the documentation that nothing was replaced
        doc_list.append({
            "Datum": today,
            "Tranche": tranche,
            "Input Dokument": in_excel,
            "Schlüssel Excel": "-",
            "Feld": "Inventarnummer",
            "Was": "Markieren wenn Problem",
            "Resultat": f"Keine Inventarnummern haben Probleme (0, falsch, doppelt)",
            "Output Dokument": f"kein neues Excel",
            "Ersetzt Hauptexcel": "nein"})
    else:
        # write the documentation with the new excel name
        out_name = f"{tranche}_{today}"
        doc_list.append({
            "Datum": today,
            "Tranche": tranche,
            "Input Dokument": in_excel,
            "Schlüssel Excel": "-",
            "Feld": "Inventarnummer",
            "Was": "Markieren wenn Problem",
            "Resultat": f"Gewisse Inventarnummern haben Probleme (0, falsch, doppelt)",
            "Output Dokument": out_name,
            "Ersetzt Hauptexcel": "nein"})
        # save the excel
        ExF.save_df_excel(df_in, out_name)
    # save the documentation in any case
    ExF.save_doc_list(doc_list, abteilung)


# TODO: write separate_inventarnummer_compliance



if __name__ == '__main__':
    pass
