# https://selenium-python.readthedocs.io/getting-started.html

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_extension("resources/Zipwhip-Extension-1.1.1.0.crx")
driver = webdriver.Chrome(options=options)
driver.get("http://www.python.org")
assert "Python" in driver.title
elem = driver.find_element(By.NAME, "q")
elem.clear()
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
print(f"Title of page is {driver.title}")
driver.switch_to.new_window()
driver.get("https://chrome-x.zipwhip.com/")
print(f"Title of page is {driver.title}")
input("Please enter to terminate the program: ")
driver.close()
