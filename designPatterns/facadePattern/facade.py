from cache import Cache
from converter import Converter
from parser import Parser
from weather import Weather
from weatherprovider import WeatherProvider

class Facade(object):
	def get_forecast(self, city, country):
		cache = Cache('myfile')

		cache_result = cache.load()
		if cache_result:
			return cache_result
		else:
			weather_provider = WeatherProvider()
			weather_data = weather_provider.get_weather_data(city, country)

			data_parser = Parser()
			parsed_data = data_parser.parse_weather_data(weather_data)

			weather = Weather(parsed_data)
			converter = Converter()
			temp_celcius = converter.from_kelvin_to_celcius(weather.temperature)

			cache.save(temp_celcius)
			return temp_celcius

if __name__ == '__main__':
	facade = Facade()
	print(facade.get_forecast('Aarau', 'ch'))