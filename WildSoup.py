#!/usr/bin/env python

import os; import sys; import sqlite3;

""" import rquiered modules"""
try:
    import json
    import argparse
    import requests
    from BeautifulSoup import BeautifulSoup
except ImportError as ie:
    print(str(ie))
    print "To install a module: pip install moduleName"
    sys.exit(-1)




class WildSoup(object):
    def __init__(self, user, passwd, sub):
        self.user = user
        self.passwd = passwd
        self.sub = "http://www.reddit.com/r/" + sub
        self.client = None

    def login(self):
        """Log in to reddit and save cookie"""

        pass_dict = {'user' : self.user,
                     'passwd' : self.passwd,
                     'api_type' : 'json',}

        headers = {'user-agent' : 'WildSoup image downloader.',}

        client = requests.session()
        client.headers = headers

        try:
            r = client.post('http://www.reddit.com/api/login', data=pass_dict)
            j = json.loads(r.text)
        except ConnectionError:
            sys.exit("Max retries exceeded with url.")

        client.modhash = j['json']['data']['modhash']
        client.user = self.user

        self.client = client

    def getTitles(self, html, imgur=False):
        if imgur == True:
            soup = BeautifulSoup(html)
            sAll = soup.findAll('a', {'class' : 'zoom'})
        else:
            soup = BeautifulSoup(html)
            sAll = soup.findAll("a", {"class" : "title may-blank loggedin"})

        return sAll

    def dlImage(self, url, path):
        try:
            fname = url.split('/')

            if fname[-1].endswith('?1'):
                fname[-1] = fname[-1].strip('?1')

            with open('%s%s' % (path, fname[-1]), 'wb') as file:
                response = requests.get('%s' % url, stream=True)

                if not response.ok:
                    print "Could not download image."
                    return "failed!"
                for block in response.iter_content(1024):
                    if not block:
                        break

                    file.write(block)
        except KeyboardInterrupt, IOError:
            sys.exit("Could not download image or interupted by user.")



    def compareFiles(self, link, files):
        for file in files:
            if file in link:
                return True
        return False




class wildSQL(object):
    """class for storing deleted images"""
    def __init__(self):
        self.db = __connect()
        self.cursor = self.db.cursor()
    
    def __connect(self):
        try:
            with sqlite3.connect('wild.db') as db:
                return db
        except sqlite3.OperationalError:
            db.close()
            return None

    def __insertTable(table_name):
        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS %s (iamge_name TEXT, title TEXT)" % table_name)
            db.commit()
        except sqlite3.OperationalError:
            db.close()

    def storeImage(table_name, image_name, image_title):
        try:
            self.cursor.execute("""
                INSERT INTO %s (iamge_name, title)
                    VALUES (%s, %s)
                """, (table_name, image_name, image_title))
            db.commit()
        except sqlite3.OperationalError:
            db.close()

    def lookUpImage(table_name, image_name):
        try:
            image = self.cursor.execute("""
                SELECT image_name FROM %s WHERE %s.image_name = %s
                """, (table_name, table_name, image_name))
            if len(image):
                return image
            else:
                return None
        except sqlite3.OperationalError:
            db.close()




def cmdArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r, --subreddit', dest='r', required=True, help='Subreddit name')
    parser.add_argument('-u, --username', dest='u', required=True, help='Reddit username')
    parser.add_argument('-p, --password', dest='p', required=True, help='Reddit password')
    parser.add_argument('-s, --suppress', dest='supp', action='store_true', required=False,help='Suppress Output')
    parser.add_argument('--version', action='version', version='%(prog)s 0.3')

    return parser.parse_args()



if __name__ == "__main__":
    base = cmdArgs()

    if not base.r:
        sys.exit("-r attribute (sub name) needed.")

    if base.supp:
        null_out = open(os.devnull, 'w')
        sys.stdout = null_out
        sys.stderr = null_out

    wildsoup = WildSoup(base.u, base.p, base.r)
    wildsoup.login()

    page = wildsoup.client.get(wildsoup.sub)
    titles = wildsoup.getTitles(page.text)

    path = os.getcwd() + "/img/" + base.r + "/"
    if not os.path.exists(path):
        os.makedirs(path)

    files = os.listdir(path)

    links = [[item.get('href').encode('utf-8'), item.getText().encode('utf-8')] for item in titles]

    part = 0 # count
    ln = len(links) # length

    for link in links: # link[0] = image url, link[1] = image title
        part += 1
        if wildsoup.compareFiles(link[0], files):
            print("[{:2}/{:2}] File '{}' exists".format(part,ln,link[1]))
        else:
            if '.jpg' in link[0]:
                print("[{:2}/{:2}] Downloading image \"{}\" ... ".format(part,ln, link[1]))
                wildsoup.dlImage(link[0], path)
            elif "http://imgur.com/a/" in link[0]:
                albumHtml = requests.get(link[0])
                album = wildsoup.getTitles(albumHtml.text, True)
                albumImgs = [items.get('href') for items in album]

                print("[{:2}/{:2}] Downloading album \"{}\" ... ".format(part,ln, link[1]))

                aPart = 0
                aLn = len(albumImgs)

                for link in albumImgs:
                    aPart += 1
                    print("\t[{:2}/{:2}] Downloading album image ... ".format(aPart,aLn))
                    wildsoup.dlImage("http:%s" % link, path)
