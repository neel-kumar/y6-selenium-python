import sys
import logging
import getpass
import pandas as pd

import utils
import seutils
import zipwhip


sms_batch_size = 50
template = "Holiday Schedule"

# Send emails to cell phone numbers in the "Cell Phone" column of the input XLSX file
utils.config_logging()
xlsx = sys.argv[1] if len(sys.argv) > 1 else "MembersExport.xlsx" 
logging.info(f"Sending emails to leads in file {xlsx}")
df = pd.read_excel(xlsx)
labels = df.iloc[3:4].values.flatten().tolist()
cdf = df.iloc[4:].set_axis(labels, axis=1).reset_index()
# Remove rows with cell number 10000000000
cdf = cdf.loc[cdf['Cell Phone'] != '10000000000']
cdf = cdf["Cell Phone"]


driver = None
try:
    zw_password = getpass.getpass("Enter Zipwhip password: ")
    driver = seutils.open_browser()
    zw = zipwhip.Zipwhip(driver, zw_password).login()

    i = 0
    while i <= len(cdf):
        cell_numbers = ",".join(cdf[i:i+sms_batch_size].values.flatten().tolist())
        logging.info(f"Sending SMS to list [{cell_numbers}] using template {template}")
        zw.send_template_sms(cell_numbers, template, stop_if_last_incoming=False)
        i += sms_batch_size
finally:
    driver.close()
