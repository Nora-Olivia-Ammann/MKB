"""
The general Exceptions that are inbuilt in Python are not specific enough when raising Errors during a function.
Therefore, custom Exceptions are created that print a specific message when raised.
"""


class TrancheMissingValue(Exception):
    def __init__(self, message):
        super().__init__(message)


class KeyDocIncomplete(Exception):
    def __init__(self, message):
        super().__init__(message)


class MissingKey(Exception):
    def __init__(self, message):
        super().__init__(message)


class DoubleGeoIDError(Exception):
    def __init__(self, message="Geo ID has doubles this is not allowed."):
        super().__init__(message)


class ColumnExistsError(Exception):
    def __init__(self, message):
        super().__init__(message)
