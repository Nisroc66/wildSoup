import json; import argparse; import requests; import os;
from BeautifulSoup import BeautifulSoup

def cmdArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument('-a', help='Enter URL to Reddit Subreddit')
	parser.add_argument('-u', help='Enter Reddit username')
	parser.add_argument('-p', help='Enter Reddit password')
	parser.add_argument('--version', action='version', version='%(prog)s 0.1')

	return parser.parse_args()


def login(usrname, passwd):
	"""Log in to reddit and save cookie"""

	pass_dict = {'user' : usrname,
				 'passwd' : passwd,
				 'api_type' : 'json',}
	headers = {'user-agent' : 'Nisroc\'s Reddit Bot',}

	client = requests.session()
	client.headers = headers

	r = client.post('http://www.reddit.com/api/login', data=pass_dict)
	j = json.loads(r.text)

	client.modhash = j['json']['data']['modhash']
	client.user = usrname

	return client


def getTitles(html, imgur=False):
	if imgur == False:
		soup = BeautifulSoup(html)
		sAll = soup.findAll("a", {"class" : "title may-blank loggedin"})
	else:
		soup = BeautifulSoup(html)
		sAll = soup.findAll('a', {'class' : 'zoom'})

	return sAll


def dlImage(url):
	path = "%s/img/" % os.getcwd()
	fname = url.split('/')
	with open('%s%s' % (path, fname[-1]), 'wb') as file:
		response = requests.get('%s' % url, stream=True)

		if not response.ok:
			print "Could not download image."
			return "failed!"
		for block in response.iter_content(1024):
			if not block:
				break

			file.write(block)

def getFilesList():
	fullPath = "%s/img/" % os.getcwd()
	files = os.listdir(fullPath)

	return files

def compareFiles(link, files):
	for file in files:
		if file in link:
			return False
	return True

if __name__ == "__main__":
	base = cmdArgs()
	url = "http://%s" % base.a
	print url

	client = login(base.u, base.p)
	page = client.get(url)
	titles = getTitles(page.text)
	files = getFilesList()

	links = [[item.get('href').encode('utf-8'), item.getText().encode('utf-8')] for item in titles]

	for link in links:
		if compareFiles(link[0], files) == False:
			print "File excists"
			continue
		else:
			if ".jpg" in link[0]:
				print "Downloading image \"%s\" ... " % link[1]
				dlImage(link[0])
			elif "http://imgur.com/a/" in link[0]:
				albumHtml = requests.get(link[0])
				album = getTitles(albumHtml.text, True)
				albumImgs = [items.get('href') for items in album]
				print "Downloading album \"%s\" ..." % link[1]
				for link in albumImgs:
					dlImage("http:%s" % link)
