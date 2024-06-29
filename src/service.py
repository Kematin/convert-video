import os
import subprocess

from exceptions import DownloadError
from pytube import YouTube
from pytube.exceptions import RegexMatchError

filename = str


class Worker:
    async def delete_file(self, filename: str):
        os.remove(filename)


class ConvertUserVideo(Worker):
    async def convert(self, filename: str):
        new_filename = filename[:-4] + ".mp3"
        command = f"ffmpeg -i '{filename}' -b:a 320k '{new_filename}'"
        subprocess.call(command, shell=True)
        await self.delete_file(filename)
        return new_filename


class YoutubeDownload(Worker):
    async def download_from_youtube(self, url: str) -> filename:
        try:
            yt = YouTube(url)
            streams = yt.streams.filter(only_audio=True)
            filename = streams.first().download()
            filename = await self.rename_file(filename)
            return filename
        except RegexMatchError:
            raise DownloadError

    async def rename_file(self, path: str) -> filename:
        old_path = f"{path}"
        new_path = f"{path}"[:-4] + ".mp3"
        os.rename(old_path, new_path)

        return new_path


if __name__ == "__main__":
    import asyncio

    # url = "https://www.youtube.com/watch?v=IRiVW6ht_nI"
    # yt = YoutubeDownload()

    filename = "Billie Eilish - Lost Cause (Official Music Video).mp4"
    ct = ConvertUserVideo()

    asyncio.run(ct.convert(filename))
