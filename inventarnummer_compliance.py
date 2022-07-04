import os
from datetime import date
import pandas as pd

from tools.custom_exceptions import *
from tools.double_check import DoubleCheck as Double
from tools.excel_functions import ExcelFunctions as ExF
from tools.inventarnummer import Inventarnummer as InvNr
from tools.picture_files import PictureFiles as Pic
from tools.RegEx_patterns import RegExPattern as RePat

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


def add_x_inventarnummer_compliance(in_excel: str, tranche: str, abteilung: str, regex_pattern) -> None:
    """
    It checks every possible mistake with the inventarnummer and marks the problems in separate columns with an x. If
    there are no mistakes it does not save an excel, it does save the documentation in any case. This function is
    used when revalidating the inventarnummer as excels are saved.
    Test Excel: Test_inventarnummer_compliance_Fehler -> mistakes occur
    Test Excel: Test_inventarnummer_compliance_Korrekt -> no mistakes Ozeanien Prefix
    :param in_excel: name of excel to test, no .xslx extension needed
    :param tranche: name of tranche
    :param abteilung: name of abteilung
    :param regex_pattern: function of the regex pattern
    :return: None as it saves the results as new excels.
    """
    # read in the excel
    df_in = ExF.in_excel_to_df(in_excel)
    # initiate a doc list
    doc_list = []
    # we do not need to clean as it is done in the functions
    # add the new column for picture rename (this way it gets pushed towards after all the compliance
    try:
        df_in, picture_doc = Pic.add_old_picture_name(df_in, tranche, in_excel)
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
        if "Komplett" in in_excel:
            out_name = f"{tranche}_Komplett_{today}"
        else:
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
            "Ersetzt Hauptexcel": "ja"})
        # save the excel
        ExF.save_df_excel(df_in, out_name)
    # save the documentation in any case
    ExF.save_doc_list(doc_list, abteilung)


# TODO: write separate_excel_inventarnummer_compliance


if __name__ == '__main__':
    pass

    add_x_inventarnummer_compliance(
        in_excel="Pilot_Komplett_2022-02-16", tranche="Pilot", abteilung="Ozeanien",
        regex_pattern=RePat.ozeanien_re_pattern())

    # file_name = "Test_inventarnummer_compliance_Korrekt"
    # file_path = os.path.join("_Test_Excel", file_name)
    #
    # add_x_inventarnummer_compliance(file_path, "Test", "Test", RePat.general_re_pattern())

