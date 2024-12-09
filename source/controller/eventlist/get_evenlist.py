from controller.eventlist import RsoeEventlistController
from helpers.playwright_manager import PlaywrightManager
from helpers.html_parser import HtmlParser

import asyncio
import requests

class RsoeEventlist(RsoeEventlistController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._url = "https://rsoe-edis.org/eventList"

    async def handler(self):
        await PlaywrightManager().one_page(self._url, self.get_event, self.headless)

    async def get_event(self, page):
        # ? click ordered by
        await page.get_by_label("Order by...").select_option("eventDate")
        await asyncio.sleep(3)

        html = await page.content()
        category = HtmlParser().bs4_parser(html, "div.right-side > div.list > div")
        for i, div_cat in enumerate(category):
            class_attr = div_cat.get('class', [])
            if 'adblock' not in class_attr:
                category_text = div_cat.select_one("div.category-section > h3").text.strip()

                sub_category = div_cat.select("div.category-section > div.sub-section")
                for j, sub_category in enumerate(sub_category):
                    sub_category_text = sub_category.select_one("div.category-section > div.sub-section >  h4").text.strip()

                    sublist = sub_category.select("div.sub-section > div:nth-child(3) > div")
                    for k, div_card in enumerate(sublist):

                        location = div_card.select_one("td.location").text.strip()
                        title = div_card.select_one("td > h5.title").text.strip()
                        detail_link = div_card.select_one("td.details > a").attrs['href']

                        result = await self.get_detail_events(detail_link)
                        result['location'] = location

                        cat_clean = category_text.replace(" ","_").replace(",", "_").replace("-", "_").replace("/", "_").replace("\\","_").replace("|","_").replace(".","_").replace("__", "_").replace(":","_").strip().lower()
                        subcat_clean = sub_category_text.replace(" ","_").replace(",", "_").replace("-", "_").replace("/", "_").replace("\\","_").replace("|","_").replace(".","_").replace("__", "_").replace(":","_").strip().lower()
                        filename = title.replace(" ","_").replace(",", "_").replace("-", "_").replace("/", "_").replace("\\","_").replace("|","_").replace(".","_").replace("__", "_").replace(":","_").strip().lower()

                        path_data_raw = f"data/{cat_clean}/{subcat_clean}/json/{filename}_{k}.json"

                        self.metadata(
                            data=result,
                            link=detail_link,
                            title=title,
                            tags="rsoe-edis.org, rsoe, event-list",
                            category=category_text,
                            sub_category=sub_category_text,
                            source="rsoe-edis.org",
                            path_data_raw=path_data_raw,
                            update="daily",
                            country="Global",
                            level="Internasional",
                            range_data=result['event_date_utc'].split("-")[0]
                        )

    
    async def get_detail_events(self, url_detail):
        res = requests.get(url_detail).text
        data = {
            "event_title" : (HtmlParser().bs4_parser(res, "div.long-section:nth-child(2) > h2:nth-child(1)"))[0].text.strip(),
            "source" : (HtmlParser().bs4_parser(res, ".source-link"))[0]['href'],
            "severity" : (HtmlParser().bs4_parser(res, "div.long-section:nth-child(3) > div:nth-child(2) > div:nth-child(2) > p:nth-child(2)"))[0].text.strip(),
            "event_date_utc" : (HtmlParser().bs4_parser(res, "div.long-section:nth-child(4) > div:nth-child(1) > p:nth-child(2)"))[0].text.strip(),
            "last_update" : (HtmlParser().bs4_parser(res, "div.long-section:nth-child(4) > div:nth-child(2) > p:nth-child(2)"))[0].text.strip(),
            "latitude" : (HtmlParser().bs4_parser(res, "#latitude"))[0].text.strip(),
            "longitude" : (HtmlParser().bs4_parser(res, "#longitude"))[0].text.strip(),
            "area_range" : (HtmlParser().bs4_parser(res, "div.long-section:nth-child(6) > div:nth-child(1) > p:nth-child(2)"))[0].text.strip(),
            "address_affected_area(s)" : (HtmlParser().bs4_parser(res, "div.long-section:nth-child(6) > div:nth-child(2) > div:nth-child(1) > p:nth-child(2)"))[0].text.strip(),
            "event_description" : (HtmlParser().bs4_parser(res, ".event-description > p:nth-child(1)"))[0].text.strip()
        }
        return data