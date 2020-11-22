import requests
from requests.exceptions import HTTPError
from geopy import distance


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
