import os
import requests
import mimetypes
import tempfile
import shutil
import asyncio
import aiofiles
import re
import yt_dlp

from uuid import uuid4
from dekimashita import Dekimashita
from icecream import ic
from requests import Response
from loguru import logger
from pytube import YouTube
from urllib.parse import urlparse, parse_qs

from server import S3
from .directory import Dir
from .fileIO import File
from playwright.sync_api import Page, ElementHandle

class Down:

    @staticmethod
    def curl(url: str, path: str, headers: dict = None, cookies: dict = None, extension: str = None) -> Response:
        Dir.create_dir(paths='/'.join(path.split('/')[:-1]))
        response = requests.get(url=url, headers=headers, cookies=cookies, verify=False, timeout=900)
        with open(path, 'wb') as f:
            f.write(response.content)

        return response
    
    @staticmethod
    def curlv2(path: str, response: Response, extension: str = None) -> Response:
        Dir.create_dir(paths='/'.join(path.split('/')[:-1]))
        with open(path, 'wb') as f:
            f.write(response.content)
            
    @staticmethod
    def playwright(page: Page, loc: ElementHandle, base_desctination: str, s3: bool, save: bool) -> str:
        with page.expect_download() as download_info:
            loc.click()
            download = download_info.value
        
        temp_dir: str = tempfile.mkdtemp().replace('\\', '/')
        filename: str = download.suggested_filename
        temp_path = temp_dir+'/'+filename
        
        logger.info(f'DOWNLOAD FILE [ {filename} ]')
        download.save_as(temp_path)
        
        extention: str = filename.split('.')[-1]
        destination_path: str = base_desctination + extention + '/' + filename
        S3.upload(
            body=File.read_byte(temp_path),
            destination=destination_path,
            send=s3
        )
        if save:
            File.write_byte(
                path=destination_path,
                media=File.read_byte(temp_path),
            )
        shutil.rmtree(temp_dir)
        return destination_path

    @staticmethod
    async def asyncPlaywright(page: Page, loc: ElementHandle, base_desctination: str, s3: bool, save: bool) -> str:
        async with page.expect_download() as download_info:
            await loc.click()
        download = await download_info.value
        temp_dir = tempfile.mkdtemp().replace('\\', '/')
        filename = download.suggested_filename
        
        temp_path = os.path.join(temp_dir, filename)
        logger.info(f'DOWNLOAD FILE [ {filename} ]')
        
        await download.save_as(temp_path)
        
        extention: str = filename.split('.')[-1]
        destination_path: str = base_desctination + extention + '/' + filename
        S3.upload(
            body=File.read_byte(temp_path),
            destination=File.vdir(destination_path),
            send=s3
        )
        if save:
            File.write_byte(
                path=File.vdir(destination_path),
                media=File.read_byte(temp_path),
            )
        shutil.rmtree(temp_dir)
        return File.vdir(destination_path)
    
    @staticmethod
    def syncPlaywright(page: Page, loc: ElementHandle, base_desctination: str, s3: bool, save: bool) -> str:
        with page.expect_download() as download_info:
            loc.click()
        download = download_info.value
        temp_dir = tempfile.mkdtemp().replace('\\', '/')
        filename = download.suggested_filename
        
        temp_path = os.path.join(temp_dir, filename)
        
        download.save_as(temp_path)
        
        extention: str = filename.split('.')[-1]
        name: str = filename.split('.')[0]
        destination_path: str = base_desctination + extention + '/' + Dekimashita.vdir(name.replace('-', '_')) + '.' + extention
        if os.path.exists(destination_path):
            destination_path: str = base_desctination + extention + '/' + Dekimashita.vdir(name.replace('-', '_')) + str(uuid4()).replace('-', '_') + '.' + extention
            
        logger.info(f'DOWNLOAD FILE [ {destination_path.split("/")[-1]} ]')
        S3.upload(
            body=File.read_byte(temp_path),
            destination=File.vdir(destination_path),
            send=s3
        )
        if save:
            File.write_byte(
                path=File.vdir(destination_path),
                media=File.read_byte(temp_path),
            )
        shutil.rmtree(temp_dir)
        return File.vdir(destination_path)
    
    @staticmethod
    def youtube_download(url):
        logger.info(f'VIDEO DOWNLOAD :: URL [ {url} ]')
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
            'nocheckcertificate': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("Mengunduh video...")
                
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    video_info = info['entries'][0]
                else:
                    video_info = info
                
                formats = video_info.get('formats', [])
                
                # Fungsi untuk mendapatkan ukuran file yang aman
                def safe_get_filesize(f):
                    return f.get('filesize') or f.get('filesize_approx') or 0
                
                # Pilih format terbaik
                best_format = max(formats, key=safe_get_filesize)
                video_url = best_format['url']
                
                # Unduh konten video
                with ydl.urlopen(video_url) as response:
                    video_bytes = response.read()
                
            print("Unduhan selesai!")
            return video_bytes
        except Exception as e:
            print(f"Terjadi kesalahan: {str(e)}")
            return None
        
    # def _upload(body: any, destination: str) -> int:
    #     try:
    #         filepath: str = f"{self.BUCKET}/{destination}"
    #         filename: str = Funct.name_file(filepath)
    #         with self.s3.open(filepath, "wb") as f:
    #             for chunk in body:
    #                 if chunk:
    #                     f.write(chunk)
    #         logger.info(f"File {filename} uploaded to S3 successfully.")
    #         return filepath
    #     except Exception as e:
    #         logger.error("Error uploading file to S3:", e)
    #         return ""

    # def _download(url: str, path: str) -> None:
    #     start = perf_counter()
    #     filename: str = Funct.name_file(path)
    #     logger.info(f"PROCESS DOWNLOAD [ {Funct.name_file(path)} ] :: START [ {Time.now()} ]")
    #     chunks = list()
    #     downloaded = 0
        
    #     for index in range(15):
    #         try:
    #             header = {'Range': f'bytes={downloaded}-'}
    #             headers.update(header)
    #             with requests.get(url, headers=headers, stream=True, timeout=600) as r:
    #                 total_size = downloaded + int(r.headers.get('Content-Length', 0))
    #                 r.raise_for_status()
    #                 file_path = path.replace(self.base_path_s3, "")
    #                 with tqdm(total=total_size, unit='B', unit_scale=True, desc='DOWNLOAD', ncols=100, initial=downloaded) as pbar:
    #                     for chunk in r.iter_content(chunk_size=262144):
    #                         if chunk and chunk not in chunks:
    #                             chunks.append(chunk)
    #                             downloaded += len(chunk)
    #                             pbar.update(len(chunk))
    #                 _upload(chunks, file_path)
    #                 break
    #         except Exception as err:
    #             if index+1 == 15: raise Exception(err)
    #             logger.error(f'MESSAGE [ {err} ] TRY AGAIN [ {index} ]')
    #     logger.info(f"DOWNLOAD [ {filename} ] :: TIME REQUIRED [ {'{:.2f}'.format(perf_counter() - start)} ]")

    
