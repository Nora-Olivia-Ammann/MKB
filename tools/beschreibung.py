import pandas as pd


class Beschreibung:

    @staticmethod
    def add_str_to_beschreibung(input_df: pd.DataFrame, source_col: str, prefix_text: str,
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
        # iterate over the rows
        for index, source_val in input_df[source_col].iteritems():
            # if this is not done this way but with try and except to cach the errors of the NaN, it adds the 'nan' as a
            # string to the beschreibung. Therefore it will only be done if it is indeed of type string
            if type(source_val) == str:
                # get the value in the Beschreibung
                besch_str = input_df["Beschreibung"][index]
                # check if they are a str, if they are empty they are not str
                if type(besch_str) == str:
                    # partition at the bracket
                    partitioned = list(besch_str.rpartition("}"))
                    # this way no values that may come after the bracket will be lost
                    # insert the information before the bracket
                    partitioned.insert(1, f", {prefix_text}{source_val}")
                    # join the items of the list and assign them into the Beschreibung
                    input_df.loc[index, "Beschreibung"] = "".join(partitioned)
                # if the Beschreibung does not contain a string (NaN), just insert the value
                else:
                    input_df.loc[index, "Beschreibung"] = f"{prefix_text}{source_val}"
            # skip the row if it contains NaN
        # write documentation
        # input_doc = pd.concat([input_doc, pd.DataFrame(
        #     {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": "-",
        #      "Feld": "Beschreibung",
        #      "Was": f"Information ergänzen",
        #      "Resultat": f"Info von Spalte: '{source_col}', zu Beschreibung mit Präfix: '{prefix_text}'",
        #      "Output Dokument": f"{tranche}_{today}", "Ersetzt Hauptexcel": "ja"}, index=[0])], ignore_index=True)
        return input_df

    # add_str_to_beschreibung(in_data="a_Test_add_str_to_beschreibung", is_excel=True, abteilung="Test", tranche="Test",
    #                         source_col="P1 Fotograf*in/Filmer*in", prefix_text="")

    @staticmethod
    def add_schublade(input_df: pd.DataFrame, tranche: str or None = None, abteilung: str or None = None):
        """
        Adds the name of the Schublade, to the Beschreibung after the number of the Schublade.
        :param input_df:
        :param tranche: name
        :param abteilung: name or df_doc if not excel
        :return: df or None
        """
        for index, row in input_df.iterrows():
            besch_spl = row["Beschreibung"].split(",")
            try:
                index_res = [ind for ind, word in enumerate(besch_spl) if word.startswith("(F)")][0]
            # in some cases a blank space precedes the (F) which leads to an IndexError
            except IndexError:
                index_res = [ind for ind, word in enumerate(besch_spl) if word.startswith(" (F)")][0]
            try:
                besch_spl.insert(index_res + 1, row["Schubladen Beschriftung"])
                input_df.loc[index, "Beschreibung"] = ",".join(besch_spl)
            except TypeError:
                pass
        # input_docu = pd.concat([input_docu, pd.DataFrame(
        #     {"Datum": today, "Tranche": tranche, "Input Dokument": in_data, "Schlüssel Excel": "-",
        #      "Feld": "Beschreibung", "Was": "Hinzufügen Schubladenname", "Resultat": f"erfolgreich hinzugefügt",
        #      "Output Dokument": f"{tranche}_{today}", "Ersetzt Hauptexcel": "ja"}, index=[0])], ignore_index=True)
        else:
            return input_df

    # add_schublade("_Test_Tranche_Neu_Formatiert_Kurz", is_excel=True, tranche="Test", abteilung="Test")


if __name__ == "__main__":
    pass
