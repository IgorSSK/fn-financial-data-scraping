import base64
import json
import re
from datetime import datetime
from decimal import Decimal
from time import sleep

import boto3
import requests
from domain.stock import Stock
from domain.stock import Price
from framework.web_driver import WebDriver
from selenium.webdriver.common.by import By


def handler(event, context):
    print('FETCHING WEBSITE...')
    web_driver = WebDriver(connection_url=f'https://www.tradingview.com/markets/stocks-brazil/market-movers-all-stocks/').driver

    print('CLOSING PROPAGANDA...')
    web_driver.find_element(By.CLASS_NAME, 'tv-dialog__close').click()
    sleep(5)

    print('LOADING MORE CONTENT...')
    load_button = web_driver.find_element(By.CLASS_NAME, 'loadButton-Hg5JK_G3')
    load_button.click()
    sleep(5)
    print('LOADING MORE CONTENT...')
    load_button.click()
    sleep(5)

    # table_rows = web_driver.find_elements(By.XPATH, '//table/tbody/tr')
    table = web_driver.find_element(By.XPATH, '//table/tbody')
    rows = table.find_elements(By.TAG_NAME, 'tr')
    print('REGISTERS FOUND: {}'.format(len(rows)))
    print('CONVERTING DATA...')
    data = [mapper(row) for row in rows]
    
    web_driver.quit()

    for stock in data: 
        save(stock)

    print('RETURNING...')
    return {
        "statusCode": 200,
        "body": 'REGISTERS FOUND: {}'.format(len(data))
    }

def mapper(row) -> Stock:
    try:
        cols = row.find_elements(By.TAG_NAME, "td")
        # ticker = driver.find_element(By.XPATH, '//table/tbody/tr[{}]/td[1]'.format(index))
        # symbol = ticker.find_element(By.TAG_NAME, 'a').text
        # name = ticker.find_element(By.TAG_NAME, 'sup').text
        # current_price = driver.find_element(By.XPATH, '//table/tbody/tr[{}]/td[2]'.format(index)).text
        # percentual_change = driver.find_element(By.XPATH, '//table/tbody/tr[{}]/td[3]'.format(index)).text
        # value_change = driver.find_element(By.XPATH, '//table/tbody/tr[{}]/td[4]'.format(index)).text
        # technical_rating = driver.find_element(By.XPATH, '//table/tbody/tr[{}]/td[5]'.format(index)).text
        ticker = cols[0]
        symbol = ticker.find_element(By.TAG_NAME, 'a').text
        name = ticker.find_element(By.TAG_NAME, 'sup').text
        current_price = cols[1].text
        percentual_change = cols[2].text
        value_change = cols[3].text
        technical_rating = cols[4].text
    except Exception as ex:
        print('Error while fetching web elements. {}'.format(ex))
    else:
        price = Price()
        price.price = value_only(current_price)
        price.currency = 'BRL'
        price.percent_change = value_only(percentual_change)
        price.price_change = value_only(value_change)
        price.quotedAt = datetime.now().isoformat()
        price.technical_rating = str(technical_rating).upper().replace(' ', '_')

        stock = Stock()
        stock.name = name
        stock.symbol = symbol
        stock.currency = price.currency
        stock.exchange = 'BMFBOVESPA'
        stock.price = price.price
        stock.percent_change = price.percent_change
        stock.price_change = price.price_change
        stock.technical_rating = price.technical_rating
        stock.price = [price.__dict__]

        try:
            img = ticker.find_element(By.TAG_NAME, 'img').get_attribute("src")
            # stock.company_shortcut = f'data:image/svg+xml;base64,{base64.b64encode(requests.get(img).content)}'
            stock.company_shortcut = img
            img_bigger = img.replace('.sgv', '--big.svg')
            stock.company_img = img_bigger
        except:
            print('Image not found for \'{}\'.'.format(symbol))

        return stock


def value_only(param: str) -> float:
    try:
        value = float(''.join(re.findall('\d|\.|\−|\+', param)).replace('−', '-'))
    except:
        print('Error while converting string to float.')
    else:
        return value

def save(stock: Stock) -> None:
    if(stock == None): return

    dynamodb = boto3.resource('dynamodb', 'us-east-1')
    table = dynamodb.Table('MoneyControl.MarketStocks')


    item = json.loads(json.dumps(stock.__dict__), parse_float=Decimal)
    response = table.put_item(
        Item=item
    )

if __name__ == "__main__":
    handler(None, None)