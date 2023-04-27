import yt_dlp
import discord
from typing import Optional

YDL_OPTS = dict(
    format='bestaudio/best',
    postprocessors=[dict(key='FFmpegExtractAudio')],
    noplaylist=True
)

FFMPEG_OPTIONS = dict(
    options='-vn',
    before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
)


def download(url: str):
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        try:
            return ydl.extract_info(url, False)
        except yt_dlp.DownloadError:
            pass


class Session:
    def __init__(self):
        self.song_info: Optional[dict[str]] = None
        self.queue: list[dict[str]] = []
        self.looping = False
        self.frozen = False
        self.message: Optional[discord.InteractionMessage] = None

    def after(self, voice: discord.VoiceClient):
        def after(error: Optional[Exception] = None):
            if error is not None:
                raise error
            if self.frozen:
                self.frozen = False
                return
            if not self.looping:
                self.next_song()
            if not voice.is_connected():
                return
            if self.song_info is None:
                return
            self.play(voice, self.song_info, True)
        return after

    def next_song(self):
        self.song_info = self.queue.pop(0) if self.queue else None

    def play(
        self,
        voice: discord.VoiceClient,
        song_info: dict[str],
        skip=False
    ):
        if self.song_info is not None:
            if not skip:
                self.queue.append(song_info)
                return
            self.stop(voice)
        source = discord.FFmpegPCMAudio(song_info['url'], **FFMPEG_OPTIONS)
        voice.play(source, after=self.after(voice))
        self.song_info = song_info

    def skip(self, voice: discord.VoiceClient):
        self.stop(voice)
        self.next_song()
        if self.song_info is None:
            return
        self.play(voice, self.song_info, skip=True)

    def stop(self, voice: discord.VoiceClient):
        if voice.is_playing() or voice.is_paused():
            self.frozen = True
            voice.stop()
