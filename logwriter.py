#!./venv/bin/python3
import os
import time


def log(text, msg='INFO'):
    msg = "{:^10}".format(msg)
    t = time.ctime()
    s = time.clock()
    time.sleep(2)
    time_now = time.asctime()
    line = msg + ' ' + time_now[10:19] + ' ' + text
    write_file(line)
    print(line)
    print(t, s * 10)


def write_file(text):
    log_path = get_path()
    f = open(log_path, 'a')
    f.write(text + '\n')


def get_path():
    """get current path to this"""
    import os
    path = os.path.abspath(__file__)
    num = path.rfind('/')
    path = path[:num+1]
    return path + "log.log"


if __name__ == "__main__":
    msg = "— А у нас скоро откроется еще два объекта, надо поменять количество."
    msg1 = "— А давайте вот тут еще перефразируем."
    msg2 = "— Можно вот тут заголовок поменять?"
    log(msg)
    log(msg1, msg='CRITICAL')
    log(msg2, msg='WARNING')

