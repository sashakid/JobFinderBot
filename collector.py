import os
import asyncio
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
target_channel = int(os.getenv("TARGET_CHANNEL"))

channels = [
    'jobGeeks', 'myjobit', 'jc_it', 'evacuatejobs', 'remocate', 'normrabota',
    'iOS_Devv_Jobs', 'Getitrussia', 'Remoteit', 'devs_it', 'headzio',
    'onlinevakansii', 'forallmobile', 'perezvonyu', 'workingincrypto',
    'notificaJobs_iOS', 'mobjobskz', 'it_jobs_armenia', 'georgiaitjobs',
    'jobsearchIT', 'jobsnit', 'zarubezhom_jobs', 'hr_breakfast_emergency',
    'serbia_jobs', 'cyprusithr', 'opento_relocate', 'cvjobge', 'relocaty_jobs',
    'Pol_relocation', 'rem0te', 'it_vakansii_jobs', 'remote_jobs_relocate',
    'careers_crypto', 'employ_work', 'Vakansii1_Rabota', 'Rabotau_Vakansii',
    'Vakansii_Rabotal'
]

keywords = [' ios']
exclude_keywords = [
    'flutter', 'не вакансия', 'Project Manager', 'ASO', 'CV по запросу',
    'kotlin', '#ищу', 'Product Designer', 'QA Engineer', 'React Native',
    '#qa', '𝐏𝐑 𝐌𝐚𝐧𝐚𝐠𝐞𝐫', 'USER ACQUISITION', '#CV', 'Оператор колл-центра',
    '#devops', '#aqa', '#TechArtist', '#ProductManager', '#System_analyst'
]

client = TelegramClient('session_name', api_id, api_hash)


async def clear_channel(channel_username_or_id):
    entity = await client.get_entity(channel_username_or_id)
    async for msg in client.iter_messages(entity, reverse=True):
        try:
            await msg.delete()
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"Не удалось удалить сообщение {msg.id}: {e}")


async def search_and_send(days_back=1):
    await client.start()
    since_date = datetime.now(timezone.utc) - timedelta(days=days_back)
    try:
        target_entity = await client.get_entity(target_channel)
    except Exception as e:
        print(f"Ошибка при получении target_channel: {e}")
        return

    for channel in channels:
        try:
            entity = await client.get_entity(channel)
            async for msg in client.iter_messages(entity):
                if msg.date < since_date:
                    break
                if not msg.text:
                    continue

                text_lower = msg.text.lower()
                if any(word in text_lower for word in (kw.lower() for kw in keywords)) \
                        and not any(bad in text_lower for bad in (ex.lower() for ex in exclude_keywords)):
                    text = f"📢 [{channel}] {msg.date.strftime('%Y-%m-%d %H:%M UTC')}\n\n{msg.text[:4000]}"
                    try:
                        await client.send_message(target_entity, text)
                        await asyncio.sleep(3)
                    except FloodWaitError as e:
                        print(f"⏸ FloodWait {e.seconds} сек")
                        await asyncio.sleep(e.seconds)
                        await client.send_message(target_entity, text)
        except Exception as e:
            print(f"Ошибка при обработке {channel}: {e}")


async def daily_task(hour, minute):
    """Запуск задачи каждый день в указанное время UTC."""
    while True:
        now = datetime.now(timezone.utc)
        target_time = datetime(
            year=now.year, month=now.month, day=now.day,
            hour=hour, minute=minute, second=0, tzinfo=timezone.utc
        )
        if target_time <= now:
            target_time += timedelta(days=1)

        wait_seconds = (target_time - now).total_seconds()
        print(f"Ждём {int(wait_seconds)} секунд до следующего запуска (UTC)...")
        await asyncio.sleep(wait_seconds)

        print("🧹 Очистка канала перед сбором сообщений")
        await clear_channel(target_channel)

        print("🚀 Запуск сбора сообщений за последние сутки")
        await search_and_send(days_back=1)
        print("🏁 Задача выполнена. Ждём следующий день...")


if __name__ == '__main__':
    # Здесь указываешь точное время UTC, например 10:00 UTC
    asyncio.run(daily_task(hour=11, minute=0))
