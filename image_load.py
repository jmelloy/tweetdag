#!/usr/bin/env python
# encoding: utf-8
"""
image_load.py

Created by Jeffrey Melloy on 2009-05-02.
"""

import sys
import os.path
import psycopg2
from urllib import urlretrieve

def main():
    conn = psycopg2.connect("dbname='jmelloy'")
    cursor = conn.cursor()
    upd_cursor = conn.cursor()

    sql = "select screen_name, image_url, image_filename, id from twitter_ids"
    upd = "update twitter_ids set image_filename = %(file)s where id = %(id)s"

    cursor.execute(sql)

    rs = cursor.fetchone()

    while(rs):
        username = rs[0]
        url = rs[1]
        suffix = url.split('.')[-1]
        filename = "images/%s.%s" % (username, suffix)
        if not os.path.exists(rs[2]):
            print username, url
            urlretrieve(url, filename)
            vars = {"id":rs[3], "file":filename}

            upd_cursor.execute(upd, vars)
        rs = cursor.fetchone()

    conn.commit()
if __name__ == '__main__':
    main()

