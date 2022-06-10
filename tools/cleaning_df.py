import os
import pandas as pd
import numpy as np
from datetime import date
import re
import warnings

from beschreibung import Beschreibung as BE
from columns_to_string import ColumnsToStr as COLSTR
from custom_exceptions import *
from ethnie import Ethnie as ETHN
from general_double_check import DoubleCheck as DOUBLE
from geographie import Geographie as GEO
from inschrift_einlaufnummer_tranche import Inschrift as INSCH
from inventarnummer import Inventarnummer as INVNR
from key_excel import KeyExcel as KE
from modify_excel import ModifyExcel as MODEX
from NaN_check import NaN as NAN
from RegEx_patterns import RegExPattern as REPAT
from save_excel import SaveExcel as SE
from TMS_einlauf import TMSEinlauf as TMSEINL
from unique_ID import UniqueID as UID

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################


class CleanDF:

    @staticmethod
    def strip_spaces(in_df: pd.DataFrame) -> pd.DataFrame:
        """
        This removes all the leading and trailing blank spaces in the df. This is important so that two values that
        are identical are not mistaken for different ones because of leading and trailing blank spaces.
        :param in_df: df that should be cleaned
        :return: cleaned df
        """
        return in_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

