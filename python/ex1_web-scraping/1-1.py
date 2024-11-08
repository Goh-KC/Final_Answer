import requests
from bs4 import BeautifulSoup
import socket
import ssl
import pandas
import re
import regex
import time
from urllib.parse import urljoin
from openpyxl import Workbook

custom_user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                   ' Chrome/130.0.0.0 Safari/537.36'}
main_url = "https://r.gnavi.co.jp/area/jp/rs/?point=SAVE"

# SSL確認用の関数
def get_server_certificate(hostname):
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname):
                return True
    except:
        return False


time.sleep(3)
# このページから各店のURLを取得
shop_url = requests.get(main_url, headers=custom_user_agent)
shop_url.raise_for_status()
webpage1 = shop_url.text

soup1 = BeautifulSoup(webpage1, "html.parser")
shop_list = soup1.findAll(name="a", class_="style_titleLink__oiHVJ")

url_list = [shop.get("href") for shop in shop_list]
next_page = soup1.find(name="a", string="2").get("href")
time.sleep(3)
shop_url2 = requests.get(urljoin(main_url, next_page), headers=custom_user_agent)
shop_url2.raise_for_status()
next_webpage = shop_url2.text
soup_next_webpage = BeautifulSoup(shop_url2.text,"html.parser")
shop_list2 = soup_next_webpage.findAll(name="a", class_="style_titleLink__oiHVJ")

for shop in shop_list2:
    url = shop.get("href")
    if len(url_list) < 50:
        url_list.append(url)
    else:
        break


# 各項目のリストを作る
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

for item in url_list:
    # 各サイトの情報を取得
    time.sleep(3)
    shop_details = requests.get(item, headers=custom_user_agent)
    webpage2 = shop_details.content
    soup2 = BeautifulSoup(webpage2.decode("utf-8","ignore"), "html.parser")

    # 各店の名前
    name = soup2.find(name="a", href=item).getText()
    shop_name_list.append(name)

    # 各店の電話番号
    number = soup2.find(name="span", class_="number").getText()
    shop_number_list.append(number)

    # 各店の住所
    address = soup2.find(name="span", class_="region").getText()
    shop_address_list.append(address)

    # 各店の県
    prefecture = re.match('東京都|北海道|(?:京都|大阪)府|.{2,3}県', address).group()
    shop_prefecture_list.append(prefecture)

    # 各店の市
    new_address = address.replace(f"{prefecture}",'')
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
        building = soup2.find(name='span', class_='locality').getText()
        shop_building_list.append(building)
    except AttributeError:
        shop_building_list.append("")

    # 各店のホームページ
    try:
        homepage = soup2.find(name="a", class_="sv-of double").get("href")
    except AttributeError:
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

data = pandas.DataFrame(diction)
data.to_csv("1-1.csv")

# CSV ファイルをExcelで開く
# data_file = pandas.read_csv('1-1.csv')
# final = pandas.ExcelWriter("shop.xlsx")
# data_file.to_excel(final, index=False)

# final.close()







