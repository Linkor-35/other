#!./venv/bin/python3


def get_path():
    """get current path to this"""
    import os
    path = os.path.abspath(__file__)
    num = path.rfind('/')
    path = path[:num+1]
    return path


def write_to_file(content):
    f = open(get_path()+'content.html', 'w')
    f.write(str(content))
    f.close
    print(get_path()+ 'content.html' + ' WRITED!!!')

def wrire_judge_card(content):
    f = open(get_path()+'judge.html', 'w')
    f.write(str(content))
    f.close
    print('OK')

def write_to_txt(content):
    f = open(get_path()+'text.txt', 'w')
    f.write(str(content))
    f.close
    print('OK')


if __name__ == '__main__':
    pass