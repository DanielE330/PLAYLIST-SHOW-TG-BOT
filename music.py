import telebot
import requests
from yandex_music import Client
from yandex_music.exceptions import UnauthorizedError
import os
import tempfile
from telebot import types

TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
YA_MUSIC_TOKEN = 'TOKEN_YA.MUSIC'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def get_reversed_tracks(client):
    tracks = client.users_likes_tracks()
    return list(reversed(tracks)) if tracks else []

def get_track_info(track):
    title = track.title
    artists = ', '.join(artist.name for artist in track.artists)
    return title, artists

def get_mp3_url(track):
    try:
        download_info = track.get_download_info(get_direct_links=True)
        for info in download_info:
            if info.codec == 'mp3':
                return info.get_direct_link()
        return None
    except Exception as e:
        print(f"Ошибка при получении ссылки: {e}")
        return None

def send_track_as_mp3(chat_id, track):
    try:
        url = get_mp3_url(track)
        if not url:
            return False
            
        with tempfile.TemporaryDirectory() as tmp_dir:
            response = requests.get(url)
            response.raise_for_status()
            
            file_path = os.path.join(tmp_dir, 'track.mp3')
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            title, artists = get_track_info(track)
            
            with open(file_path, 'rb') as audio_file:
                bot.send_audio(
                    chat_id,
                    audio_file,
                    title=title,
                    performer=artists,
                    timeout=60
                )
        return True
    except Exception as e:
        print(f"Ошибка при отправке трека: {e}")
        return False

@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.InlineKeyboardMarkup()
    btn_all = types.InlineKeyboardButton("Все треки", callback_data='all')
    btn_range = types.InlineKeyboardButton("Выбрать номера", callback_data='range')
    markup.add(btn_all, btn_range)
    
    welcome_text = (
        "Добро пожаловать!\n"
        "Нумерация начинается с *последнего* добавленного трека:\n"
        "1 — самый новый\n"
        "2 — предпоследний\n"
        "И так далее..."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    try:
        client = Client(YA_MUSIC_TOKEN).init()
        reversed_tracks = get_reversed_tracks(client)
        
        if not reversed_tracks:
            bot.send_message(chat_id, "Ваш плейлист пуст!")
            return
            
        if call.data == 'all':
            bot.send_message(chat_id, "Начинаю загрузку всех треков, начиная с самого нового...")
            send_tracks(chat_id, reversed_tracks)
            
        elif call.data == 'range':
            msg = bot.send_message(
                chat_id, 
                f"Введите диапазон (всего {len(reversed_tracks)} треков)\n"
                "Примеры:\n"
                "• 1-3 — 3 последних добавленных трека\n"
                "• 5 — пятый по новизне\n"
                "• 2-4 — предпоследние три трека"
            )
            bot.register_next_step_handler(msg, lambda m: process_range(m, reversed_tracks))
            
    except UnauthorizedError:
        bot.send_message(chat_id, "Ошибка авторизации!")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка: {str(e)}")

def process_range(message, reversed_tracks):
    chat_id = message.chat.id
    try:
        total = len(reversed_tracks)
        input_text = message.text.strip()
        
        if '-' in input_text:
            start, end = map(int, input_text.split('-'))
        else:
            start = end = int(input_text)
        
        if start < 1 or end > total or start > end:
            bot.send_message(chat_id, f"Некорректный диапазон. Доступно: 1-{total}")
            return
            
        selected_tracks = reversed_tracks[start-1:end]
        bot.send_message(chat_id, f"Загружаю треки с {start} по {end} позицию...")
        send_tracks(chat_id, selected_tracks)
        
    except ValueError:
        bot.send_message(chat_id, "Используйте числовой формат (например: 1-5)")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка: {str(e)}")

def send_tracks(chat_id, tracks):
    success = 0
    total = len(tracks)
    for i, track_short in enumerate(tracks, 1):
        try:
            track = track_short.fetch_track()
            if send_track_as_mp3(chat_id, track):
                success += 1
            
            # Показываем прогресс только для каждого 10-го трека или последнего
            if i % 10 == 0 or i == total:
                bot.send_message(
                    chat_id, 
                    f"Прогресс: обработано {i} из {total} треков\n"
                    f"Успешно: {success} треков"
                )
        except Exception as e:
            print(f"Ошибка: {e}")
    
    bot.send_message(
        chat_id,
        f"Завершено!\n"
        f"Всего треков: {total}\n"
        f"Успешно отправлено: {success}\n"
        f"Не удалось отправить: {total - success}"
    )

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()