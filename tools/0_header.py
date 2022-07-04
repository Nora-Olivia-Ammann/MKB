import os
import pandas as pd
import numpy as np
from datetime import date

from sourcetree_code.tools.excel_functions import ExcelFunctions as ExF
from sourcetree_code.tools.beschreibung import Beschreibung as Besch
from sourcetree_code.tools.cleaning_df import CleanDF as Clean
from sourcetree_code.tools.columns_to_string import ColumnsToStr as ColStr
from sourcetree_code.tools.custom_exceptions import *
from sourcetree_code.tools.double_check import DoubleCheck as Double
from sourcetree_code.tools.geographie import Geographie as Geo
from sourcetree_code.tools.inschrift_tranche import Inschrift as Insch
from sourcetree_code.tools.inventarnummer import Inventarnummer as InvNr
from sourcetree_code.tools.key_excel import KeyExcel as KE
from sourcetree_code.tools.modify_excel import ModifyExcel as ModE
from sourcetree_code.tools.NaN_check import NaN as NAN
from sourcetree_code.tools.RegEx_patterns import RegExPattern as RePat
from sourcetree_code.tools.TMS_inschrift import TMSEinlauf as TMSInsch
from sourcetree_code.tools.unique_ID import UniqueID as UID

today = str(date.today())

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)

# , tranche: str, in_excel_name: str
"""
doc_dict = {"Datum": today,
            "Tranche": tranche,
            "Input Dokument": in_excel_name,
            "Schlüssel Excel": "-",
            "Feld": "",
            "Was": "",
            "Resultat": f"",
            "Output Dokument": np.nan,
            "Ersetzt Hauptexcel": ""}
"""


if __name__ == "__main__":
    pass

    file_name = ""
    file_path = os.path.join("_Test_Excel", file_name)
    df = ExF.in_excel_to_df(file_path)

    # function call
    boo, out_df, doc = funct

    print(boo)
    ExF.save_doc_single("Test", doc)
    if out_df is not None:
        ExF.save_df_excel(out_df, "Test")
