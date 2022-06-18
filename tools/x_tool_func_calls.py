from os.path import dirname as up
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

################################

if __name__ == '__main__':
    # Beschreibung Call

    file_name = "Test_add_str_to_beschreibung"
    file_path = "_Test_Excel/" + file_name

    in_df = ExF.in_excel_to_df(file_path)
    out_df, dict_df = Besch.add_str_to_beschreibung(
        in_df, in_excel_name="Test", source_col="Schubladen Beschriftung",
        prefix_text="Schublade: ", tranche="Test")

    print(1)
