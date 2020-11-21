import requests
from requests.exceptions import HTTPError
from geopy import distance
from environs import Env

env = Env()
env.read_env()


def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_distance(apikey, origin, destination):
    try:
        origin_coords = fetch_coordinates(apikey, origin)
        destination_coords = fetch_coordinates(apikey, destination)
    except (IndexError, HTTPError):
        return

    return distance.distance(origin_coords, destination_coords).km



if __name__ == '__main__':
    # from django.conf import settings
    #
    # settings.configure()

    from environs import Env

    # env = Env()
    # env.read_env()
    #
    GEOCODER_APIKEY = env.str('GEOCODER_APIKEY')
    # coords = fetch_coordinates(apikey=GEOCODER_APIKEY, place='Пулково')

    # print(coords)

    # wellington = (-41.32, 174.81)
    # salamanca = (40.96, -5.50)
    #
    # print(distance.distance(wellington, salamanca).km)

    # address_1 = 'wertwret'
    address_1 = 'Москва, пл. Киевского Вокзала, 2'
    address_2 = 'Москва, ул. Новый Арбат, 15'

    print(fetch_coordinates(GEOCODER_APIKEY, address_1))
    print(fetch_coordinates(GEOCODER_APIKEY, address_2))
    # print(get_distance(GEOCODER_APIKEY, address_1, address_2))
