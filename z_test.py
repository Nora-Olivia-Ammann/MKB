import os
import pandas as pd
import numpy as np
from datetime import date
from openpyxl import *

wb2 = load_workbook('Test_colour_excel.xlsx')
print(wb2.sheetnames)