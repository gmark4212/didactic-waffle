#!/usr/bin/python

import sqlite3
from sqlite3 import Error
from modules.storage import DataStorage


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None


def select_(conn, table):

    print(f'================= {table} ================')
    cur = conn.cursor()
    cur.execute(f"SELECT {table} FROM  results")
    rows = cur.fetchall()
    s1 = []

    for row in rows:
        row = list(row)
        st = row[0]

        if st:
            s = st.split(';')
            for i in s:
                f = i.split('/')
                if f:
                    s1.extend(f)
                else:
                    s1.append(i)

    skills = list(set(s1))
    return skills


def main():
    db = DataStorage()
    database = "csv-data.db"
    conn = create_connection(database)
    result = []

    with conn:
        result.extend(select_(conn, 'LanguageWorkedWith'))
        result.extend(select_(conn, 'LanguageDesireNextYear'))
        result.extend(select_(conn, 'DatabaseWorkedWith'))
        result.extend(select_(conn, 'DatabaseDesireNextYear'))
        result.extend(select_(conn, 'PlatformWorkedWith'))
        result.extend(select_(conn, 'PlatformDesireNextYear'))
        result.extend(select_(conn, 'WebFrameWorkedWith'))
        result.extend(select_(conn, 'WebFrameDesireNextYear'))
        result.extend(select_(conn, 'MiscTechWorkedWith'))
        result.extend(select_(conn, 'MiscTechDesireNextYear'))
        result.extend(select_(conn, 'DevEnviron'))

        result = list(set(result))
        print(result)
        db.add_skill_to_ref(result)


if __name__ == '__main__':
    main()
