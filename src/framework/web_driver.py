from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class WebDriver:
    driver: RemoteWebDriver

    def __init__(self, connection_url: str) -> None:
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument('--headless')
        driver_options.add_argument('--no-sandbox')
        driver_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome('chromedriver', options=driver_options)
        self.driver.get(connection_url)
