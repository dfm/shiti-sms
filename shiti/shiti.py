#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

__all__ = []

import requests
from math import radians, sin, cos, asin, sqrt


def get_stations(latitude, longitude, min_bikes=1, min_docks=1):
    # Fetch the realtime list of all the stations.
    r = requests.get("http://citibikenyc.com/stations/json")
    if r.status_code != requests.codes.ok:
        r.raise_for_status()
    stations = r.json().get("stationBeanList", [])

    # Sort the stations.
    good_stations = []
    latitude, longitude = radians(latitude), radians(longitude)
    for station in stations:
        # Skip if the station is out of service.
        if station["statusValue"] != "In Service":
            continue

        # Skip if the number of bikes/docks criteria is not met.
        if station["availableBikes"] < min_bikes:
            continue
        if station["availableDocks"] < min_docks:
            continue

        lat, lng = radians(station["latitude"]), radians(station["longitude"])
        dlat, dlng = latitude - lat, longitude - lng
        dist = 2*asin(sqrt(sin(0.5*dlat)**2
                           + cos(lat)*cos(latitude)*sin(0.5*dlng)**2))
        dist *= 3963.1676  # Miles.
        good_stations.append({
            "distance": dist,
            "name": station["stationName"],
            "bikes": station["availableBikes"],
            "docks": station["availableDocks"],
        })

    return sorted(good_stations, key=lambda s: s["distance"])


def parse_location(loc):
    params = {"address": loc + " New York, NY", "sensor": "false"}
    r = requests.get("http://maps.googleapis.com/maps/api/geocode/json",
                     params=params)
    if r.status_code != requests.codes.ok:
        r.raise_for_status()

    result = r.json()
    try:
        coords = result["results"][0]["geometry"]["location"]
    except (IndexError, KeyError):
        return None

    return coords


if __name__ == "__main__":
    coords = parse_location("736 dean st.")
    stations = get_stations(coords["lat"], coords["lng"], min_bikes=10)
    print(stations[:3])
