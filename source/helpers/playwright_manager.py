import asyncio
import json

from playwright.async_api import async_playwright
from fake_useragent import UserAgent
from loguru import logger
from typing import Optional


ua = UserAgent()

class PlaywrightManager:
    def __init__( self, url_request:Optional['str']=None ):
        self.full_args = [
            '--disable-gpu',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-infobars',
            '--disable-features=site-per-process',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--disable-web-security-warning',
            '--allow-file-access-from-files',
            '--allow-file-access',
            '--allow-popups',
            '--disable-setuid-sandbox',
            '--disable-dev-tools',
            '--disable-dev-tools-auto-open-devtools-for-tabs',
            '--disable-default-apps',
            '--disable-features=NetworkService',
            '--disable-features=NetworkServiceInProcess',
            '--disable'
            ]
        self.args =[
            '--disable-gpu', 
            '--no-sandbox', 
            '--disable-dev-shm-usage', 
            '--disable-extensions', 
            '--disable-background-timer-throttling', 
            '--disable-backgrounding-occluded-windows', 
            '--disable-infobars', 
            '--window-size=1920,1080'
            ]
        self.request_url = url_request


    async def one_page( self, url: str, script_function: callable, headless ):
        """ Run Playwright and execute a process from script_function on a single page """
        logger.debug("Starting Playwright for one page")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=headless, 
                args=self.full_args
            )
            context = await browser.new_context( user_agent=ua.random )
            # await context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media"] else route.continue_())
            page = await context.new_page()

            try:
                await self.run_script_on_page( page, url, script_function, None)
            except Exception as e:
                print( e )
            finally:
                await page.close()
                await context.close()
                await browser.close()


    async def multiple_pages( self, url: str, script_function: callable, list_tasks: list, headless, max_tabs:int=2 ):
        """ Run Playwright with multiple pages and execute a process from script_function for each task """
        logger.debug("Starting Playwright for multiple pages")
        
        async with async_playwright() as p:
            browser = await p.firefox.launch( headless=headless, args=self.args )
            context = await browser.new_context()
            
            semaphore = asyncio.Semaphore( max_tabs )

            async def run_task_with_semaphore( task ):
                async with semaphore:
                    # await context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media"] else route.continue_())
                    page = await context.new_page()
                    
                    try:
                        await self.run_script_on_page( page, url, script_function, task )
                    except Exception as e:
                        print( e )
                    finally:
                        await page.close()

            tasks = [asyncio.create_task(run_task_with_semaphore( list_tasks[i] )) for i in range(len( list_tasks ))]
            await asyncio.gather( *tasks )


    async def run_script_on_page( self, page, url, script_function, task=None ):
        """ Run the provided script on a page """

        data_container = {}

        async def request_handle( response ):
            if self.request_url in response.url:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        if not( data.get("unread_message") == 0 ):
                            data_container["data"] = data["data"]

        try:
            if self.request_url is not None:
                page.on("response", request_handle)

            response = await page.goto( url, wait_until="domcontentloaded", timeout=300000 )
            if response.status != 200:
                print( f"Failed to load page { url }. Status: { response.status }" )
            else:
                if self.request_url is not None:
                    await script_function( page, data_container )
                else:
                    await script_function( page )

        except TimeoutError:
            print( f"Timeout error when accessing { url }" )
        except Exception as e:
            print( f"Error processing page { url }: { e }" )
            raise e


    @staticmethod
    async def context_cookies( context ):
        """ Static method to handle or retrieve context cookies """
        try:
            with open( './cookies.json', 'r' ) as f:
                cookies = json.load( f )
                await context.add_cookies( cookies["cookies"] )
        except Exception as e:
            print(f"Error loading cookies: { e }")




    @staticmethod
    async def get_curl_response( page, url_request, headers, data ):
        """ Static method to retrieve curl response data """
        try:
            response = await page.request.post(
                url_request,
                headers=headers,
                data=data,
            )
            result = await response.json()
            return result
        except Exception as e:
            print(f"Error fetching data from  { url_request }: { e }")
            return None