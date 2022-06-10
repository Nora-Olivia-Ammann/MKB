import os
import pandas as pd
import numpy as np
from datetime import date
import re
import warnings

from beschreibung import Beschreibung as BE
from cleaning_df import CleanDF as Clean
from columns_to_string import ColumnsToStr as COLSTR
from custom_exceptions import *
from ethnie import Ethnie as ETHN
from double_check import DoubleCheck as DOUBLE
from geographie import Geographie as GEO
from inschrift_einlaufnummer_tranche import Inschrift as INSCH
from inventarnummer import Inventarnummer as INVNR
from key_excel import KeyExcel as KE
from modify_excel import ModifyExcel as MODEX
from NaN_check import NaN as NAN
from RegEx_patterns import RegExPattern as REPAT
from excel_functions import ExcelFunctions as ExF
from TMS_einlauf import TMSEinlauf as TMSEINL
from unique_ID import UniqueID as UID

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)

if __name__ == "__main__":
    pass
