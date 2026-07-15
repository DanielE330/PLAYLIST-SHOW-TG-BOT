# 🎧 PLAYLIST-SHOW-TG-BOT

> Telegram-бот на Python, который показывает и присылает MP3 понравившихся треков из Яндекс.Музыки.

---

## ✨ Функционал

- Забирает список лайкнутых треков через [Yandex Music API](https://github.com/MarshalX/yandex-music-api)
- Достаёт прямые ссылки на MP3 и отправляет их в чат
- Работает через [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/)

## ⚙️ Настройка

| Файл | Назначение |
|---|---|
| `TG_TOKEN.txt` | Токен Telegram-бота (⚠️ храните локально, не коммитьте реальный токен) |
| `YA_TOKEN.txt` | Токен доступа к Яндекс.Музыке (⚠️ храните локально, не коммитьте реальный токен) |

## 🏃 Запуск

```bash
pip install pyTelegramBotAPI requests yandex-music
python music.py
```

Либо готовый исполняемый файл из [`exe file`](https://github.com/DanielE330/PLAYLIST-SHOW-TG-BOT/tree/main/exe%20file) — для Windows без установки Python.
