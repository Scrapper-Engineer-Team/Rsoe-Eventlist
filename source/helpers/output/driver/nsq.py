import atexit

from helpers.eBnsq import Producer
from helpers.output.driver import OutputDriver


class NsqOutputDriver(OutputDriver):
    name = "nsq"

    def __init__(
        self,
        topic: str,
        nsqd_http_address: str = "http://localhost:4151",
        *args,
        **kwargs
    ):
        super(NsqOutputDriver, self).__init__(*args, **kwargs)
        self.topic = topic
        self.nsq = Producer(nsqd_http_address=nsqd_http_address)
        atexit.register(self.close)

    def put(self, output: str, **kwargs):
        self.nsq.publish(output, self.topic)

    def close(self):
        self.nsq.close()
