from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_cancel = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Отмена')]],
    resize_keyboard= True,
    one_time_keyboard=True
)

kb_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Новый Поиск')],
        [KeyboardButton(text='Помощь')],
        [KeyboardButton(text='Показать последние результаты')]
    ],
    resize_keyboard=True
)