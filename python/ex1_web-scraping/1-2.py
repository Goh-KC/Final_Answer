from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import re
import regex
import ssl
import socket


custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
                    " (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"

option = Options()
option.add_argument("--headless")
option.add_argument('--disable-extensions')
option.add_argument('--disable-popup-blocking')
option.add_argument(f'--user-agent={custom_user_agent}')
driver = webdriver.Chrome(options=option)


# 1ページ目の店のURL
driver.get('https://r.gnavi.co.jp/area/jp/rs/?point=SAVE')
first_page = driver.find_elements(By.CSS_SELECTOR, '.style_titleLink__oiHVJ')
shop_url_list = [items.get_attribute('href') for items in first_page]

# 2ページ目の店のURL
second_page_url = driver.find_element(By.LINK_TEXT, '2').get_attribute("href")
driver.get(second_page_url)
second_page = driver.find_elements(By.CSS_SELECTOR, '.style_titleLink__oiHVJ')
for items in second_page:
    if len(shop_url_list) < 50:
        shop_url_list.append(items.get_attribute('href'))


# SSL確認用の関数
def get_server_certificate(hostname):
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname):
                return True
    except:
        return False


shop_name_list = []
shop_number_list = []
shop_address_list = []
shop_homepage_list =[]
shop_prefecture_list = []
shop_city_list = []
shop_banchi_list = []
shop_building_list = []
shop_email_list = []
SSL_list = []

for item in shop_url_list:
    driver.get(item)
    # 各店の名前
    name = driver.find_element(By.ID, 'info-name').text
    shop_name_list.append(name)

    # 各店の電話番号
    number = driver.find_element(By.CSS_SELECTOR, '.number').text
    shop_number_list.append(number)

    # 各店の住所
    address = driver.find_element(By.CSS_SELECTOR, '.region').text
    shop_address_list.append(address)

    # 各店の県
    prefecture = re.match('東京都|北海道|(?:京都|大阪)府|.{2,3}県', address).group()
    shop_prefecture_list.append(prefecture)

    # 各店の市
    new_address = address.replace(f"{prefecture}", '')
    city_array = regex.findall(r'\p{Han}+|\p{Hiragana}+|\p{Katakana}+', new_address)
    city = ""
    for _ in city_array:
        city += _
    shop_city_list.append(city)

    # 各店の番地
    banchi = new_address.replace(f"{city}", '')
    shop_banchi_list.append(banchi)

    # 各店の建物名
    try:
        building = driver.find_element(By.CSS_SELECTOR, '.locality').text
    except NoSuchElementException:
        building = ""
    shop_building_list.append(building)

    # 各店のホームページ
    try:
        homepage = driver.find_element(By.CSS_SELECTOR, '.sv-of.double').get_attribute("href")
    except NoSuchElementException:
        homepage = ""
    shop_homepage_list.append(homepage)

    # メールアドレス
    shop_email_list.append("")

    # 各店のSSLの有無の確認
    stripped_address = re.findall('https://(.*)/', homepage)
    if stripped_address:
        cert = get_server_certificate(stripped_address[0])
    else:
        cert = get_server_certificate("")
    SSL_list.append(cert)

# ドライバーを閉じる
driver.quit()

# 辞書を作る
diction = {
        "店舗名": shop_name_list,
        "電話番号": shop_number_list,
        "メールアドレス": shop_email_list,
        "都道府県": shop_prefecture_list,
        "市区町村": shop_city_list,
        "番地": shop_banchi_list,
        "建物名": shop_building_list,
        "URL": shop_homepage_list,
        "SSL": SSL_list
}

# CSVファイルにする
data = pd.DataFrame(diction)
data.to_csv("1-2.csv")


