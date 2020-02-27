#!./venv/bin/python3
# encoding=utf8  

import os
import re
import csv
import write_to_file
list_groups = []
list_words = []

NEWLINE_RE = re.compile(r'\x00')
SEVERAL_SPACES = re.compile(r'\s{2,}')


def find_matches(text):
    # print(text)
    result = re.findall(r'\w+', text)
    # print(result)
    if result:
        return text
    else:
        return None


def add_splits_to_list(text):
    global list_groups
    text_1 = re.findall(r'^\w+ ', text)
    text_1 = re.sub(NEWLINE_RE, '',str(text_1))
    s = []
    if text:
        try:
            s.append(text_1[0]),s.append(text)
            # list_groups[text_1[0]] = str(text)
        except:
            print('error')
    else:
        text_1 = re.findall(r'^\w+\$\w+', text)
        s.append(text_1),s.append(text)
        # list_groups[text_1[0]] = str(text)

    list_groups.append(s)

def split_string(text):
    result = re.findall(r'ENTRY:RU@@(\w\$\w+)|ENTRY:RU@@(\w+)', text)
    return result


def get_path():
    """get current path to this"""
    import os
    path = os.path.abspath(__file__)
    num = path.rfind('/')
    path = path[:num+1]
    return path


def write_file(list):
    """write csv"""
    with open('courts.csv', 'w', newline='') as csvfile:
        for x in list:
            if len(x[2]) < 5 and len(x[3]) > 0:
                writer1 = csv.writer(csvfile)
                text = re.sub(NEWLINE_RE, '',str(x[2]))
                writer1.writerow([text]+[x[3]])

    return "OK"


def read_file():
    global list_words
    data = open(get_path() + '1.txt',encoding="utf-8", errors="backslashreplace").read()
    result = re.split(r'ENTRY:RU@@', data)
    print(len(result), 'grups in file')
    for i in result:
        add_splits_to_list(i)



if __name__ == '__main__':
    read_file()
    write_to_file.write_to_txt(list_groups, "words")
    print(list_groups[5])
    print(len(list_groups), 'groups in list')


