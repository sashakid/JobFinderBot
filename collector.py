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

# Каналы для обхода
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

# Ключевые слова для поиска
keywords = [' ios']

# Ключевые слова для исключения
exclude_keywords = [
    'flutter', 'не вакансия', 'Project Manager', 'ASO', 'CV по запросу',
    'kotlin', '#ищу', 'Product Designer', 'QA Engineer', 'React Native',
    '#qa', '𝐏𝐑 𝐌𝐚𝐧𝐚𝐠𝐞𝐫', 'USER ACQUISITION', '#CV', 'Оператор колл-центра',
    '#devops', '#aqa', '#TechArtist', '#ProductManager'
]

# Настройка даты
days_back = 3
since_date = datetime.now(timezone.utc) - timedelta(days=days_back)

client = TelegramClient('session_name', api_id, api_hash)


async def clear_channel(channel_username_or_id):
    """Удаляет все сообщения из целевого канала."""
    await client.start()
    entity = await client.get_entity(channel_username_or_id)

    async for msg in client.iter_messages(entity, reverse=True):
        try:
            await msg.delete()
            print(f"🗑 Deleted message {msg.id}")
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"Не удалось удалить сообщение {msg.id}: {e}")

    print("✅ Очистка завершена.")


async def search_and_send():
    """Ищет сообщения по ключевым словам и пересылает их в целевой канал."""
    await client.start()
    print("🚀 Userbot запущен")

    try:
        target_entity = await client.get_entity(target_channel)
    except Exception as e:
        print(f"Ошибка при получении target_channel: {e}")
        await client.disconnect()
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

                # Условие поиска: есть нужное слово и нет исключённых слов
                if any(word in text_lower for word in (kw.lower() for kw in keywords)) \
                        and not any(bad in text_lower for bad in (ex.lower() for ex in exclude_keywords)):

                    # for kw in keywords:
                    #     pos = text_lower.find(kw.lower())
                    #     if pos != -1:
                    #         # получаем слова вокруг
                    #         words = msg.text.split()
                    #         idx = next((i for i, w in enumerate(
                    #             words) if kw.lower() in w.lower()), None)
                    #         if idx is not None:
                    #             left = max(0, idx - 5)
                    #             right = min(len(words), idx + 6)
                    #             snippet = ' '.join(words[left:right])
                    #             title = msg.text.strip().split('\n', 1)[0]
                    #             print(f"[{channel}] {title[:120]} | …{snippet}…")

                    text = f"📢 [{channel}] {msg.date.strftime('%Y-%m-%d %H:%M')}\n\n{msg.text[:4000]}"
                    try:
                        await client.send_message(target_entity, text)
                        await asyncio.sleep(3)
                    except FloodWaitError as e:
                        resume_time = datetime.now() + timedelta(seconds=e.seconds)
                        print(
                            f"⏸ FloodWait на {e.seconds} сек. Ждём до {resume_time.strftime('%Y-%m-%d %H:%M:%S')}...")
                        await asyncio.sleep(e.seconds)
                        print("▶ Возобновляем отправку...")
                        await client.send_message(target_entity, text)

        except Exception as e:
            print(f"Ошибка при обработке {channel}: {e}")

    await client.disconnect()
    print("🏁 Готово.")


async def main():
    await clear_channel(target_channel)
    await search_and_send()

if __name__ == '__main__':
    asyncio.run(main())
