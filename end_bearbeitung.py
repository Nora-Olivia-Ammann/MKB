import os
import pandas as pd
from datetime import date
import warnings

from tools.beschreibung import Beschreibung as Besch
from tools.cleaning_df import CleanDF as Clean
from tools.custom_exceptions import *
from tools.inschrift_tranche import Inschrift as Insch
from tools.inventarnummer import Inventarnummer as InvNr
from tools.NaN_check import NaN as NAN
from tools.excel_functions import ExcelFunctions as ExF

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)

# TODO: extract nested functions
# TODO: clean up nested functions
# TODO: complete rewrite

def end_bearbeitung(in_excel: str, header_excel: str, tranche: str, abteilung: str, regex_pattern,
                    do_inventarnummer_compliance: bool = True, continue_if_false_values: bool = False) -> None:
    """
    This function transfers the data from the excel we worked with into a excel which contains the headers for the TMS
    import. The headers will be read in as an excel because, the newest version can be easily downloaded from the TMS.
    Rather than created the excel myself, this ensures that the columns are correct. The Inventarnummer compliance
    is optional, because there very well may be a situation in which it is decided to keep some incorrect
    Inventarnummer. If that is the case a warning will appear.
    Before the information is transferred, the content of the tranchen excel is checked. These are not extensive checks
    and if problems are diagnosed then other functions may have to be used to process it further. If the Tranchen excel
    is not complete or has mistakes, then it can be chosen whether the function should continue with the rows that
    are correct. In any case the excels with the rows that are faulty is saved.
    If the function is continued then the second header is added to the import excel and the information is transferred
    and the columns with default values are filled.
    :param regex_pattern: function form the tools.RegEx_patterns that compiles and returns the pattern for the Abteilung
    :param in_excel: tranchen Excel
    :param header_excel: current excel that can be used for TMS import
    :param do_inventarnummer_compliance: True: checks the inventarnummer
    :param continue_if_false_values: True: creates import excel with the rows that are correct, False: stops function
    :param tranche: name
    :param abteilung: name
    :return: None
    """
    # read in_excel to df, which is the one to fill with values
    df_in = ExF.in_excel_to_df(in_excel)
    # clean the df
    df_in = Clean.strip_spaces_whole_df(df_in)
    # read in the header excel which is the output format
    df_out = ExF.in_excel_to_df(header_excel)
    # read the documentation excel
    doc_list = []
    ############################################
    # add a list to store the information whether anything is wrong
    correct_check_list = []
    # NAN CHECK
    # Check whether all the mandatory fields are filled
    mandatory_fields = ["Beschreibung", "Inventarnummer", "Erwerbungsart", "Objektstatus", "Inschrift", "Geographietyp",
                        "Herk.9: Kontinent", "Herk.7: Subkontinent", "Datierung"]
    # the fourth return is the df with the NaN columns dropped, therefore we give it the
    res_nan_check, df_nan, ex_name, df_not_nan = NAN.has_columns_nan(
        in_data=df_in, is_excel=False, tranche=None, abteilung=df_doc, column_list=mandatory_fields,
        separate_excel_columns=False)
    # check if any are empty
    # Returns true if there are NaN
    if res_nan_check:
        # overwrite the df with the one without the doubles
        df_in = df_not_nan
        df_in.reset_index(inplace=True)  # reset the index
        df_in.pop("index")  # when resetting the index it is saved as a new column
        ExF.save_df_excel(df_nan, f"{tranche}_{today}_Fehlende_Angaben")
        doc_list.append({"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "-", "Feld": "alle",
             "Was": "End Check", "Resultat": f"{len(df_nan)} Zeilen fehlen Angaben",
             "Output Dokument": f"{tranche}_{today}_Fehlende_Angaben", "Ersetzt Hauptexcel": "unterteilt es"})
        # append that a mistake was found
        correct_check_list.append(False)
    # INVENTARNUMMER DOUBLE CHECK
    # returns True if there are doubles
    res_doubles_check, df_doubles, df_no_double = InvNr.has_inventarnummer_double(
        in_data=df_in, is_excel=False, tranche=None, abteilung=df_doc)
    if res_doubles_check:
        df_in = df_no_double
        df_in.reset_index(inplace=True)  # reset the index
        df_in.pop("index")  # when resetting the index it is saved as a new column
        ExF.save_df_excel(df_doubles, f"{tranche}_{today}_Doppelte_Inventarnummern")
        doc_list.append({"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "-", "Feld": "alle",
             "Was": "End Check", "Resultat": f"{len(df_doubles)} Doppelte Inventarnummern",
             "Output Dokument": f"{tranche}_{today}_Doppelte_Inventarnummern", "Ersetzt Hauptexcel": "unterteilt es"})
        # append that a mistake was found
        correct_check_list.append(False)
    # INVENTARNUMMER COMPLIANCE
    # as we do not want to perform an extensive analysis of the wrong Inventarnummer, we do a simple test here
    if do_inventarnummer_compliance:
        pattern_correct, _, _ = regex_pattern
        # we can only drop the rows according to their index, at the end, because otherwise we might get an
        # IndexError because the number is greater than the size of the df
        drop_index_list = []
        df_wrong_inventar = pd.DataFrame({})
        for index, value in df_in["Inventarnummer"].iteritems():
            if not pattern_correct.match(value):
                df_wrong_inventar = df_wrong_inventar.append(df_in.iloc[index, :], ignore_index=True)
                drop_index_list.append(index)
        if len(df_wrong_inventar) != 0:
            # we drop the wrong rows
            df_in.drop(index=drop_index_list, axis=0, inplace=True)
            # add the columns to document the renaming of inventarnummer
            df_wrong_inventar = InvNr.add_inventarnummer_alt(in_data=df_wrong_inventar, is_excel=False, return_sorted=True,
                                                             tranche=None)
            doc_list.append(
                {"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "-",
                 "Feld": "Inventarnummer",
                 "Was": "End Check", "Resultat": f"{len(df_wrong_inventar)} Falsche Inventarnummern",
                 "Output Dokument": f"{tranche}_{today}_Falsche_Inventarnummer",
                 "Ersetzt Hauptexcel": "unterteilt es"})
            ExF.save_df_excel(df_wrong_inventar, f"{tranche}_{today}_Falsche_Inventarnummer")
            correct_check_list.append(False)
    else:
        # it is possible that we end up using Inventarnummer that are not compliant, therefore we may not want
        # to check and separate it. Although it is recommended to do that in the first step.
        warnings.warn("Inventarnummer compliance was not checked.")
    # EINLAUFNUMMER COMPLIANCE
    # the function may add leading zeros to the einlaufnummer, in that case it would not read as a false value,
    # it returns that df, therefore we replace in the df_in with that one
    einlauf_check, df_in = Insch.add_x_inschrift_incorrect(
        in_data=df_in, is_excel=False, tranche=None, abteilung=df_doc)
    if not einlauf_check:
        doc_list.append({"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "-",
             "Feld": "Inschrift", "Was": "End Check", "Resultat": f"Es hat Falsche Einlaufnummern",
             "Output Dokument": f"{tranche}_{today}_Falsche_Inschrift",
             "Ersetzt Hauptexcel": "unterteilt es"})
        correct_check_list.append(False)
    # Check if the program should continue if data was missing or incorrect
    if not continue_if_false_values and len(correct_check_list) != 0:
        # save the df_in, where all the correct data is stored
        ExF.save_df_excel(df_in, f"{tranche}_{today}_Alles_Korrekt")
        doc_list.append({"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "-",
             "Feld": "alle", "Was": "End Check", "Resultat": f"Das Excel hat {len(correct_check_list)} fehler, das"
                                                             f"TMS Import Excel wurde nicht erstellt.",
             "Output Dokument": f"{tranche}_{today}_Alles_Korrekt", "Ersetzt Hauptexcel": "unterteilt es"})
        ExF.save_doc_list(doc_list, abteilung)
        # raise an Exception to stop the program
        raise TrancheMissingValue("Some data is missing or incorrect, the TMS import excel was not created.")
    elif continue_if_false_values and len(correct_check_list) != 0:
        warnings.warn("Some data is missing or incorrect, the program will continue to create the TMS import excel,"
                      "with the remaining correct data.")
        doc_list.append({"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "-",
             "Feld": "alle", "Was": "End Check",
             "Resultat": f"Das Excel hat {len(correct_check_list)} Fehler, mit den Korrekten Zeilen wurde das TMS "
                         f"Import Excel erstellt.",
             "Output Dokument": f"TMS_Import_{tranche}_{today}",
             "Ersetzt Hauptexcel": "ja"})
    else:
        doc_list.append({"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "-",
             "Feld": "alle", "Was": "End Check",
             "Resultat": f"All notwendigen Angaben sind vorhanden, Daten werden transferiert",
             "Output Dokument": f"TMS_Import_{tranche}_{today}", "Ersetzt Hauptexcel": "ja"})
    # START TRANSFERRING DATA
    # before transferring data we add the Schubladenname to the Beschreibung, as it is easier to do before we add
    # the second header
    df_in = Besch.add_schublade(in_data=df_in, is_excel=False, abteilung=df_doc)
    # drop all the content of the header df so that only the header remains
    df_out.drop(index=df_out.index[:], axis=0, inplace=True)
    # add the information for the second header
    df_out = df_out.append({"Person oder Institution1": "Fotograf*in/Filmer*in",
                            "Person oder Institution2": "Aufgenommene Person",
                            "Titel (ausführlich)1": "früherer Titel / alte Bezeichnung",
                            "Titel (ausführlich)2": "Werktitel / Name der Darstellung",
                            }, ignore_index=True)
    # adding nan rows so that df_out has as many rows as df_in plus an additional for the second header
    df_out = df_out.reindex(index=list(range(0, len(df_in.index) + 1)))
    # Fill the columns that have a default value
    info_dict = {"Abteilung": abteilung, "Klassifizierung": "Fotografie", "Objekt (Kurzbezeichnung)": "Feldfoto",
                 "Überprüft": "0", "Freigabe Internet": "0", "Ausgestellt": "0", "Verantwortlichkeit": "1",
                 "Virtuelles Objekt": "0"}
    for key, value in info_dict.items():
        df_out[key][1:] = value
    # if there are no values fill the Material & Technik with the default
    df_out["Material & Technik"][1:] = df_out["Material & Technik"][1:].fillna("Positiv (auf Karteikarte)")
    # Info to transfer
    # few columns have different names in the excel than in the excel for the import, for those we use a dictionary
    col_dict = {"P1 Fotograf*in/Filmer*in": "Person oder Institution1",
                "P2 Aufgenommene Person": "Person oder Institution2",
                "T1 früherer Titel / alte Bezeichnung": "Titel (ausführlich)1",
                "T2 Werktitel / Name der Darstellung": "Titel (ausführlich)2"}
    for key, value in col_dict.items():
        df_out[value][1:] = df_in[key]
    # these columns have to be in the source excel therefore we do not allow the program to continue if they
    # are not there, this will raise a KeyError
    cols_must_transfer = ["Inventarnummer", "Erwerbungsart", "Objektstatus", "Datierung", "Beschreibung", "Inschrift",
                          "Geographietyp", "Herk.9: Kontinent", "Herk.6: Land", "Departement/Provinz/Kanton",
                          "Distrikt", "Herk.1: Ort", "Bezirk/Gemeinde", "Herk.2: Landschaft/Fluss",
                          "Herk. 8: Politische Region", "Herk.7: Subkontinent", "Inselgruppe", "Insel",
                          "Herk.4: Grossregion/gr. Insel", "Herk.3: Gebiet/Unterregion/Kl. Insel",
                          "Bemerkungen [Geographie]", "Ethniengruppe (Nation)"]
    for col in cols_must_transfer:
        df_out[col][1:] = df_in[col]
    ExF.save_df_excel(df_out, f"TMS_Import_{tranche}_{today}")
    ExF.save_doc_list(doc_list, abteilung)


