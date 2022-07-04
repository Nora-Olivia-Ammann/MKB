import os
import pandas as pd
from datetime import date

import warnings
from tools.cleaning_df import CleanDF as Clean
from tools.inschrift_tranche import Inschrift as Insch
from tools.inventarnummer import Inventarnummer as InvNr
from tools.excel_functions import ExcelFunctions as ExF
from tools.unique_ID import UniqueID as UID

today = str(date.today())
# os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


# TODO: complete rewrite
# TODO: reorganise and make compatible with other header names

def new_tranche_excel(in_excel: str, tranche: str, abteilung: str, prefix_unique_id: str, return_sorted: bool = False,
                      has_second_header: bool = False) -> None:
    """
    Transfers the data from the Excel we get from the BSB to the excel that we use to work with.
    If any "Inventarnummer" or "Beschreibung" are missing it creates an additional document, because we would need to
    contact the BSB for that information.
    If the Einlaufnummer are missing the leading zeros it adds them.
    It filters out the number of the Schublade (which is the name of the folder for the picture) and adds that to a new
    column.
    Creates and adds a Unique_ID, by which a row can be definitively identified at all times.
    For roughly correct Inventarnummer it adds leading zeros in a new column so that it can be machine sortable.
    """
    # read in the excel with the data
    df_in = ExF.in_excel_to_df(in_excel)
    # clean the df
    df_in = Clean.strip_spaces(df_in)
    # create empty list to save the documentation
    doc_list = []
    if has_second_header:
        # drop the first row as it is the second header, modifies memory of df (inplace)
        df_in.drop(index=df_in.index[0], axis=0, inplace=True)
        # display a message that the row was dropped
        warnings.warn("The first row was dropped as it was indicated to be a second header.")
    # drop all the rows that are only NaN
    df_in.dropna(axis=0, how='all', inplace=True)
    df_in.reset_index(inplace=True)  # reset the index
    # create a new df to transfer the information to
    # TODO: change the arrangement and names of the columns
    df_out = pd.DataFrame(
        columns=["Inventarnummer", "Dublette", "Tranche", "Ordner Bild", "Bilddatei", "Ethniengruppe (Nation)",
                 "Datierung", "Geo_ID",
                 "Beschreibung", "P2 Aufgenommene Person", "Inschrift", "P1 Fotograf*in/Filmer*in",
                 "T1 früherer Titel / alte Bezeichnung", "T2 Werktitel / Name der Darstellung",
                 "Schubladen Beschriftung", "Inventar Sortierbar", "Bemerkung (betr. Bearbeitung)", "Unique_ID"])
    # in order for the contents of the column to be transferred one by one as we do not want to merge we need the
    # target df to have the same row numbers, this can be achieved through reindexing
    df_out = df_out.reindex(index=list(range(0, len(df_in.index))))
    # transfer the information to the correct new columns
    # TODO: revise in and out columns
    in_cols = ["Inventarnummer", "Abteilung", "Person oder Institution1", "Datierung", "Beschreibung", "Inschrift"]
    out_cols = ["Inventarnummer", "Schubladen Beschriftung", "P1 Fotograf*in/Filmer*in", "Datierung", "Beschreibung",
                "Inschrift", "Bilddatei"]
    for in_col, out_col in zip(in_cols, out_cols):
        df_out[out_col] = df_in[in_col]
    # assign the tranche name, this is relevant as at a later point different tranche will be merged, while the picture
    # will stay within the folder of the tranche
    df_out["Tranche"] = tranche
    # TODO: inventarnummer compliance from the original nested functions
    # add leading zeros to the Einlaufnummer if not already present, and add a column to mark where the einlaufnummer
    # is missing or incorrect
    _, df_out = Insch.add_x_inschrift_incorrect(in_data=df_out, is_excel=False, tranche=tranche, abteilung=abteilung)
    # for easier use and later processing get the folder name from the Beschreibung for each row and place it in
    # the column, iterate over the columns
    for index, value in df_out["Beschreibung"].iteritems():
        # in case any Beschreibung are missing
        try:
            # extract the name of the folder and assign the folder name to the cell
            df_out.loc[index, "Ordner Bild"] = list(filter(lambda x: x.startswith('(F)'),
                                                           value.split()))[0].replace(',', '')
        # attribute in case it is empty, as float has not split
        except AttributeError:
            continue
    # add the sortierbare Inventarnummer
    df_out = InvNr.add_inventar_sortierbar(in_data=df_out, is_excel=False, tranche=None, return_sorted=return_sorted)
    # as at this stage the inventarnummer may change, there is no way to uniquely identify a row
    # therefore we create our own ID, by adding leading zeros we make this number sortable and thus preserve the
    # original order
    df_out = UID.add_unique_id(in_data=df_out, is_excel=False, tranche=None, prefix_unique_id=prefix_unique_id)
    # check if Inventarnummer or Beschreibung are missing any values
    if df_out[["Inventarnummer", "Beschreibung"]].isnull().any().any():
        # get the null Inventarnummer
        # tODO. add the column with the identifier from BSB, do this part before the reformatting of the file so that
        #  the original BSB format is kept
        df_nan = df_out[df_out["Inventarnummer"].isnull()]
        df_nan = df_nan.append(df_out[df_out["Beschreibung"].isnull()], ignore_index=True)
        df_nan.drop_duplicates(subset=["Unique_ID"], keep="first", inplace=True, ignore_index=True)
        ExF.save_df_excel(df_nan, f"{tranche}_{today}_BSB_Angaben_Fehlen")
        doc_list.append({"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "-",
                         "Feld": "Gesamtes Dokument", "Was": "Transfer von Information in Excel für die Bearbeitung",
                         "Resultat": f"{len(df_nan)} Beschreibung/Inventarnummer fehlen, Zeilen auf Hauptexcel erhalten.",
                         "Output Dokument": f"{tranche}_{today}_BSB_Angaben_Fehlen", "Ersetzt Hauptexcel": "neu"})
    # save the df
    ExF.save_df_excel(df_out, f"{tranche}_{today}_Komplett")
    # write documentation
    doc_list.append({"Datum": today, "Tranche": tranche, "Input Dokument": in_excel, "Schlüssel Excel": "-",
                     "Feld": "Gesamtes Dokument", "Was": "Transfer von Information in Excel für die Bearbeitung",
                     # TODO: change this from iloc to loc with the UID name
                     "Resultat": f"Unique_ID: {df_out.iloc[0, 15]} - {df_out.iloc[-1, 15]}",
                     "Output Dokument": f"{tranche}_{today}_Komplett", "Ersetzt Hauptexcel": "neu"})
    ExF.save_doc_list(doc_list, abteilung)


if __name__ == '__main__':
    pass
