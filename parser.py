#!./venv/bin/python3
import requests
from bs4 import BeautifulSoup as bs4
import write_to_file
import datetime
import db


url = 'https://web.archive.org/web/20130908231150/http://www.msk.arbitr.ru:80/about/ourJudges/chycha'
url_1 = 'https://web.archive.org/web/20130908231150/http://www.msk.arbitr.ru/about/ourJudges/ageeva'
url_2 = 'https://web.archive.org/web/20130908231150/http://www.msk.arbitr.ru/about/ourJudges/aleksandrova'

def get_date(url):
    date = url[28:36]
    dd = date[6:]
    mm = date[4:6]
    yyyy = date[:4]
    date = datetime.date(year = int(yyyy) ,month = int(mm), day = int(dd))
    return date


def find_list_judges(url):
    """get list judges: inser url, return list"""
    session = requests.Session()
    req = session.get(url)
    if req.status_code == 200:
        soup = bs4(req.content, 'html.parser')
        judge_cards = soup.find('li', attrs={"class": "b-menu-item js-menu-item b-menu-item--active js-menu-item--active b-menu-item--is_submenu last"})
        judge_cards = judge_cards.find("ul", attrs={"class": 'b-menu js-menu menu accordion'})
        write_to_file.write_to_file(judge_cards)
        return judge_cards
    else:
        return "Not found"
    return "list"

def find_judges_cards(url):
    count = 0
    """find all short_name and hrefs: insert url, return list[short_name, href]"""
    list_judges = []
    judges_lists = find_list_judges(url)
    judges = judges_lists.find_all('li')
    for card in judges:
        try:
            s = []
            name = card.a.get_text()
            link = card.a['href']
            s.append(name),s.append('https://web.archive.org'+ link)
            list_judges.append(s)
            s = []
        except AttributeError:
            count += 1
            print("AttributeError:", name , link)
    print('Судей найдено = ', len(list_judges))
    print('Судей пропущено = ', count)
    return list_judges

def get_judge_attrs(judge_url):
    """get judge attrs: insert judge_url, return full_name, data, judge_stuff"""
    session = requests.Session()
    request = session.get(judge_url)
    print(judge_url)
    if request.status_code == 200:
        print("ok")
        soup = bs4(request.content, 'html.parser')
        header = soup.head.get_text()
        print(header)
    else:
        print("Not found")
        

def main():
    # find_judge_attrs(url) # main
    get_judge_attrs(url_1) # test
    get_judge_attrs(url_2) # test


def find_judge_attrs(url):
    """make list_judges(move to judges cards): enter url, return list_judges[short_name, href, full_name, date, judge_stuff]"""
    list_judges = []
    list_judges = find_judges_cards(url)
    for judge in list_judges:
        get_judge_attrs(judge[1])
        break
        


if __name__ == '__main__':
    main()
    