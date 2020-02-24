#!./venv/bin/python3
import sqlite3
from sqlite3 import Error


def get_path():
    """get current path to this"""
    import os
    path = os.path.abspath(__file__)
    num = path.rfind('/')
    path = path[:num+1]
    return path


def create_connection(db_file):
    """creat connection to db"""
    if db_file:
        conn = None
        try:
            conn = sqlite3.connect(get_path() + db_file)
            print("connection to ", db_file, " SUSSES")
        except Error as e:
            print(e)
        return conn
    else:
        pass


def make_table():
    pass



def write_judge():

    pass


if __name__ == "__main__":
    pass
    # create_connection('judges_db.db')