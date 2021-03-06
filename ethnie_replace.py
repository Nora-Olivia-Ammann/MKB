import os
import pandas as pd
import numpy as np
from datetime import date

from tools.custom_exceptions import *
from tools.key_excel import KeyExcel as KE
from tools.excel_functions import ExcelFunctions as ExF

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)

# TODO double key

def replace_ethnie(in_excel: str, key_excel: str, tranche: str, abteilung: str) -> None:
    """
    After the checks whether the key document is complete and has all the keys, it will replace the existing values
    with the new spelling. If the spelling should stay the same, it has to be copied from the old spelling.
    :param in_excel: tranche excel
    :param key_excel: key
    :param tranche: name
    :param abteilung: name
    :return:
    """
    # ACCORDING TO THE KEY EXCEL REPLACE THE EXISTING INFO
    df_in = ExF.in_excel_to_df(in_excel)
    df_key = ExF.in_excel_to_df(key_excel)
    df_doc = ExF.doc_excel_to_df(abteilung)
    # check if all the elements are in the key excel and were checked
    key_check, df_not_dict = KE.key_all_there(in_data=df_in, key_data=df_key,
                                              drop_uncontrolled=True, is_excel=False,
                                              abteilung=df_doc)
    if not key_check:
        # check whether it is only because the values are marked as uncontrolled
        # because modifications were made on the dataframe in the previous check we have to read it in again
        df_key = pd.read_excel(os.path.join(current_wdir, "input", f"{key_excel}.xlsx"))
        key_check_uncontrolled, df_not_dict_uncontr = KE.key_all_there(
            in_data=df_in, key_data=df_key, drop_uncontrolled=False, is_excel=False, abteilung=df_doc)
        if not key_check_uncontrolled:
            out_key = pd.DataFrame(
                {"Kontrolliert": "", "Original Schreibweise": df_not_dict_uncontr["Ethniengruppe (Nation)"],
                 "Ethnie Neu": "", "Bsp: Inventarnummer": df_not_dict_uncontr["Inventarnummer"],
                 "Bsp: Ordner Bild": df_not_dict_uncontr["Ordner Bild"], "Bemerkungen": ""})
            # save the excel
            ExF.save_df_excel(out_key, f"Schl??ssel_Fehlende_Ethnie_{tranche}_{today}")
            # write documentation
            ExF.save_doc_single(
                abteilung,
                {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schl??ssel Excel": key_excel,
                 "Feld": f"Ethniengruppe (Nation)", "Was": f"Vollst??ndigkeit im Schl??ssel Excel",
                 "Resultat": f"{len(out_key)} fehlende Schl??ssel",
                 "Output Dokument": f"Schl??ssel_Fehlende_Ethnie_{tranche}_{today}", "Ersetzt Hauptexcel": "-"})
            raise MissingKey("Ethniengruppe (Nation) values are missing in the key document.")
        else:
            # reformat the df
            out_key = pd.DataFrame(
                {"Kontrolliert": "", "Ethniengruppe (Nation)": df_not_dict["Ethniengruppe (Nation)"],
                 "Ethnie Neu": "", "Bsp: Inventarnummer": df_not_dict["Inventarnummer"],
                 "Bsp: Ordner Bild": df_not_dict["Ordner Bild"], "Bemerkungen": ""})
            # save the excel
            ExF.save_df_excel(out_key, f"Schl??ssel_Unkontrolliert_Ethnie_{tranche}_{today}")
            # write documentation
            ExF.save_doc_single(
                abteilung,
                {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schl??ssel Excel": key_excel,
                 "Feld": f"Ethniengruppe (Nation)", "Was": f"Vollst??ndigkeit im Schl??ssel Excel",
                 "Resultat": f"{len(out_key)} Schl??ssel sind nicht kontrolliert.",
                 "Output Dokument": f"Schl??ssel_Unkontrolliert_Ethnie_{tranche}_{today}",
                 "Ersetzt Hauptexcel": "-"})
            # raise Error
            raise MissingKey("Not all keys are validated")
    # at this point the uncontrolled are already dropped, therefore this doesnt have to be repeated
    # check if all the keys have a new value
    if df_key["Ethnie Neu"].isnull().any():
        df_nan = df_key[df_key["Ethnie Neu"].isnull()]
        ExF.save_df_excel(df_nan, f"Schl??ssel_Fehlende_Angaben_{today}")
        ExF.save_doc_single(
            abteilung, {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schl??ssel Excel": key_excel,
                        "Feld": f"Ethniengruppe (Nation)", "Was": f"Vollst??ndigkeit im Schl??ssel Excel",
                        "Resultat": f"{len(df_nan)} Schl??ssel fehlen Angaben",
                        "Output Dokument": f"Schl??ssel_Fehlende_Angaben_{today}",
                        "Ersetzt Hauptexcel": "-"})
        raise KeyDocIncomplete("Not alle Keys have an assigned new value.")
    # replace the values with the correct TMS constituent name
    # create a dict from the key_excel
    ethno_dict = dict(zip(df_key["Ethniengruppe (Nation)"], df_key["Ethnie Neu"]))
    # add a nan value
    ethno_dict[np.nan] = np.nan
    df_in.replace(to_replace=ethno_dict, inplace=True)
    # save excel
    ExF.save_df_excel(df_in, f"{tranche}_{today}")
    ExF.save_doc_single(
        abteilung, {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schl??ssel Excel": key_excel,
                    "Feld": f"Ethniengruppe (Nation)", "Was": f"Ersetzten mit neuer Schreibweise",
                    "Resultat": f"Erfolgreich ersetzt", "Output Dokument": f"{tranche}_{today}",
                    "Ersetzt Hauptexcel": "ja"})


# # EVERYTHING IS CORRECT
# replace_ethnie(in_excel="d_Test_replace_ethnie_Tranche", key_excel="d_Test_replace_ethnie_Schlu??ssel_Korrekt",
#                tranche="Test", abteilung="Test")
#
#
# # KEY EXCEL UNCONTROLLED
# replace_ethnie(in_excel="d_Test_replace_ethnie_Tranche", key_excel="d_Test_replace_ethnie_Schlu??ssel_Unkontrolliert",
#                tranche="Test", abteilung="Test")
#
# # KEY EXCEL MISSING
# replace_ethnie(in_excel="d_Test_replace_ethnie_Tranche", key_excel="d_Test_replace_ethnie_Schlu??ssel_Fehlen",
#                tranche="Test", abteilung="Test")
#
#
# # SOME KEYS MISSING NEW VALUE
# replace_ethnie(in_excel="d_Test_replace_ethnie_Tranche", key_excel="d_Test_replace_ethnie_Schlu??ssel_Unausgefu??llt",
#                tranche="Test", abteilung="Test")


if __name__ == '__main__':
    pass
