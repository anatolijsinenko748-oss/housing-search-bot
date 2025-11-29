# housing-search-bot — поиск жилья в Telegram

Асинхронный Telegram-бот для поиска квартир в аренду с реальными объявлениями с ЦИАН.

Статус: MVP готов, в активной разработке

Технологии
Python 3.12 · aiogram 3.13 · SQLAlchemy 2.0 · Docker · httpx + selectolax

Возможности (уже работают)
- Поиск по городу и цене
- Реальный парсинг ЦИАН в режиме онлайн (обновляется каждые несколько минут)
- Сохранение истории поисков и пользователей
- Чистая архитектура (роутеры, состояния, pydantic-settings)


Скриншоты
1[](/screenshots/1.png)
2[](/screenshots/2.png)


Запуск локально
```bash
git clone https://github.com/anatolijsinenko748-oss/housing-search-bot.git
cd housing-search-bot
cp .env.example .env           # вставить свой BOT_TOKEN
pip install -r requirements.txt
python create_db.py
python -m bot.main


Планы развития (скоро)

Tinder-подобный UX (лайки / дизлайки)
Избранное и уведомления о новых подходящих квартирах
Парсинг Авито + Яндекс.Недвижимости
Веб-версия на FastAPI + React

Автор
Анатолий Аргунов · @anatoliy_dev · anatolijsinenko748@gmail.com