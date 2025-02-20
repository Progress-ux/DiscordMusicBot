import discord
import asyncio
import yt_dlp as youtube_dl
from discord.ext import commands
from aiohttp_socks import ProxyConnector
import aiohttp

# Настройки прокси
proxy_url = 'YOUR_PROXY_URL' 

async def create_bot():
    # Создание aiohttp-сессии через прокси
    connector = ProxyConnector.from_url(proxy_url)
    session = aiohttp.ClientSession(connector=connector)

    # Создание бота с кастомным HTTP-клиентом
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Настройки YouTube-DL
    YDL_OPTIONS = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    # Отключаем видео, только аудио
    @bot.event
    async def on_ready():
        print(f'✅ Бот запущен как {bot.user}')

    @bot.event
    async def on_message(message):
        print(f"Получено сообщение: {message.content}")
        await bot.process_commands(message)

    @bot.command()
    async def join(ctx):
        """Подключает бота к голосовому каналу"""
        print("Команда !join вызвана")
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"Подключился к каналу {channel}")
        else:
            await ctx.send("Вы должны быть в голосовом канале!")

    @bot.command()
    async def leave(ctx):
        """Отключает бота из голосового канала"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("Бот не в голосовом канале!")


    @bot.command()
    async def play(ctx, url: str):
        """Воспроизводит музыку из YouTube"""
        voice_channel = ctx.voice_client

        # Подключаемся к каналу, если бота нет в голосовом канале
        if not voice_channel:
            await ctx.invoke(join)
            voice_channel = ctx.voice_client

        if voice_channel is None:
            await ctx.send("Не удалось подключиться к голосовому каналу!")
            return

        try:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info.get('url', None)  # Поправленный вариант
                title = info.get('title', 'Неизвестный трек')

                if not url2:
                    await ctx.send("⚠ Не удалось получить ссылку на аудиофайл!")
                    return

                await ctx.send(f"🎶 Найден трек: {title}")
        except Exception as e:
            await ctx.send(f"❌ Ошибка загрузки: {e}")
            return

        # Если в голосовом канале уже идет воспроизведение
        if voice_channel.is_playing():
            voice_channel.stop()

        # Воспроизведение трека
        source = discord.FFmpegPCMAudio(url2, executable="C:/ffmpeg/bin/ffmpeg.exe", **FFMPEG_OPTIONS) # Необходимо указать путь к ffmpeg(у вас может быть свой)
        voice_channel.play(source)

        await ctx.send(f"▶ Начинаю играть: {title}")

    @bot.command()
    async def pause(ctx):
        """Ставит музыку на паузу"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸ Музыка на паузе")
        else:
            await ctx.send("Сейчас ничего не играет!")

    @bot.command()
    async def resume(ctx):
        """Возобновляет воспроизведение"""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶ Музыка продолжается")
        else:
            await ctx.send("Музыка не на паузе!")

    @bot.command()
    async def stop(ctx):
        """Останавливает музыку"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏹ Музыка остановлена")
        else:
            await ctx.send("Сейчас ничего не играет!")

    # Запуск бота
    await bot.start("your_token")
    
# Запуск бота в асинхронном контексте
asyncio.run(create_bot())
