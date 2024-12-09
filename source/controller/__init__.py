import random
import re
import time
import redis
import settings
import requests

from faker import Faker
from httpx import AsyncClient, Response
from loguru import logger
from stem.control import Controller
from stem import Signal
from abc import ABC
from configparser import ConfigParser
from helpers.input import Input
from helpers.output import Output
from helpers import Time, File
from server import S3, Kafkaa


class Controllers(ABC):

    job: dict = {}

    def __init__(self, *args, **kwargs):                
        self.log = logger
        self.faker = Faker()
        self.headless = kwargs.get('headless')
        self._base_path_s3 = settings.S3_CONFIGURATIONS["base_path_s3"]
        
    async def main(self):
        try:
            await self.handler()
        except Exception as e:
            self.log.error(e)

    async def handler(self):
        pass
    
    def metadata(self, data, **kwargs) -> None:
        path_data_raw = kwargs.get('path_data_raw')
        _temp = {
            "link": kwargs.get('link'),
            "tags": kwargs.get('tags') if isinstance(kwargs.get('tags'), list) else kwargs.get('tags').split(", ") if kwargs.get('tags') else None,
            "source": kwargs.get('source'),
            "title": kwargs.get('title'),
            "sub_title": kwargs.get('subtitle'),
            "range_data": kwargs.get('range_data'),
            "create_date": Time.now(),
            "update_date": Time.now(),
            "desc": kwargs.get('desc'),
            "category": kwargs.get('category'),
            "sub_category": kwargs.get('sub_category'),
            "crawling_time": Time.now(),
            "crawling_time_epoch": Time.epoch(),
            "country_name": kwargs.get('country'),
            "level": kwargs.get('level'),
            "stage": "Crawling data",
            "update_schedule": kwargs.get('update'),
            "data": data
        }
        
        if kwargs.get('save', False):
            File.write_json(path_data_raw, _temp)

        Kafkaa.send(_temp, "data-knowledge-repo-general_10", "research_ai")
        self.log.debug(_temp)

        # S3.upload_json(
        #     destination=_temp["path_data_raw"][0].replace(self._base_path_s3, ''),
        #     body=_temp,
        #     send=kwargs.get('s3', False)
        # )


    def APIretrys(self, url, headers:dict, cookies:dict, data:dict, link_referer:str, max_retries:int=5, delay:int=2) -> dict:
        headers.update({'Referer' : link_referer})
        retries = 0

        while retries < max_retries:
            try:
                res = requests.post(url=url, data=data, headers=headers, cookies=cookies)
                
                if res.status_code == 200:
                    try:
                        return res.json()  
                    except ValueError as e:
                        return res.text
                else:
                    retries += 1
                    time.sleep(delay) 
                    
            except requests.RequestException as e:
                self.log.error(f"API Retrys failed: {e}")
                retries += 1
                time.sleep(delay) 

        self.log.debug("Reached max retries")
        return None