# ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
# ─████████──████████─██████──██████─████████████████───██████████████────████████████───██████████████─████████──████████─██████████████─████████████████───
# ─██░░░░██──██░░░░██─██░░██──██░░██─██░░░░░░░░░░░░██───██░░░░░░░░░░██────██░░░░░░░░████─██░░░░░░░░░░██─██░░░░██──██░░░░██─██░░░░░░░░░░██─██░░░░░░░░░░░░██───
# ─████░░██──██░░████─██░░██──██░░██─██░░████████░░██───██░░██████░░██────██░░████░░░░██─██░░██████░░██─████░░██──██░░████─██░░██████████─██░░████████░░██───
# ───██░░░░██░░░░██───██░░██──██░░██─██░░██────██░░██───██░░██──██░░██────██░░██──██░░██─██░░██──██░░██───██░░░░██░░░░██───██░░██─────────██░░██────██░░██───
# ───████░░░░░░████───██░░██──██░░██─██░░████████░░██───██░░██████░░██────██░░██──██░░██─██░░██──██░░██───████░░░░░░████───██░░██████████─██░░████████░░██───
# ─────████░░████─────██░░██──██░░██─██░░░░░░░░░░░░██───██░░░░░░░░░░██────██░░██──██░░██─██░░██──██░░██─────██░░░░░░██─────██░░░░░░░░░░██─██░░░░░░░░░░░░██───
# ───────██░░██───────██░░██──██░░██─██░░██████░░████───██░░██████░░██────██░░██──██░░██─██░░██──██░░██───████░░░░░░████───██░░██████████─██░░██████░░████───
# ───────██░░██───────██░░██──██░░██─██░░██──██░░██─────██░░██──██░░██────██░░██──██░░██─██░░██──██░░██───██░░░░██░░░░██───██░░██─────────██░░██──██░░██─────
# ───────██░░██───────██░░██████░░██─██░░██──██░░██████─██░░██──██░░██────██░░████░░░░██─██░░██████░░██─████░░██──██░░████─██░░██████████─██░░██──██░░██████─
# ───────██░░██───────██░░░░░░░░░░██─██░░██──██░░░░░░██─██░░██──██░░██────██░░░░░░░░████─██░░░░░░░░░░██─██░░░░██──██░░░░██─██░░░░░░░░░░██─██░░██──██░░░░░░██─
# ───────██████───────██████████████─██████──██████████─██████──██████────████████████───██████████████─████████──████████─██████████████─██████──██████████─
# ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# Telegram channel @zamerz_typing 


import asyncio
import json
import os
import random
from telethon import TelegramClient, events
import psycopg2
from psycopg2.extras import RealDictCursor

api_id = "введите свой"
api_hash = "введите свой"
phone = "введите свой"
owner_id = "введите свой"
database_url = os.getenv('DATABASE_URL')

comments = [
    'гад факин дэээм',
    'потужно',
    'ичо'
]

client = TelegramClient(
    'session', 
    api_id, 
    api_hash,
    connection_retries=None,
    retry_delay=1,
    auto_reconnect=True,
    flood_sleep_threshold=0
)

monitored_channels = []

def get_db_connection():
    if not database_url:
        return None
    return psycopg2.connect(database_url, sslmode='require')

def init_db():
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    try:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id BIGINT PRIMARY KEY,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f'DB init error: {e}')
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def load_channels():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute('SELECT channel_id FROM channels')
        channels = [row[0] for row in cur.fetchall()]
        cur.close()
        return channels
    except Exception as e:
        print(f'Load channels error: {e}')
        return []
    finally:
        conn.close()

def add_channel_db(channel_id):
    conn = get_db_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO channels (channel_id) VALUES (%s) ON CONFLICT DO NOTHING', (channel_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f'Add channel error: {e}')
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def remove_channel_db(channel_id):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute('DELETE FROM channels WHERE channel_id = %s', (channel_id,))
        deleted = cur.rowcount > 0
        conn.commit()
        cur.close()
        return deleted
    except Exception as e:
        print(f'Remove channel error: {e}')
        return False
    finally:
        conn.close()

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.add (-?\d+)$'))
async def add_channel(event):
    if event.sender_id != owner_id:
        return
    
    channel_id = int(event.pattern_match.group(1))
    
    try:
        entity = await client.get_entity(channel_id)
        
        if channel_id not in monitored_channels:
            if add_channel_db(channel_id):
                monitored_channels.append(channel_id)
                await event.edit(f'Канал добавлен: {entity.title} (ID: {channel_id})')
            else:
                await event.edit(f'Ошибка добавления')
        else:
            await event.edit(f'Канал уже в списке: {entity.title}')
    except Exception as e:
        await event.edit(f'Ошибка: {str(e)}')
    
    await asyncio.sleep(5)
    await event.delete()

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.remove (-?\d+)$'))
async def remove_channel(event):
    if event.sender_id != owner_id:
        return
    
    channel_id = int(event.pattern_match.group(1))
    
    if remove_channel_db(channel_id):
        if channel_id in monitored_channels:
            monitored_channels.remove(channel_id)
        await event.edit(f'Канал удален (ID: {channel_id})')
    else:
        await event.edit(f'Канал не найден в списке')
    
    await asyncio.sleep(5)
    await event.delete()

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.list$'))
async def list_channels(event):
    if event.sender_id != owner_id:
        return
    
    if not monitored_channels:
        await event.edit('Список пуст')
    else:
        text = 'Отслеживаемые каналы:\n\n'
        for channel_id in monitored_channels:
            try:
                entity = await client.get_entity(channel_id)
                text += f'{entity.title} (ID: {channel_id})\n'
            except:
                text += f'ID: {channel_id} (недоступен)\n'
        
        await event.edit(text)
    
    await asyncio.sleep(10)
    await event.delete()

@client.on(events.NewMessage())
async def auto_comment(event):
    global monitored_channels
    
    if event.chat_id not in monitored_channels:
        return
    
    if event.out:
        return
    
    try:
        await asyncio.sleep(random.uniform(3, 5))
        
        comment = random.choice(comments)
        await asyncio.sleep(2)
        await client.send_message(
            entity=event.chat_id,
            message=comment,
            comment_to=event.id
        )
        
    except Exception as e:
        error_str = str(e).lower()
        print(f'Ошибка автокомментария: {e}')
        
        ban_keywords = [
            'private and you lack permission',
            'you were banned',
            "you can't write in this chat",
            'you can\'t write in this chat',
            'access is denied'
        ]
        
        is_banned = any(keyword in error_str for keyword in ban_keywords)
        
        if is_banned and event.chat_id in monitored_channels:
            monitored_channels.remove(event.chat_id)
            remove_channel_db(event.chat_id)
            try:
                await client.send_message(owner_id, f'Канал {event.chat_id} удален из списка из-за: {str(e)[:100]}')
            except:
                pass

async def main():
    global monitored_channels
    
    init_db()
    monitored_channels = load_channels()
    
    await client.start(phone)
    print(" запущен")
    print(f'Отслеживается : {len(monitored_channels)}')
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())