# end_bearbeitung(in_excel="Metadaten_Test_Import", header_excel="_TMS_Header",
#                 do_inventarnummer_compliance=True, continue_if_false_values=False, tranche="Test", abteilung="Test")
#
# # EVERYTHING IS CORRECT
# end_bearbeitung(in_excel="l_Test_Endbearbeitung_Korrekt", header_excel="l_Test_Endbearbeitung_TMS_Header",
#                 do_inventarnummer_compliance=True, continue_if_false_values=False, tranche="Test", abteilung="Test")
#
# # EVERYTHIG HAS A MISTAKE, PROGRAM WILL BE STOPED
# end_bearbeitung(in_excel="l_Test_Endbearbeitung_Fehler", header_excel="l_Test_Endbearbeitung_TMS_Header",
#                 do_inventarnummer_compliance=True, continue_if_false_values=False, tranche="Test", abteilung="Test")
#
# # EVERYTHIG HAS A MISTAKE, PROGRAM WILL CONTINUE
# end_bearbeitung(in_excel="l_Test_Endbearbeitung_Fehler", header_excel="l_Test_Endbearbeitung_TMS_Header",
#                 do_inventarnummer_compliance=True, continue_if_false_values=True, tranche="Test", abteilung="Test")
#
#
# # EVERYTHING BUT THE INVENTARNUMMER IS CORRECT
# # BECAUSE THE INVENTARNUMMER WILL NOT BE CONTROLLED IT WILL NOT REGISTER AS A FAULT, IT HOWEVER MAY BE A
# # EXPLICIT DECISION TO CONTINUE WITH SOME MISTAKES
# end_bearbeitung(in_excel="l_Test_Endbearbeitung_Inventar_Fehler", header_excel="l_Test_Endbearbeitung_TMS_Header",
#                 do_inventarnummer_compliance=False, continue_if_false_values=True, tranche="Test", abteilung="Test")


# complete list of all columns that have content to transfer
all_cols = ["Inventarnummer", "Abteilung", "Klassifizierung", "Erwerbungsart", "Objektstatus",
            "Person oder Institution1", "Person oder Institution2", "Titel (ausführlich)1", "Titel (ausführlich)2",
            "Objekt (Kurzbezeichnung)", "Datierung", "Material & Technik", "Beschreibung", "Inschrift",
            "Überprüft", "Freigabe Internet", "Ausgestellt", "Verantwortlichkeit", "Virtuelles Objekt",
            "Geographietyp", "Herk.9: Kontinent", "Herk.6: Land", "Departement/Provinz/Kanton", "Distrikt",
            "Herk.1: Ort", "Bezirk/Gemeinde", "Herk.2: Landschaft/Fluss", "Herk. 8: Politische Region",
            "Herk.7: Subkontinent", "Inselgruppe", "Insel", "Herk.4: Grossregion/gr. Insel",
            "Herk.3: Gebiet/Unterregion/Kl. Insel", "Bemerkungen [Geographie]", "Ethniengruppe (Nation)"]
