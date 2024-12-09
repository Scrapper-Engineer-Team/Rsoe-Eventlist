import aiohttp
import yt_dlp
import aiofiles
import os
import asyncio
import requests
from typing import Optional

class Downloaders:

    def download_file(links, filename, save_path, headers: Optional[dict]):
        asyncio.run(Downloaders.async_download_file(links, filename, save_path, headers))
        try:
            os.makedirs(save_path, exist_ok=True)

            if headers:
                response = requests.get(links, headers=headers)
            else:
                response = requests.get(links)

            response.raise_for_status()

            if response.status_code == 200:
                print(f"Konten berhasil diterima, panjang data: {len(response.content)} bytes.")
            else:
                print(f"Status code: {response.status_code}, konten tidak ditemukan.")

            # Menyimpan file
            full_path = os.path.join(save_path, filename)
            with open(full_path, 'wb') as file:
                file.write(response.content)

            print(f"File '{filename}' berhasil diunduh dan disimpan di '{save_path}'.")
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        except Exception as e:
            print(f"error occurred: {e}")


    async def async_download_file(links, filename, save_path, headers: Optional[dict]):
        try:
            os.makedirs(save_path, exist_ok=True)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(links, headers=headers) as response:
                    response.raise_for_status()

                    full_path = os.path.join(save_path, filename)

                    async with aiofiles.open(full_path, 'wb') as file:
                        await file.write(await response.read())

                    print(f"File '{filename}' berhasil diunduh dan disimpan di '{save_path}'.")
        except aiohttp.ClientError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")


    async def download_video(url, path, filename):
        try:
            def hook(d):
                if d['status'] == 'downloading':
                    print(f'Downloading: {d["filename"]} ({d["_percent_str"]})')
                elif d['status'] == 'finished':
                    print(f'Done downloading: {d["filename"]}')

            outmpl = f'{path}%(title)s.%(ext)s'
            if filename is not None:
                outmpl = f'{path}/{filename}.%(ext)s'

            ydl_opts = {
                'outtmpl': outmpl,
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'progress_hooks': [hook],
                # ! you need to download ffmpeg to use this function
                'ffmpeg_location': r'C:/ffmpeg/bin/ffmpeg.exe'
            }

            def run_download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    print(f'Mendownload video dari: {url}')
                    ydl.download([url])
                    print('Video berhasil didownload!')

            await asyncio.to_thread(run_download)

        except Exception as e:
            print(f'Error: {e}')