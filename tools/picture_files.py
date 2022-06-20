import os
import pandas as pd
import numpy as np
from datetime import date

from excel_functions import ExcelFunctions as ExF
from beschreibung import Beschreibung as Besch
from cleaning_df import CleanDF as Clean
from columns_to_string import ColumnsToStr as ColStr
from custom_exceptions import *
from double_check import DoubleCheck as Double
from geographie import Geographie as Geo
from inschrift_tranche import Inschrift as Insch
from inventarnummer import Inventarnummer as InvNr
from key_excel import KeyExcel as KE
from modify_excel import ModifyExcel as ModE
from NaN_check import NaN as NAN
from RegEx_patterns import RegExPattern as RePat
from TMS_inschrift import TMSEinlauf as TMSInsch
from unique_ID import UniqueID as UID

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()


###############################


class PictureFiles:

    @staticmethod
    def add_rename_picture_col(input_df: pd.DataFrame, tranche: str, in_excel_name: str) \
            -> pd.DataFrame and dict or None:
        # TODO: write description
        # TODO: validate
        # check if the column exists, we do not want to overwrite anything
        if "Bild umbenennt" in input_df.columns:
            raise ColumnExistsError("The Column already exists.")
        # get the index for the inventarnummer so we can add the column next to it
        ind_invnr = input_df.columns.get_loc("Inventarnummer")
        # add the new column
        input_df.insert(ind_invnr + 1, "Bild umbenennt", np.nan)
        doc_dict = {"Datum": today,
                    "Tranche": tranche,
                    "Input Dokument": in_excel_name,
                    "Schlüssel Excel": "-",
                    "Feld": "Bild umbenennt",
                    "Was": "hinzugefügt",
                    "Resultat": f"-",
                    "Output Dokument": np.nan,
                    "Ersetzt Hauptexcel": "ja"}
        return input_df, doc_dict


if __name__ == '__main__':
    pass
