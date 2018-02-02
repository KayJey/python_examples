
import httplib2
import os
import re
import threading
import urllib
import urllib.request
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


class Singleton(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance

class ImageDownloaderThread(threading.Thread):
	def __init__(self, thread_id, name, counter):
		threading.Thread.__init__(self)
		self.name = name

	def run(self):
		print('Starting thread ' + self.name)
		download_images(self.name)
		print('Finished thread ' + self.name)

def traverse_site(max_links=10):
	link_parser_singleton = Singleton()

	while link_parser_singleton.queue_to_parse:
		#print('queue has elements left: ' + str(link_parser_singleton.queue_to_parse))
		if len(link_parser_singleton.to_visit) == max_links:
			#print('unexpected return')
			return

		url = link_parser_singleton.queue_to_parse.pop()
		original_url = url
		print('Popped ' + url)

		parsed_url = urlparse(url)

		if not parsed_url.netloc:
			url = root + url

		http = httplib2.Http()
		try:
			status, response = http.request(url)
		except Exception:
			continue

		if status.get('content-type').split(';',1)[0] != 'text/html':
			#print('not html')
			continue

		link_parser_singleton.to_visit.add(url)
		link_parser_singleton.parsed_queue.add(original_url)
		print('Added '+url+' to queue')

		bs = BeautifulSoup(response, "html.parser")

		for link in BeautifulSoup.findAll(bs, 'a'):
			link_url = link.get('href')

			if not link_url or link_url in link_parser_singleton.parsed_queue:
				continue

			parsed = urlparse(link_url)

			if parsed.netloc and parsed.netloc != parsed_root.netloc:
				#print('didnt pass netloc test' + link_url)
				continue
			#print('passed netloc test: '+link_url)

			if link_url in link_parser_singleton.to_visit:
				continue
			print('added '+link_url+' to parsing queue')
			link_parser_singleton.queue_to_parse.append(link_url)

def download_images(thread_name):
	singleton = Singleton()

	print('links to visit')
	print(str(singleton.to_visit))
	while singleton.to_visit:

		url = singleton.to_visit.pop()

		http = httplib2.Http()
		print(thread_name + 'Startin downloading images from '+url)

		try:
			status, response = http.request(url)
		except Exception as e:
			continue

		bs = BeautifulSoup(response, "html.parser")

		images = BeautifulSoup.findAll(bs, 'img')

		for image in images:
			src = image.get('src')

			src = urljoin(url, src)

			basename = os.path.basename(src)

			if src not in singleton.downloaded:
				singleton.downloaded.add(src)
				print('Downloading '+src)
				try:
					urllib.request.urlretrieve(src, os.path.join('images', basename))
				except Exception:
					continue

		print(thread_name + ' finished downloading images from ' + url)


if __name__ == '__main__':
	root = 'http://python.org'

	parsed_root = urlparse(root)

	singleton = Singleton()
	singleton.queue_to_parse = [root]
	singleton.parsed_queue = set()
	singleton.to_visit = set()
	singleton.downloaded = set()

	traverse_site()

	if not os.path.exists('images'):
		os.makedirs('images')

	thread1 = ImageDownloaderThread(1, 'Thread-1', 1)
	thread2 = ImageDownloaderThread(2, 'Thread-2', 2)

	thread1.start()
	thread2.start()
					