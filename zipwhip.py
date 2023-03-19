import getpass
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


class Zipwhip():


    # Class variables
    URL = "https://chrome-x.zipwhip.com/"

    find_bys = {
        "template": (By.CSS_SELECTOR, ".message-template-toolip_buttonStyle"),
    }
    # https://www.seleniumeasy.com/selenium-tutorials/examples-for-xpath-and-css-selectors
    # css=div:contains('Cancel 3')

    def __init__(self, driver: webdriver.Chrome, username: str, password: str):
        self.driver = driver
        self.username = username
        self.password = password
        self.window_handle = None


    def switchto(self):
        self.driver.switch_to.window(self.window_handle)
        return self

    def login(self):
        self.driver.switch_to.new_window()
        self.driver.get(Zipwhip.URL)
        self.driver.find_element(By.NAME, "identity").send_keys(self.username)
    
        utils.rsleep()
        seutils.wait_and_scrollto(self.driver, By.CSS_SELECTOR, ".zk-login-button").click()

        utils.rsleep()
        seutils.wait_and_scrollto(self.driver, By.NAME, "password").send_keys(self.password)

        utils.rsleep()
        self.driver.find_element(By.CSS_SELECTOR, ".zk-login-button").click()

        seutils.wait_and_scrollto(self.driver, By.CSS_SELECTOR, ".zk-action-icon-iconElement > path")

        utils.rsleep()
        self.window_handle = self.  driver.current_window_handle
        return self

    # 4085945095,+1 (408) 594-5095,+14085945095
    # All messages including timestamp (latest first) - $$('.zw-default-div-style.message-list_messageListContainer')
    #     Figure out if the most recent message is incoming or outgoing, if incoming, this prospect should be checked manually.
    # Class name of divs for outgoing:
    #     class="message-footer_container message-footer_outbound message-footer_visible"
    #     class="zk-hover message-item_outgoingMessageHover"
    # Class name of divs for incoming:
    #     class="message-footer_container message-footer_inbound message-footer_visible"
    #     class="zk-hover message-item_incomingMessageHover"
    # All outgoing messages (text only, not timestamp) latest first - $$('.message-item_outgoingMessageHover')
    # All incoming messages (text only, not timestamp) latest first - $$('.message-item_incomingMessageHover')
    #     If latest incoming message is STOP, don't send sms
    #     Most recent incoming text - $$('.message-item_incomingMessageHover')[0].innerText - this value is 'stop' - case-insensitive

    def __select_non_group_contact(self):
        contact_list = self.driver.find_elements(By.CLASS_NAME, "zk-selectable-list_listItemWrapper")
        # If there are more than one contact, then select the one whose name does not begin with "Group"
        if len(contact_list) == 1:
            contact_list[0].click()
        else:
            i = 0
            done = False
            while i < len(contact_list) and not done:
                tmp = contact_list[i].find_element(By.CLASS_NAME, "to-box_contact-card-wrapper_contact-name")
                if not tmp.text.startswith("Group"):
                    logging.info(f"Selecting non-group contact {tmp.text} to send SMS")
                    contact_list[i].click()
                    done = True
                i = i + 1


    def __customer_stopped(self, cell: str) -> bool:
        stopped = False
        if seutils.waitfor_catch(self.driver, By.CSS_SELECTOR, ".message-item_incomingMessageHover"):
            incoming_msgs = self.driver.find_elements(By.CSS_SELECTOR, ".message-item_incomingMessageHover")
            stoppped = incoming_msgs and len(incoming_msgs) > 0 and incoming_msgs[0].text.strip().lower() == "stop"
        
        if stopped:
            logging.error(f"Not sending SMS to cell {cell}, since latest incoming text is STOP")
        
        return stopped


    def __is_latest_incoming_text(self, cell: str) -> bool:
        latest_incoming = False
        all_msgs = self.driver.find_elements(By.CSS_SELECTOR, ".zw-default-div-style.message-list_messageListContainer")
        if all_msgs and len(all_msgs) > 0:
            msg = all_msgs[0]
            divs = msg.find_elements(By.TAG_NAME, "div")
            if divs and len(divs) > 0:
                cls = divs[0].get_attribute("class")
                latest_incoming = ("inbound" in cls) or ("incoming" in cls)
        
        if latest_incoming:
            logging.error(f"Not sending SMS to cell {cell}, since latest text is incoming, so text manually instead")

        return latest_incoming


    def send_sms(self, cell: str, sms: str):
        self.switchto()
        self.driver.get(Zipwhip.URL)
        # wait_and_scrollto(driver, By.CSS_SELECTOR, ".zk-action-icon-iconElement > path").click()
        seutils.wait_and_scrollto(self.driver, By.CSS_SELECTOR, "button.conversation-list-panel_newMessage").click()
        self.driver.find_element(By.CSS_SELECTOR, ".zk-text-input").send_keys(cell)

        sent = False
        # Select the right contact from the matches found
        contact = seutils.waitfor_catch(self.driver, By.CLASS_NAME, "zk-selectable-list_listItemWrapper")
        if contact:
            self.__select_non_group_contact()
            if not self.__customer_stopped(cell):
                sms_element = seutils.waitfor_catch(self.driver, By.CSS_SELECTOR, ".zk-text-editor_input")
                if sms_element:
                    # If latest incoming msg is STOP, sms field may not show up
                    sms_element.send_keys(sms)
                    #self.driver.find_element(By.CSS_SELECTOR, ".zk-text-editor_input").send_keys(sms)
                    # Click to send
                    self.driver.find_element(By.CSS_SELECTOR, ".zk-button-label-primary").click()
                    sent = True
                else:
                    logging.error(f"SMS element not found for cell number {cell}, check if the recent incoming sms is STOP")
        else:
            logging.error(f"No contact found for cell number {cell}")
        
        utils.rsleep_within(2000, 4000)
        return sent


    def send_template_sms(self, cell: str, template_name: str, stop_if_last_incoming: bool = True, click_send: bool = True) -> bool:
        self.switchto()
        self.driver.get(Zipwhip.URL)
        seutils.wait_and_scrollto(self.driver, By.CSS_SELECTOR, "button.conversation-list-panel_newMessage").click()
        self.driver.find_element(By.CSS_SELECTOR, ".zk-text-input").send_keys(cell)

        # Select the right contact from the matches found
        contact_found = False
        contact = seutils.waitfor_catch(self.driver, By.CLASS_NAME, "zk-selectable-list_listItemWrapper")
        if contact:
            contact_found = True
            self.__select_non_group_contact()
        else:
            logging.debug(f"No contact found for cell number {cell}")

        sent = False
        if not self.__customer_stopped(cell) and (not stop_if_last_incoming or not self.__is_latest_incoming_text(cell)):
            kv = Zipwhip.find_bys['template']
            
            # Wait for the template selector dropdown
            tmp = seutils.waitfor_catch(self.driver, kv[0], kv[1])
            if tmp:
                seutils.wait_and_scrollto(self.driver, kv[0], kv[1]).click()
                template = f"//div[text()='{template_name}']"
                logging.debug(f"cell number: {cell}, selecting template: {template} for selector: {template_name}")
                # self.driver.find_element(By.CSS_SELECTOR, template).click()
                seutils.wait_and_scrollto(self.driver, By.XPATH, template).click()

                send_button = seutils.wait_and_scrollto_catch(self.driver, By.CSS_SELECTOR, ".zk-button-primary")
                if send_button:
                    if click_send:
                        # Click to send
                        send_button.click()
                        sent = True
                    else:
                        logging.info(f"Did not click on send button for cell number {cell}")
                else:
                    logging.error(f"cell number {cell}, selected template {template}, but send button is not enabled/found. Contact found: {'YES' if contact_found else 'NO'}")
            else:
                logging.error(f"Template selector element not found for cell number {cell}, check if the recent incoming sms is STOP")

        utils.rsleep_within(2000, 4000)
        return sent


if __name__ == '__main__':
    utils.config_logging()
    driver = None
    try:
        zw_password = getpass.getpass("Enter Zipwhip password: ")
        driver = seutils.open_browser()
        zw = Zipwhip(driver, zw_password).login(1)
        # zw.send_template_sms("4085945095,+1 (408) 594-5095,+14085945095", "Cancel 1", click_send=False)
        zw.send_template_sms("4085945095", "Cancel 1", click_send=True)
        zw.send_template_sms("4085945095", "Cancel 1", stop_if_last_incoming=False)
        #zw.send_template_sms("4085308371", "Cancel 1", click_send=False)
        #zw.send_template_sms("(650) 464-3073", "Cancel 1", click_send=False)
        # Ruthie Reyes details: ('New Unscheduled Day 3', '8312366306') sms template Day 3
        zw.send_template_sms("8312366306", "Day 3")

    finally:
        driver.close()
