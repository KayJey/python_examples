import abc
import urllib
import urllib.request
import urllib.error
from bs4 import BeautifulSoup

class Connector(object):
	__metaclass__ = abc.ABCMeta
	
	def __init__(self, factory):
		self.protocol = factory.create_protocol()
		self.port = factory.create_port()
		self.parse = factory.create_parser()

	def read(self, host, path):
		url = self.protocol + '://' + host + ':' + str(self.port) + path
		print('Connecting to ' + url)
		return urllib.request.urlopen(url, timeout=2).read()

class AbstractFactory(object):
	__metaclass__ = abc.ABCMeta

	def __init__(self, is_secure):
		self.is_secure = is_secure

	@abc.abstractmethod
	def create_port(self):
		pass

	@abc.abstractmethod
	def create_protocol(self):
		pass

	@abc.abstractmethod
	def create_parser(self):
		pass

class HTTPFactory(AbstractFactory):

	def create_port(self):
		if self.is_secure:
			return HTTPSPort()
		return HTTPPort()

	def create_protocol(self):
		if self.is_secure:
			return 'https'
		return 'http'

	def create_parser(self):
		return HTTPParser()

class FTPFactory(AbstractFactory):

	def create_port(self):
		return FTPPort()

	def create_protocol(self):
		return 'ftp'

	def create_parser(self):
		return FTPParser()

class Port(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def __str__(self):
		pass

class FTPPort(Port):

	def __str__(self):
		return '21'

class HTTPPort(Port):

	def __str__(self):
		return '80'

class HTTPSPort(Port):

	def __str__(self):
		return '443'

class Parser(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def __call__(self):
		pass

class HTTPParser(Parser):

	def __call__(self, content):
		filenames = []
		soup = BeautifulSoup(content)
		links = soup.table.findAll('a')
		for link in links:
			filenames.append(link.text)

		return '\n'.join(filenames)

class FTPParser(Parser):

	def __call__(self, content):
		lines = content.split('\n')
		filenames = []
		for line in lines:
			splitted_line = line.split(None,8)
			if len(splitted_line) == 9:
				filenames.append(splitted_line[-1])

		return '\n'.join(filenames)


if __name__ == '__main__':
	domain = 'freebsd.org'
	path = '/de/where.html'

	protocol = input('Connecting to {}. Which protocol to use? (0-http, 1-ftp)'.format(domain))

	if protocol == '0':
		is_secure = bool(input('use secure connection? (1-yes, 0-no)'))
		factory = HTTPFactory(is_secure)
	elif protocol == '1':
		is_secure = False
		factory = FTPFactory(is_secure)
	else:
		raise Exception('Invalid protocol')

	try:
		connector = Connector(factory)
		content = connector.read(domain, path)
	except urllib.error.URLError as e:
		print('Couldnt read resource like this')
	else:
		print(connector.parse(content))
