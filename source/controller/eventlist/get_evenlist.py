from controller.eventlist import RsoeEventlistController
from helpers.playwright_manager import PlaywrightManager
from helpers.html_parser import HtmlParser

import asyncio
import requests
import traceback

class RsoeEventlist(RsoeEventlistController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._url = "https://rsoe-edis.org/eventList"

    async def handler(self):
        await PlaywrightManager().one_page(self._url, self.get_event, self.headless)

    async def get_event(self, page):
        # ? click ordered by
        try:
            await page.get_by_label("Order by...").select_option("eventDate")
            await asyncio.sleep(10)

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

                            location = div_card.select_one("td.location").text.strip() if div_card.select_one("td.location") else None
                            title = div_card.select_one("td > h5.title").text.strip() if div_card.select_one("td > h5.title") else None
                            detail_link = div_card.select_one("td.details > a").attrs['href'] if div_card.select_one("td.details > a") else None

                            result = await self.get_detail_events(detail_link)
                            result['location'] = location

                            cat_clean = category_text.replace(" ","_").replace(",", "_").replace("-", "_").replace("/", "_").replace("\\","_").replace("|","_").replace(".","_").replace("__", "_").replace(":","_").strip().lower()
                            subcat_clean = sub_category_text.replace(" ","_").replace(",", "_").replace("-", "_").replace("/", "_").replace("\\","_").replace("|","_").replace(".","_").replace("__", "_").replace(":","_").strip().lower()
                            filename = title.replace(" ","_").replace(",", "_").replace("-", "_").replace("/", "_").replace("\\","_").replace("|","_").replace(".","_").replace("__", "_").replace(":","_").strip().lower()

                            path_data_raw = f"data/{cat_clean}/{subcat_clean}/json/{filename}_{k}.json"

                            if result['event_date_utc']:
                                range_data = result['event_date_utc'].split("-")[0]
                            else:range_data=None

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
                                range_data=range_data
                                )
        except Exception as e:
            error = traceback.print_exc()
            self.log.error(error)
    
    async def get_detail_events(self, url_detail):
        try:
            res = requests.get(url_detail).text
            
            # Menetapkan nilai ke variabel terlebih dahulu
            event_title = HtmlParser().bs4_parser(res, "div.long-section:nth-child(2) > h2:nth-child(1)")
            source = HtmlParser().bs4_parser(res, ".source-link")
            severity = HtmlParser().bs4_parser(res, "div.long-section:nth-child(3) > div:nth-child(2) > div:nth-child(2) > p:nth-child(2)")
            event_date_utc = HtmlParser().bs4_parser(res, "div.long-section:nth-child(4) > div:nth-child(1) > p:nth-child(2)")
            last_update = HtmlParser().bs4_parser(res, "div.long-section:nth-child(4) > div:nth-child(2) > p:nth-child(2)")
            latitude = HtmlParser().bs4_parser(res, "#latitude")
            longitude = HtmlParser().bs4_parser(res, "#longitude")
            area_range = HtmlParser().bs4_parser(res, "div.long-section:nth-child(6) > div:nth-child(1) > p:nth-child(2)")
            address_affected_areas = HtmlParser().bs4_parser(res, "div.long-section:nth-child(6) > div:nth-child(2) > div:nth-child(1) > p:nth-child(2)")
            event_description = HtmlParser().bs4_parser(res, ".event-description > p:nth-child(1)")
            
            # Membuat dictionary dengan nilai yang sudah ditetapkan
            data = {
                "event_title": event_title[0].text.strip() if event_title else None,
                "source": source[0].text.strip() if source else None,
                "severity": severity[0].text.strip() if severity else None,
                "event_date_utc": event_date_utc[0].text.strip() if event_date_utc else None,
                "last_update": last_update[0].text.strip() if last_update else None,
                "latitude": latitude[0].text.strip() if latitude else None,
                "longitude": longitude[0].text.strip() if longitude else None,
                "area_range": area_range[0].text.strip() if area_range else None,
                "address_affected_areas": address_affected_areas[0].text.strip() if address_affected_areas else None,
                "event_description": event_description[0].text.strip() if event_description else None
            }

            print(data)
            return data
        except Exception as e:
            self.log.error(e)
