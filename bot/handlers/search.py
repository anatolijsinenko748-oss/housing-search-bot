from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from sqlalchemy import select, desc
from states.search import SearchStates
from keyboards.reply import kb_cancel, kb_main_menu
from data.fake_data import FakeDataGenerator
from database.models import User, Search
from database.db_helper import async_session_maker
from parser.cian import search_cian


#Здесь функция для получения или создания пользователя в базе данных
async def get_or_create_user(message : Message) -> User:
    async with async_session_maker() as sessions:
        result = await sessions.execute(
            select(User).where(User.telegram_id == message.from_user.id) # type: ignore
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                telegram_id=message.from_user.id, # type: ignore
                username=message.from_user.username, # type: ignore
                first_name=message.from_user.first_name # type: ignore
            )
            sessions.add(user)
            await sessions.commit()
        return user
    

'''

    Представленны классы состояний

'''

router = Router(name='search_router')

#Роутер для команды /start
@router.message (CommandStart())
async def cmd_start(message : Message, state : FSMContext):
    await state.clear()

    user = await get_or_create_user(message)

    await state.update_data(current_user=user)

    await message.answer(
        f'Привет, {message.from_user.first_name}! Я помогу тебе найти кваритиру/дом.\nВ каком городе ищем?', # type: ignore
        reply_markup=kb_cancel
    )
    
    await state.set_state(SearchStates.waiting_for_city)

#Роутер для команды /cancel и кнопки "Отмена"
@router.message(F.text.lower() == 'отмена')        
async def cancel_heandler(message : Message, state : FSMContext):
    await state.clear()
    await message.answer('Поиск отменен. Чем займемся?', reply_markup=kb_main_menu)

#Роутер для кнопки "Новый Поиск"
@router.message(F.text == 'Новый Поиск')
async def new_search(message : Message, state : FSMContext):
    await cmd_start(message, state)

#Роутер для кнопки "Показать последние результаты"
@router.message(F.text == 'Показать последние результаты')
async def show_last_results(message : Message, state : FSMContext):
    async with async_session_maker() as sessions: # with - что бы после использования сессия она закрывалась автоматически
                                                  # Нужен для каждого обращения к базе данных

        user = await sessions.scalar(
            select(User).where(User.telegram_id == message.from_user.id) # type: ignore
        )

        if not user:
            await message.answer('Вы еще не зарегестрированны в боте')
            return

        result = await sessions.execute(
            select(Search)
            .where(Search.user_id == user.id) # type: ignore
            .order_by(desc(Search.created_at))
            .limit(10)
        )
        searches_list =  result.scalars().all()

        if not searches_list:
            await message.answer('У вас пока нет сохраненных поисков', reply_markup=kb_main_menu)
            return
        
        text = 'Ваши последние поиски: \n\n'

        for s in searches_list:
            text += f'{s.city}: {s.min_price:,} - {s.max_price:,} рублей\n'

        await message.answer(text, reply_markup=kb_main_menu)



@router.message(SearchStates.waiting_for_city) 
async def process_city(message : Message, state : FSMContext):
    if message.text.strip().lower() == 'отмена': # type: ignore
        return await cancel_heandler(message, state)
    
    city = message.text
    await state.update_data(city=city)
    await message.answer('Введите теперь минимальную цена за квартиру')
    await state.set_state(SearchStates.waiting_for_min_price)


@router.message(SearchStates.waiting_for_min_price)    
async def search_min_price(message : Message, state : FSMContext):
    if message.text.strip().lower() == 'отмена': # type: ignore
        return await cancel_heandler(message, state)
    
    text = message.text.strip() # type: ignore
    if not text.isdigit():
        await message.answer('Пожалуйста введите число')
        return
    
    min_price = int(text)
    if min_price < 0:
        await message.answer('Цена должна быть больше 0')
        return
    
    await state.update_data(min_price=min_price)
    await message.answer('Введите макисмальную цену в месяц', reply_markup=kb_cancel)
    await state.set_state(SearchStates.waiting_for_max_price)


@router.message(SearchStates.waiting_for_max_price) 
async def process_max_price(message : Message, state : FSMContext): 
    
    if message.text.strip().lower() == 'Отмена': # type: ignore
        return await cancel_heandler(message, state)
        
    text = message.text.strip() # type: ignore

    if not text.isdigit():
        await message.answer('Введите пожалуйста число')
        return
    
    max_price = int(text)

    if max_price <= 0:
        await message.answer('Сумма не должна быть меньше 0')
        return
    
    user_data = await state.get_data()

    if user_data['min_price'] > max_price:
        await message.answer('Максимальная цена не может быть меньше минимальной!')
        return
  
    await state.update_data(max_price=max_price)

    async with async_session_maker() as sessions:
        user = user_data['current_user']

        new_search = Search(
            user_id = user.id,
            city=user_data['city'],
            min_price=user_data['min_price'],
            max_price=max_price
        )
        sessions.add(new_search)
        await sessions.commit()

    appartments = await search_cian(
        city=user_data['city'],
        min_price=user_data['min_price'],
        max_price=max_price,
        limit=10
    )

    await message.answer(
        f'Ваши парметры:\n'
        f'Город: {user_data['city']}\n'
        f'Цена: {user_data["min_price"]:,} - {max_price:,} рублей \n\n'
        f'Найдено вариантов: {len(appartments)}',
        reply_markup=kb_cancel
    )

    for apt in appartments:
        if not apt.get('link'):
            continue

        text = (
            f"{apt.get('title', 'Квартира в аренду')}\n"
            f"Цена: {apt.get('price', 'Не указана'):,} рублей\n"
            f"Источники: {apt.get('source')}\n\n"
            f"Подробности: {apt.get('link')}"
        )
        
        if apt.get('photo'):
            await message.answer_photo(
                photo=apt['photo'],
                caption=text,
                reply_markup=kb_cancel
            )
        else:
            await message.answer(text, reply_markup=kb_cancel)
          




