#!/usr/bin/python3

from bs4 import BeautifulSoup as bs
import requests
import re

count = 1
file_name = None


def get_name_to_file(url):
    pattern = re.findall(r'\d{14}', url)
    return str(pattern[0])


def get_judge_attrs(url):
    """move to judge urls and take data"""
    session_judge = requests.Session()
    request = session_judge.get(url)
    if request.status_code == 200:
        soup = bs(request.content, 'html.parser')
        judge_card = soup.find("h2", attrs={"class": 'b-card-title b-card-fio'})
        judge_card2 = soup.find("dd", attrs={"class": 'b-card-info-descr'})
        judicial_staff = judge_card2.get_text()
        full_name = judge_card.get_text()

    else:
        print("Личная карта не найдена")

    return str(full_name) + "   " + str(judicial_staff)


def get_judge(url):
    session = requests.Session()
    request = session.get(url)
    global count

    """req to main landing for take urls and short names"""
    if request.status_code == 200:
        soup = bs(request.content, 'html.parser')
        accordion = soup.find("li", attrs={"class": 'b-menu-item js-menu-item b-menu-item--active js-menu-'
                                                    'item--active b-menu-item--is_submenu last'})
        judges = accordion.find("ul", attrs={"class": 'b-menu js-menu menu accordion'})
        judges = judges.find_all('a')
        for judge in judges:
            global count
            href = "https://web.archive.org" + str(judge.get("href"))
            short_name = judge.get_text()
            file = open(get_name_to_file(url), 'a')
            number = count
            count += 1
            text = str(number) + "   " + short_name + "   " + str(url) + "   " + get_judge_attrs(href) + "\n"
            file.write(text)

    else:
        print("Архив не найден! неверная ссылка")

    file.close()
    count = 1
    print("Make file  " + str(get_name_to_file(url) + "  " + "DONE"))

