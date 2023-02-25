import sys
import logging
import getpass

import utils
import seutils
import zipwhip


# Global variables
sms_batch_size = 50
template = "Holiday Schedule"

utils.config_logging()

# Send text to cell phone numbers in the "Cell Phone" column of the input XLSX file
xlsx = sys.argv[1] if len(sys.argv) > 1 else "MembersExport.xlsx" 
logging.info(f"Sending text to leads in file {xlsx}")
cdf = utils.read_members_xlsx(xlsx)
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
