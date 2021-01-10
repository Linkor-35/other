#!/usr/bin/python3
import re
import judge

list_urls = []


def get_list_urls():

    global list_urls
    urls = open("urls.txt", "r")
    for href in urls:
        pattern = re.sub(r'[;,\n]', ' ', href)
        list_urls.append(pattern)


get_list_urls()
for url in list_urls:
    judge.get_judge(url)

