import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
from openai import AsyncOpenAI

load_dotenv()
API_ID = int(os.getenv('TELEGRAM_API_ID'))
API_HASH = os.getenv('TELEGRAM_API_HASH')
AI_KEY = os.getenv('TOKENROUTER_API_KEY')

# Настраиваем ИИ-клиент на эндпоинт TokenRouter
ai_client = AsyncOpenAI(
    api_key=AI_KEY,
    base_url="https://cortex.tokenrouter.io/v1" # Проверь точный URL в документации на сайте TokenRouter
)

client = TelegramClient('kiro', API_ID, API_HASH)
TARGET_CHATS = [] # Впиши юзернеймы нужных чатов, например: ['@chat1', '@chat2']

async def is_b2b_lead(text: str) -> bool:
    prompt = f"Я Full-stack разработчик с упором на Backend (Python, FastAPI, Telegram-боты, парсеры, React/TS). Это сообщение — релевантный B2B-заказ или поиск исполнителя на разработку? Ответь только 'да' или 'нет'. Текст: {text}"
    try:
        response = await ai_client.chat.completions.create(
            model="openai/gpt-5.4-nano",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.1
        )
        answer = response.choices[0].message.content.strip().lower()
        return 'да' in answer
    except Exception as e:
        print(f"Ошибка ИИ-фильтра: {e}")
        return False

@client.on(events.NewMessage(chats=TARGET_CHATS))
async def handler(event):
    if not event.message.text:
        return
        
    print("⏳ Анализирую новое сообщение...")
    if await is_b2b_lead(event.message.text):
        sender = await event.get_sender()
        username = f"@{sender.username}" if getattr(sender, 'username', None) else "Скрыт"
        msg = f"🔥 **НОВЫЙ ЛИД (Одобрено ИИ)**\n👤 Отправитель: {username}\n\n{event.message.text}"
        
        await client.send_message('me', msg)
        print(f"✅ Профитный лид от {username} перехвачен и отправлен в Избранное!")

with client:
    print("🕷️ Паук Kiro с ИИ-мозгом запущен! Мониторю чаты...")
    client.run_until_disconnected()
