import base64
import json
import re
from datetime import datetime
from decimal import Decimal
from time import sleep

import boto3
import requests
from domain.stock import Stock
from domain.stock import Quote
from framework.web_driver import WebDriver
from selenium.webdriver.common.by import By


def handler(event, context):
    print('FETCHING WEBSITE...')
    web_driver = WebDriver(connection_url=f'https://www.tradingview.com/markets/stocks-brazil/market-movers-all-stocks/').driver

    # try:
    #     print('CLOSING PROPAGANDA...')
    #     web_driver.find_element(By.CLASS_NAME, 'tv-dialog__close').click()
    #     sleep(5)
    # except:
    #     print('Nothing to close.')
        
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
        sector = cols[11].text
    except Exception as ex:
        print('Error while fetching web elements. {}'.format(ex))
    else:
        quote = Quote()
        quote.price = value_only(current_price)
        quote.currency = 'BRL'
        quote.percent_change = value_only(percentual_change)
        quote.price_change = value_only(value_change)
        quote.quoted_at = datetime.now().isoformat()
        quote.technical_rating = str(technical_rating).upper().replace(' ', '_')

        stock = Stock()
        stock.name = name
        stock.symbol = symbol
        stock.exchange = 'BMFBOVESPA'
        stock.sector = sector.upper().replace(' ', '_').replace('-', '')
        stock.quote = quote

        try:
            img = ticker.find_element(By.TAG_NAME, 'img').get_attribute("src")
            # stock.company_shortcut = f'data:image/svg+xml;base64,{base64.b64encode(requests.get(img).content)}'
            stock.company_shortcut = img
            img_bigger = img.replace('.svg', '--big.svg')
            stock.company_img = img_bigger
        except:
            print('Image not found for \'{}\'.'.format(symbol))
            stock.company_shortcut = ''
            stock.company_img = ''

        return stock


def value_only(param: str) -> float:
    try:
        value = float(''.join(re.findall('\d|\.|\−|\+', param)).replace('−', '-'))

        if param.find('−') > 0 | param.find('-') > 0: 
            return -value 
        else:
            return value
    except:
        print('Error while converting string to float.')

def save(stock: Stock) -> None:
    if(stock == None): return

    dynamodb = boto3.resource('dynamodb', 'us-east-1')
    table = dynamodb.Table('MoneyControl.MarketStocks')

    print(stock.__dict__)

    quote = json.loads(json.dumps(stock.quote.__dict__), parse_float=Decimal)
    response = table.update_item(
            Key={"symbol": stock.symbol},
            UpdateExpression="""SET #nm = :name,
                                    company_img = :img,
                                    company_shortcut = :shortcut,
                                    exchange = :exchange,
                                    sector = :sector,
                                    quote = :quote,
                                    timeline = list_append(if_not_exists(timeline, :empty_list), :timeline)""",
            ExpressionAttributeNames={
                "#nm": "name"
            },
            ExpressionAttributeValues={
                ":name": stock.name,
                ":img": stock.company_img,
                ":shortcut": stock.company_shortcut,
                ":exchange": stock.exchange,
                ":sector": stock.sector,
                ":quote": quote,
                ":timeline": [quote],
                ":empty_list": []
            }
        )

if __name__ == "__main__":
    handler(None, None)