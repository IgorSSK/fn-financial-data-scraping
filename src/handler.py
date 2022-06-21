import json
from framework.web_driver import WebDriver
from domain.stock import Stock
from selenium.webdriver.common.by import By

def stock(event, context):
    web_driver = WebDriver(connection_url=f'https://www.tradingview.com/symbols/BMFBOVESPA-{event.symbol}/').driver

    stock = Stock()

    main_el = web_driver.find_element(by=By.XPATH, value='//*[@id="anchor-page-1"]')
    img_el = main_el.find_element(by=By.TAG_NAME, value='img').get_attribute("src")
    header_el = main_el.find_element(by=By.XPATH, value='//*[@class="tv-category-header__title "]').text

    symbol_price_el = main_el.find_element(by=By.XPATH, value='//*[@class="tv-symbol-price-quote js-last-price-block"]/div/*[1]').text

    symbol, name, exchange = title.split('\n')

    return {
        "statusCode": 200,
        "body": json.dumps(stock)
    }

# def hello(event, context):
#     body = {
#         "message": "Go Serverless v1.0! Your function executed successfully!",
#         "input": event
#     }

#     response = {
#         "statusCode": 200,
#         "body": json.dumps(body)
#     }

#     return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    # return {
    #     "message": "Go Serverless v1.0! Your function executed successfully!",
    #     "event": event
    # }
