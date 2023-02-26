import requests

from npr.domain import Station, Stream

NPR_QUERY_URL = "https://www.npr.org/proxy/stationfinder/v3/stations"


class NPRAPI:
    def __init__(self, npr_query_url: str = NPR_QUERY_URL):
        self.uri = npr_query_url

    def search_stations(self, query: str) -> list[Station]:
        response = requests.get(
            self.uri,
            params={
                "q": query,
            },
        )

        return [
            self.station_from_api_item(item)
            for item in response.json().get("items", [])
        ]

    def station_from_api_item(self, item: dict) -> Station:
        attrs = item["attributes"]
        return Station(
            name=attrs["brand"]["name"],
            call=attrs["brand"]["call"],
            streams=[
                self.stream_from_api_item(stream, attrs)
                for stream in attrs["streamsV2"]
            ],
        )

    def stream_from_api_item(self, stream: dict, station: dict) -> Stream:
        return Stream(
            primary=stream["primary"],
            station=station["brand"]["name"],
            title=stream["title"],
            href=stream["urls"][0]["href"],
        )
