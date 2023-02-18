from selenium import webdriver
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def open_browser():
    options = webdriver.ChromeOptions()
    options.add_extension("resources/Zipwhip-Extension-1.1.1.0.crx")
    return webdriver.Chrome(options=options)


def scrollto(driver, element):
    actions = ActionChains(driver)
    actions.scroll_to_element(element).move_to_element(element).perform()
    return element


def waitfor(driver: webdriver.Chrome, by: str, value: str, timeout: float = 10) -> webelement:
    # https://stackoverflow.com/questions/52400233/error-other-element-would-receive-the-click-in-python
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((by, value))
    )
    return element


def waitfor_catch(driver: webdriver.Chrome, by: str, value: str, timeout: float = 10) -> webelement:
    try:
        return waitfor(driver, by, value, timeout)
    except:
        return None


def wait_and_scrollto(driver: webdriver.Chrome, by: str, value: str, timeout: float = 10) -> webelement:
    element = waitfor(driver, by, value, timeout)
    return scrollto(driver, element)


def wait_and_scrollto_catch(driver: webdriver.Chrome, by: str, value: str, timeout: float = 10) -> webelement:
    element = waitfor_catch(driver, by, value, timeout)
    if element:
        return scrollto(driver, element)
    
    return None
