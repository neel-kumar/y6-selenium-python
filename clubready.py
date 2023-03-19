import time
import logging

from selenium import webdriver
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import utils
import seutils


# unused
def open_prospect(name: str, driver: webdriver.Chrome):
    driver.find_element(By.LINK_TEXT, "Prospects").click()
    driver.find_element(By.ID, "stshow").send_keys(name)

    utils.rsleep()
    driver.find_element(By.XPATH, "xpath=//table[@id='reslist']/tbody/tr[1]/td/div/table/tbody/tr/td/span").click()


class ClubReady():


    # Class variables
    prospect_type_2_sms_template = {
        'New Unscheduled Day 1': 'Day 1',
        'New Unscheduled Day 3': 'Day 3',
        'New Unscheduled Day 7': 'Day 7',
        'New Unscheduled Day 14': 'Day 14',
        'New Unscheduled Day 30': 'Day 30',
        'Missed Sale - Day 1': 'Missed Sale Day 1',
        'Missed Sale Day 1': 'Missed Sale Day 1',
        'Missed Sale Day 3': 'Missed Sale Day 3',
        'Missed Sale Day 7': 'Missed Sale Day 1',
        'Missed Sale Day 14': 'Missed Sale Day 3',
        'Missed Sale Day 30': 'Missed Sale Day 1',
        'Day Prior Booking Confirmation': 'Class Reminder',
        'No Show Day 1': 'Cancel 1',
        'No Show Day 3': 'Cancel 2',
        'No Show Day 7': 'Cancel 3',
        'No Show Day 14': 'Cancel 7',
        'No Show Day 30' : 'Cancel 7',
        #'No Show Day 30': ''
        'No Show - Same Day': 'Cancel 1',
        'Same Day': 'Day 1',
        'Renewed Interest - Day 1': 'Day 1',
        'Renewed Interest - Day 3': 'Day 3',
        'Renewed Interest - Day 7': 'Day 7',
        'Renewed Interest - Day 14': 'Day 14',
        'Renewed Interest - Day 30': 'Day 30',
        'Cancelled Booking': 'Cancel 1',
        'Cancelled Booking Day 1': 'Cancel 1',
        'Cancelled Booking Day 3': 'Cancel 3',
        'Cancelled Booking Day 7': 'Cancel 4',
        'Cancelled Booking Day 14': 'Cancel 7',
        'Cancelled Booking Day 30': 'Cancel 1',
        'Main Page Inquiry Day 1': 'Day 1',
        'Main Page Inquiry Day 3': 'Day 3',
        'Main Page Inquiry Day 7': 'Day 7',
        'Main Page Inquiry Day 14': 'Day 14',
        'Main Page Inquiry Day 7': 'Day 7',
        'Intro Offer - First Week for $26': 'Introduction to Yoga - Harvard',
        '$26 Intro Week Missed Sale - Day 1': 'Why YogaSix?',
        '$26 Intro Week Missed Sale - Day 7': 'Missed Sale Day 1',
        '$26 Intro Week Missed Sale - Day 14': 'Missed Sale Day 3',
        '$26 Intro Week Missed Sale - Day 30': 'Missed Sale Day 3',
        '$26 Intro Week - Day 4 of 7 - Intro Offer Check In': 'Introduction to Yoga - Harvard',
        '10 pack - 1 session left': '10 classpack 1',
        '10 pack - 3 session left - Check In': '10 classpack 3',

        # Presale Studio
        'Presale Lead - Day 3' :'Day 3',
        'Presale Lead - Day 7' :'Day 7',
        'Presale Lead - Day 1' :'Day 1',
        'Presale Lead - Day 14' :'Day 14',
        'Presale Lead - Day 30' :'Day 30',
        'Presale Lead - Day 60' :'Day 60',
        'Presale Lead Same Day' :'Day 1',
        'Presale Contacted - Needs Follow Up Task' :'',

    }


    def __init__(self, driver: webdriver.Chrome, username: str, password: str):
        self.driver = driver
        self.username = username
        self.password = password
        self.window_handle = None
        self.reset_worked_on()


    def switchto(self):
        self.driver.switch_to.window(self.window_handle)
        return self


    def reset_worked_on(self):
        # Ignore 10000000000 cell number
        self.worked_on = {'10000000000'}

    def login(self):
        self.driver.get("https://www.clubready.com/cl/yogasix.asp")
        # Enter login/password
        self.driver.find_element(By.ID, "uid").send_keys(self.username)
        self.driver.find_element(By.ID, "pw").send_keys(self.password)
    
        utils.rsleep()
        self.driver.find_element(By.NAME, "submit").click()
    
        # utils.rsleep()
        # self.driver.find_element(By.NAME, "Submit2").click()

        utils.rsleep()
        self.window_handle = self.driver.current_window_handle
        return self


    def work_on_prospect(self, name, workit, details, zw):
        if details and details[0] in ClubReady.prospect_type_2_sms_template:
            sms_template = ClubReady.prospect_type_2_sms_template[details[0]]
            logging.info(f"Working on name: {name} details: {details} sms template: {sms_template}")
            if zw.send_template_sms(details[1], sms_template):
                # Add to worked set. If Selenium fails while logging the phone call, user must do it manually.
                self.worked_on.add(details[1])
                self.switchto()
                workit.click()
                select = Select(seutils.wait_and_scrollto(self.driver, By.ID, "thecalloutcome"))
                select.select_by_visible_text("voicemail - didn't leave message")
                self.driver.find_element(By.ID, "callnoteentry").send_keys("Automated")

                self.driver.find_element(By.ID, "LogThePhoneCallButtonWorkIt").click()

                # TODO: Wait to be invisible - <div class="toast toast-success" style="">...</div>
                time.sleep(6)
                seutils.wait_and_scrollto(self.driver, By.CSS_SELECTOR, ".fancybox-close").click()
            else:
                # Mark this prospect as done, since the text will not be sent if user has stopped or recent text is incoming.
                # If you don't add to worked set, then it will in infinite loop!
                self.worked_on.add(details[1])
                self.switchto()
        elif details and details[0] not in ClubReady.prospect_type_2_sms_template:
            logging.error(f"No template provided for {details[0]}")
            self.worked_on.add(details[1])
            
        utils.rsleep_long()


    def find_first_to_work_on(self, todorows):
        for row in todorows:
            # seutils.scrollto(self.driver, row) # Quite often fails as: selenium.common.exceptions.ElementNotInteractableException: Message: element not interactable: [object HTMLDivElement] has no size and location
            tds = row.find_elements(By.TAG_NAME, "td")
            workit = tds[1].find_element(By.TAG_NAME, "span")
            name = tds[2].text

            prospect_text = tds[4].text
            if len(prospect_text) == 0:
                # Try to grab from span element
                prospect_text = tds[4].find_element(By.TAG_NAME, "span").text

            if len(prospect_text) > 0:
                details = utils.Utils.get_prospect_details(prospect_text)
                if details:
                    if details[1] not in self.worked_on:
                        logging.debug(f"Found prospect to work on name: {name} text: {prospect_text} details: {details}")
                        return (name, workit, details)
                else:
                    logging.error(f"Could not extract prospect type and/or cell phone from text: {prospect_text}")
            else:
                logging.debug(f"Empty prospect_text for row {tds[4].get_property('outerHTML')}")

        return None


    def work_on_prospects_tasks(self, zw):
        self.switchto()
        self.driver.find_element(By.LINK_TEXT, "Prospects").click()
        seutils.wait_and_scrollto(self.driver, By.ID, "mtab1").click()
        seutils.wait_and_scrollto(self.driver, By.CSS_SELECTOR, ".dd-select").click()
        seutils.wait_and_scrollto(self.driver, By.CSS_SELECTOR, "li:nth-child(1) .dd-option-text").click()
        tasks = (int)(self.driver.find_element(By.ID, "alltodocount").text)
        if tasks > 0:
            logging.info(f"There are {tasks} tasks to work on")
            # Prevent selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: element is not attached to the page document
            utils.rsleep_long()
            todorows = self.driver.find_elements(By.CLASS_NAME, "toddowrow")
            work_on = self.find_first_to_work_on(todorows)
            while work_on:
                self.work_on_prospect(work_on[0], work_on[1], work_on[2], zw)
                todorows = self.driver.find_elements(By.CLASS_NAME, "toddowrow")
                work_on = self.find_first_to_work_on(todorows)

        else:
            logging.error("No task to work on")


        return self


if __name__ == '__main__':
    pass
