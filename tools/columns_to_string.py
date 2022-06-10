import os
import pandas as pd
import numpy as np
from datetime import date

from excel_functions import ExcelFunctions as ExF
from cleaning_df import CleanDF as Clean

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class ColumnsToStr:

    @staticmethod
    def join_col_to_str(in_data: str or pd.DataFrame, col_list: list[str], name_list: list[str] or False,
                        new_col_name: str, tranche: str or None = None, abteilung: str or None = None,
                        is_excel: bool = False) -> pd.DataFrame or None:
        """
        For each row it gets the information from a list of columns and if it is not NaN enters that as a str into a new
        column. A prefix (such as column name or similar) for each column can be added. If this function is used with an
        excel as input it writes the documentation.
        :param in_data: excel / df
        :param is_excel: True if excel
        :param col_list: list of column names that should be included
        :param name_list: names of the prefix for every column MUST BE SAME LENGTH AS LIST OF COLUMNS or False if no prefix
        :param new_col_name: name of the column where the resulting str should be entered
        :param tranche: name
        :param abteilung: name or df_doc if not excel
        :return: df or none
        """
        if is_excel:
            # read the excel into a dataframe
            df_in = pd.read_excel(io=os.path.join(current_wdir, "input", f"{in_data}.xlsx"))
            df_doc = pd.read_excel(
                os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))
        else:
            df_in = in_data
        # clean the df
        df_in = Clean.strip_spaces(df_in)
        # iterate over the column list that contains information that should be joined into a str
        for col in col_list:
            # check if the column contains only NaN values, if it does then it doesn't skip them and you get nan in the
            # resulting str
            if df_in[col].isnull().all():
                # get the index of the column
                ind = col_list.index(col)
                # remove the NaN colum from both lists
                col_list.pop(ind)
                if name_list is not False:
                    name_list.pop(ind)
        # iterate over the rows of the df
        for index, row in df_in.iterrows():
            # initiate an empty list to store the values form the columns
            besch = []
            # with an index range iterate over the column and name list
            for i in range(0, len(col_list)):
                # check if the singular cell is nan, if yes skip
                if row[col_list[i]] is not np.nan:
                    # get the value from the cell
                    val = row[col_list[i]]
                    # if we have a prefix, add that
                    if name_list is not False:
                        besch.append(f"{name_list[i]}: {val}")
                    # if not only append the value
                    else:
                        besch.append(val)
            # if that row had no values we get an empty list
            if len(besch) == 0:
                b_str = np.nan
            # otherwise we join the list, if there is only one value it does not add the "; "
            else:
                b_str = "; ".join(besch)
            # add the string the the new_column
            df_in.loc[index, new_col_name] = b_str
        if is_excel:
            df_doc = pd.concat([df_doc, pd.DataFrame(
                {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": "-",
                 "Feld": new_col_name, "Was": f"Info hinzufügen",
                 "Resultat": f"Info von Spalte: '{col_list}' in neue Spalte {new_col_name}",
                 "Output Dokument": f"{tranche}_{today}", "Ersetzt Hauptexcel": "ja"}, index=[0])], ignore_index=True)
            # save df
            ExF.save_df_excel(df_in, f"{tranche}_{today}")
            ExF.save_doc_excel(df_doc, abteilung)
        else:
            return df_in

    # # with Prefix
    # join_col_to_str(in_data="a_Test_join_col_to_str", is_excel=True, col_list=["Col1", "Col2", "Col3", "Col4"],
    #                 name_list=["N1", "N2", "N3", "N4"], new_col_name="New_Col", tranche="Test", abteilung="Test")
    #
    # # without Prefix
    # join_col_to_str(in_data="a_Test_join_col_to_str", is_excel=True, col_list=["Col1", "Col2", "Col3", "Col4"],
    #                 name_list=False, new_col_name="New_Col", tranche="Test", abteilung="Test")


if __name__ == "__main__":
    pass
