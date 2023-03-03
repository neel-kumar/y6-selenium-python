import sys
import logging
import getpass
import traceback
from PIL import Image

from selenium import webdriver
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# https://iq-inc.com/importerror-attempted-relative-import/
import utils
import seutils
import zipwhip
import clubready


def exception_handler():
    global driver

    logging.error("Exception caught!")
    traceback.print_exc()
    driver.save_screenshot("error.png")
    screenshot = Image.open("error.png")
    screenshot.show()


def setup(studio_selector):
    global driver
    global zw
    global club_ready

    club_ready_password = getpass.getpass("Enter ClubReady password: ")
    zw_password = getpass.getpass("Enter Zipwhip password: ")

    driver = seutils.open_browser()

    club_ready = clubready.ClubReady(driver, club_ready_password).login(studio_selector)
    zw = zipwhip.Zipwhip(driver, zw_password).login()
    

def test():
    global driver
    global zw
    global club_ready

    zw.send_sms("4085945095", 'Day 3')
    zw.send_sms("xxxxxxxxxxx", 'Day 3')
    zw.send_template_sms("4085945095", 'Day 3')
    zw.send_template_sms("4085945095", 'Missed Sale Day 3')

    zw.send_sms("(650) 796-1099", 'Day 3')
    zw.send_template_sms("(650) 796-1099", 'Day 3')

    zw.send_sms("4085308271", 'Day 3')
    zw.send_template_sms("4085308271", 'Day 3')

    club_ready.switchto()
    logging.info(f"Title of ClubReady page is {driver.title}")

    zw.switchto()
    logging.info(f"Title of Zipwhip page is {driver.title}")


def work_on_prospects():
    global driver
    global zw
    global club_ready

    run = True
    while run:
        try:
            club_ready.work_on_prospects_tasks(zw)
            # Done working on prospects
            y = input("Done working on prospects, do you want to rerun workit (press y)? ")
            if y != "y":
                run = False
            else:
                club_ready.reset_worked_on()
        except Exception:
            exception_handler()
            y = input("Check the screenshot, work on the browser and press y if you want me to continue on working on prospects: ")
            if y != "y":
                run = False


# Global variable
driver = None
zw = None
club_ready = None


# main program
try:
    # 1 is Campbell and 2 is Saratoga
    studio_selector = int(sys.argv[1]) if len(sys.argv) > 1 else 1 
    utils.config_logging()
    setup(studio_selector)
    work_on_prospects()
except Exception:
    exception_handler()
    input("Please enter when you are done with the error screenshot to exit the program: ")
finally:
    #input("Please enter to terminate the program: ")
    #print(driver.page_source)
    driver.close()
