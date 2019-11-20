# coding: UTF-8
import requests
from bs4 import BeautifulSoup as bs
import re
import json
import time
import pandas as pd
from tqdm import tqdm

start_time = time.time()
print("start")

top_url = "https://www.u-coop.net/food/menu/hanshin/info.php"
menu_url = "https://www.u-coop.net/food/menu/hanshin/info.php?menu_code="

top_html = requests.get(top_url)
top_soup = bs(top_html.content, "lxml")

category_urls = [top_url + href.get("href") for href in top_soup.find_all("a") if
                 ((type(href.get("href")) == str) and (re.match(r"\?category=", href.get("href"))))]

columns = ['category', 'name', 'R', 'G', 'Y', 'Energy', 'Protein', 'Lipid', 'Carbohydrate', 'Calcium', 'Iron',
           'VitaminA', 'VitaminB1', 'VitaminB2 ', 'VitaminC', 'Salt', 'Vegetables']


# matchの第二引数はnoneが入るとおかしくなるので type(href.get("href"))==str でstrのみにする。


def get_menu(url):
    html = requests.get(url)
    time.sleep(0.2)
    soup = bs(html.content, "lxml")
    menu_codes = [re.findall(r"[0-9]+", href.get("href"))[0] for href in soup.find_all("a") if
                  ((type(href.get("href")) == str) and (re.search(r"menu_code=", href.get("href"))))]
    menu_codes.append(re.findall(r"[0-9]+", soup.find_all("p", text=re.compile(r"（[0-9]+）"))[0].string)[0])
    return menu_codes


def get_category(url):
    html = requests.get(url)
    time.sleep(0.5)
    soup = bs(html.content, "lxml")
    category_name = soup.find("div", class_="columns medium-12").find("h2").string
    return category_name


def get_data(url):
    html = requests.get(url)
    time.sleep(0.5)
    soup = bs(html.content, "lxml")
    menu_name = re.findall(r"<h3 .+>(.+)（.+）<.+/h3>", str(soup.find_all("h3", "main-tit")))[0]
    menu_data = [str(p.string) for p in soup.find_all("p") if re.match(r"【栄養バランス】", str(p.string))][0]

    facts = dict(zip(columns[2:],
                     [float(j[:1] + "." + j[1:]) if not (re.findall(r"^[1-9].*?|\.|^0$", j)) else float(j) for j in
                      re.findall(r"[ \u3000]+●?(?:\D+[0-9]??) ?([0-9]+\.?[0-9]*)(?:[mμ]?g|Kcal|点)", menu_data)]))

    return menu_name, facts


menu_code_dict = {}

for name, url in zip([get_category(url) for url in category_urls], category_urls):
    menu_code_dict[name] = get_menu(url)

print("get menu:OK!")

# menu_df = pd.DataFrame(columns=["category", "name", "R", "G", "Y", "cal"])
menu_df = pd.DataFrame(columns=columns)

for category, code_list in menu_code_dict.items():

    for code in tqdm(code_list, desc=category):
        name = get_data(menu_url + code)[0]
        facts = get_data(menu_url + code)[1]
        menu_df = menu_df.append(pd.Series({**{"category": category, "name": name}, **facts}), ignore_index=True)

with open('menu_data.json', 'w') as fw:
    json.dump(menu_df.to_dict(orient="index"), fw, indent=4, ensure_ascii=False)

elapsed_time = time.time() - start_time
print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
