from .data_manipulation import *
from .annotations  import Annotations
from .functions import Funct
from .datetimes import Time
from .endecode import *
from .casting import Casting
from .parser import Parser
from .fileIO import File
from .stream import logger, Stream
from .directory import Dir
from .downloader import Down
from .urlParsered import UrlPars

from configparser import ConfigParser
from greenstalk import Client
from helpers.eBnsq import Producer


def init_beanstalk_worker(config: ConfigParser, tube: str):
    return Client(
        (config.get("beanstalk", "host"), config.getint("beanstalk", "port")),
        use=tube,
        watch=tube,
    )


def init_beanstalk_pusher(config: ConfigParser, tube: str):
    return Client(
        (config.get("beanstalk", "host"), config.getint("beanstalk", "port")),
        use=tube,
        watch=tube,
    )


def init_nsq_producer(config: ConfigParser):
    return Producer(nsqd_http_address=config.get("nsq", "nsqd_http_address"))


def job_metadata(job, *args):
    result = {}
    for a in args:
        if a in job:
            result[a] = job[a]
    return result
