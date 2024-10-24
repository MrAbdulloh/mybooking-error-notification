import asyncio

import requests
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message

from logger import setup_logger

API_TOKEN = '5519984673:AAG9VKRQBB-c08Q04XPRN0zHELh90HGyyWY'
CHAT_ID = '-1002245220290'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logger = setup_logger()

# Список сайтов
username = "main24"
password = "saas24"
timeout = 5

sites = [
    "https://mybooking.uz",
    f"https://{username}:{password}@oops.mybooking.uz",
    "https://hotel.mybooking.uz"
]

monitoring_task = None


async def send_request(url):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200, response
    except requests.Timeout as e:
        return False, f"Timeout: {str(e)}"
    except requests.RequestException as e:
        return False, f"Request Exception: {str(e)}"
    except Exception as e:
        return False, f"Unexpected Error: {str(e)}"


async def check_site(url):
    for attempt in range(1, 4):
        logger.info(f"{url}: {attempt}-й запрос отправляется...")
        success, response = await send_request(url)
        if success:
            logger.info(f"{url}: {attempt}-й запрос успешен!")
            return True
        logger.warning(f"{url}: {attempt}-й запрос завершился таймаутом или ошибкой.")
    return response


async def monitor_requests():
    global monitoring_task
    while True:
        logger.info("Началась проверка...")
        for url in sites:
            error_info = await check_site(url)
            if error_info is not True:
                logger.error(f"{url}: Все 3 запроса не удались. Отправляем сообщение в Telegram...")
                error_msg = (f"Ошибка\n: {url} завершился таймаутом или ошибкой.\n\n"
                             f"Детали\n: {error_info}")
                await bot.send_message(CHAT_ID, error_msg)
        await asyncio.sleep(10)


@dp.message_handler(commands=['start'])
async def start_monitoring(message: Message):
    global monitoring_task
    if monitoring_task is None:
        monitoring_task = asyncio.create_task(monitor_requests())
        await message.answer("Мониторинг начат, проверяется каждые 2 минуты.")
    else:
        await message.answer("Мониторинг уже продолжается.")


@dp.message_handler(commands=['stop'])
async def stop_monitoring(message: Message):
    global monitoring_task
    if monitoring_task is not None:
        monitoring_task.cancel()
        monitoring_task = None
        await message.answer("Мониторинг остановлен.")
    else:
        await message.answer("Мониторинг в настоящее время не выполняется.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
