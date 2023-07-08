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
            station
            for item in response.json().get("items", [])
            if (station := self.__station_from_api_item(item)) and station.streams
        ]

    def search_streams_by_station(self, query: str) -> list[Stream]:
        return [s for st in self.search_stations(query) for s in st.streams]

    def __station_from_api_item(self, item: dict) -> Station:
        attrs = item["attributes"]
        return Station(
            name=f"{attrs['brand']['name']} ({attrs['brand']['call']})",
            call=attrs["brand"]["call"],
            streams=[
                self.__stream_from_api_item(stream, attrs)
                for stream in attrs["streamsV2"]
            ],
        )

    def __stream_from_api_item(self, stream: dict, station: dict) -> Stream:
        return Stream(
            primary=stream["primary"],
            station=station["brand"]["name"],
            name=stream["title"],
            href=stream["urls"][0]["href"],
        )


nprapi = NPRAPI()
