import requests
from pprint import pprint

url = "https://hotels4.p.rapidapi.com/properties/v2/get-offers"

payload = {
    "currency": "USD",
    "eapid": 1,
    "locale": "en_US",
    "siteId": 300000001,
    "propertyId": "9209612",
    "checkInDate": {
        "day": 6,
        "month": 10,
        "year": 2022
    },
    "checkOutDate": {
        "day": 9,
        "month": 10,
        "year": 2022
    },
    "destination": {
        "coordinates": {
            "latitude": 12.24959,
            "longitude": 109.190704
        },
        "regionId": "6054439"
    },
    "rooms": [
        {
            "adults": 2,
            "children": [{"age": 5}, {"age": 7}]
        },
        {
            "adults": 2,
            "children": []
        }
    ]
}
headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": "3b106b61f3msh7fcb63f72e7547dp185eebjsn9b4eb1f7b934",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

response = requests.request("POST", url, json=payload, headers=headers)

pprint(response.json())


def bestdeal():
    pass
