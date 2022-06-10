import os
from datetime import date
import pandas as pd

from save_excel import SaveExcel as SE

today = str(date.today())
os.chdir("..")
current_wdir = os.getcwd()

############################################
# Suppress the SettingWithCopyWarning
pd.set_option("mode.chained_assignment", None)


class Beschreibung:

    @staticmethod
    def add_str_to_beschreibung(in_data: str or pd.DataFrame, source_col: str, prefix_text: str,
                                is_excel: bool = False, abteilung: str or None = None, tranche: str or None = None) \
            -> None or pd.DataFrame:
        """
        Adds the value from one column to the Beschreibung column.
        :param in_data: excel
        :param is_excel: True: if it is excel
        :param abteilung: name
        :param tranche: name
        :param source_col: Value that should be added to Beschreibung
        :param prefix_text: if not Prefix is wished then write "", otherwise a set Prefix (e.g. "Photo: ")
        :return: if not excel: df
        """
        if is_excel:
            # read the excel
            df_in = pd.read_excel(os.path.join(current_wdir, "input", "", f"{in_data}.xlsx"))
            # read the documentation excel
            df_doc = pd.read_excel(
                os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))
        else:
            df_in = in_data
            df_doc = abteilung
        # iterate over the rows
        for index, source_val in df_in[source_col].iteritems():
            # if this is not done this way but with try and except to cach the errors of the NaN, it adds the 'nan' as a
            # string to the beschreibung. Therefore it will only be done if it is indeed of type string
            if type(source_val) == str:
                # get the value in the Beschreibung
                besch_str = df_in["Beschreibung"][index]
                # check if they are a str, if they are empty they are not str
                if type(besch_str) == str:
                    # partition at the bracket
                    partitioned = list(besch_str.rpartition("}"))
                    # this way no values that may come after the bracket will be lost
                    # insert the information before the bracket
                    partitioned.insert(1, f", {prefix_text}{source_val}")
                    # join the items of the list and assign them into the Beschreibung
                    df_in.loc[index, "Beschreibung"] = "".join(partitioned)
                # if the Beschreibung does not contain a string (NaN), just insert the value
                else:
                    df_in.loc[index, "Beschreibung"] = f"{prefix_text}{source_val}"
            # skip the row if it contains NaN
        # write documentation
        df_doc = pd.concat([df_doc, pd.DataFrame(
            {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": "-",
             "Feld": "Beschreibung",
             "Was": f"Information ergänzen",
             "Resultat": f"Info von Spalte: '{source_col}', zu Beschreibung mit Präfix: '{prefix_text}'",
             "Output Dokument": f"{tranche}_{today}", "Ersetzt Hauptexcel": "ja"}, index=[0])], ignore_index=True)
        if is_excel:
            # save df
            SE.save_df_excel(df_in, f"{tranche}_{today}")
            SE.save_doc_excel(df_doc, abteilung)
        else:
            return df_in

    # add_str_to_beschreibung(in_data="a_Test_add_str_to_beschreibung", is_excel=True, abteilung="Test", tranche="Test",
    #                         source_col="P1 Fotograf*in/Filmer*in", prefix_text="")

    @staticmethod
    def add_schublade(in_data: pd.DataFrame or str, tranche: str or None = None, abteilung: str or None = None,
                      is_excel: bool = False):
        """
        Adds the name of the Schublade, to the Beschreibung after the number of the Schublade.
        :param in_data: excel / df
        :param is_excel: True if excel
        :param tranche: name
        :param abteilung: name or df_doc if not excel
        :return: df or None
        """
        if is_excel:
            # read the excel
            df_in = pd.read_excel(os.path.join(current_wdir, "input", "", f"{in_data}.xlsx"))
            # read the documentation excel
            df_doc = pd.read_excel(
                os.path.join(current_wdir, "output", "_dokumentation", f"{abteilung}_Dokumentation.xlsx"))
        else:
            df_in = in_data
            df_doc = abteilung

        for index, row in df_in.iterrows():
            besch_spl = row["Beschreibung"].split(",")
            try:
                index_res = [ind for ind, word in enumerate(besch_spl) if word.startswith("(F)")][0]
            # in some cases a blank space precedes the (F) which leads to an IndexError
            except IndexError:
                index_res = [ind for ind, word in enumerate(besch_spl) if word.startswith(" (F)")][0]
            try:
                besch_spl.insert(index_res + 1, row["Schubladen Beschriftung"])
                df_in.loc[index, "Beschreibung"] = ",".join(besch_spl)
            except TypeError:
                pass
        if is_excel:
            df_doc = pd.concat([df_doc, pd.DataFrame(
                {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": "-",
                 "Feld": "Beschreibung", "Was": "Hinzufügen Schubladenname", "Resultat": f"erfolgreich hinzugefügt",
                 "Output Dokument": f"{tranche}_{today}", "Ersetzt Hauptexcel": "ja"}, index=[0])], ignore_index=True)
            SE.save_df_excel(df_in, f"{tranche}_{today}")
            SE.save_doc_excel(df_doc, abteilung)
        else:
            return df_in

    # add_schublade("_Test_Tranche_Neu_Formatiert_Kurz", is_excel=True, tranche="Test", abteilung="Test")


if __name__ == "__main__":
    pass
