import pandas as pd


class CleanDF:

    @staticmethod
    def strip_spaces_whole_df(input_df: pd.DataFrame) -> pd.DataFrame:
        """
        This removes all the leading and trailing blank spaces in the df. This is important so that two values that
        are identical are not mistaken for different ones because of leading and trailing blank spaces.
        :param input_df: df that should be cleaned
        :return: cleaned df
        """
        return input_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    @staticmethod
    def strip_spaces_col(input_df: pd.DataFrame, col_name: str) -> pd.DataFrame:
        """
        Removes all the leading and trailing spaces of a column in a df.
        :param col_name: Column name that should be striped
        :param input_df: df that should be cleaned
        :return: cleaned df
        """
        return input_df.apply(func=lambda x: x.strip if isinstance(x is str) else x, axis=col_name)


if __name__ == '__main__':
    pass
