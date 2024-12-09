from urllib.parse import urljoin

import requests


class Producer:
    def __init__(self, nsqd_http_address):
        self.__nsqd_http_address = nsqd_http_address
        self.__session = requests.session()

    def publish(self, message, topic, defer=0):
        request = requests.PreparedRequest()
        request.prepare_url(
            urljoin(self.__nsqd_http_address, "pub"),
            params=dict(topic=topic, defer=defer),
        )
        self.__session.post(request.url, message)

    def close(self):
        self.__session.close()
