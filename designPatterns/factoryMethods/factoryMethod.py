import abc
import urllib
import urllib.request
import urllib.error
from bs4 import BeautifulSoup

class Connector(object):
	__metaclass__ = abc.ABCMeta

	def __init__(self, is_secure):
		self.is_secure = is_secure
		self.port = self.port_factory_method()
		self.protocol = self.protocol_factory_method()

	@abc.abstractmethod
	def parse(self):
		pass

	def read(self, host, path):
		url = self.protocol + '://' + host + ':' + str(self.port) + path
		print('Connecting to ' + url)
		return urllib.request.urlopen(url, timeout=2).read()

	@abc.abstractmethod
	def protocol_factory_method(self):
		pass

	@abc.abstractmethod
	def port_factory_method(self):
		pass

class HTTPConnector(Connector):

	def protocol_factory_method(self):
		if self.is_secure:
			return 'https'
		return 'http'

	def port_factory_method(self):
		if self.is_secure:
			return HTTPSecurePort()
		return HTTPPort()

	def parse(self, content):
		filenames = []
		soup = BeautifulSoup(content, "html.parser")
		links = BeautifulSoup.findAll(soup, 'a')
		for link in links:
			filenames.append(link['href'])
		return '\n'.join(filenames)

class FTPConnector(Connector):

	def protocol_factory_method(self):
		return 'ftp'

	def port_factory_method(self):
		return FTPPort()

	def parse(self, content):
		lines = content.split('\n')
		filenames = []
		for line in lines:
			splitted_line = line.split(None, 8)
			if len(splitted_line) == 9:
				filenames.append(splitted_line[-1])

		return '\n'.join(filenames)

class Port(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def __str__(self):
		pass

class HTTPSecurePort(Port):

	def __str__(self):
		return '443'

class HTTPPort(Port):

	def __str__(self):
		return '80'

class FTPPort(Port):

	def __str__(self):
		return '21'

if __name__ == '__main__':
	domain = 'freebsd.org'
	path = '/de/where.html'

	protocol = input('Connecting to {}. Which protocol to use? (0-http, 1-ftp)'.format(domain))

	if protocol == '0':
		is_secure = bool(input('Use secure connection? (1-yes, 0-no)'))
		connector = HTTPConnector(is_secure)
	elif protocol == '1':
		is_secure = False
		connector == FTPConnector(is_secure)
	else:
		raise Exception('Invalid protocol')

	try:
		content = connector.read(domain, path)
	except urllib.error.URLError as e:
		print('Cannot access resource with this method')
	else:
		print(connector.parse(content))
