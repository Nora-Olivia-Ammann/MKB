import pandas as pd


class CleanDF:

    @staticmethod
    def strip_spaces(input_df: pd.DataFrame) -> pd.DataFrame:
        """
        This removes all the leading and trailing blank spaces in the df. This is important so that two values that
        are identical are not mistaken for different ones because of leading and trailing blank spaces.
        :param input_df: df that should be cleaned
        :return: cleaned df
        """
        return input_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

