import sys
import logging
import getpass

import utils
import seutils
import zipwhip

invalid_cell_no = {'10000000000', '(111) 111-1112', '8888888888', '8615810927190',
                   '4080000000', '420731130518', '4522811819', '(000) 000-0000',
                   '0000000000'}
# Global 'variables'
sms_batch_size = 5
# template = 'Final Day Morning OFF'
template = "Final Hours OFF"


def is_invalid_no(num):
    if num in invalid_cell_no:
        return False
    else:
        return True


utils.config_logging()

# Send text to cell phone numbers in the "Cell Phone" column of the input XLSX file
xlsx = sys.argv[1] if len(sys.argv) > 1 else "LeadsExport.xlsx" 
logging.info(f"Sending text to leads in file {xlsx}")
cdf = utils.read_members_xlsx(xlsx)
# Remove rows with cell number 10000000000
cdf = cdf.loc[cdf['Cell Phone'] != '10000000000']
cdf = cdf["Cell Phone"]
# Drop rows with no cell phone
cdf = cdf.dropna()
cdf.reset_index(drop=True)


driver = None
try:
    zw_login = input("Enter Zipwhip login: ")
    zw_password = getpass.getpass("Enter Zipwhip password: ")
    driver = seutils.open_browser()
    zw = zipwhip.Zipwhip(driver, zw_login, zw_password).login()

    i = 0
    while i <= len(cdf):
        cell_numbers = ",".join(filter(is_invalid_no, cdf[i:i+sms_batch_size].values.flatten().tolist()))
        logging.info(f"Offset: {i} Sending SMS to list") # [{cell_numbers}] using template {template}")
        zw.send_template_sms(cell_numbers, template, stop_if_last_incoming=False)
        i += sms_batch_size
finally:
    driver.close()
