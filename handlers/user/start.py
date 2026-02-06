from aiogram.filters import CommandStart, CommandObject
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
from aiogram.types import CallbackQuery, Message
from data.loader import rt, bot
from utils.db.api.user import DBuser
from utils.system.inline_btns import create_markup
from handlers.admin.start import del_mes


class UserState(StatesGroup):
    sing = State()
    sell = State()
    sell_sum = State()
    sell_card = State()
    buy = State()
    buy_sum = State()
    buy_card = State()
    trade = State()
    trade2 = State()
    trade_sum = State()
    trade_card = State()


@rt.message(UserState.sing)
async def sing_message(message: Message):
    """удаляет сообщения"""
    try:
        await del_mes(message.from_user.id, message.message_id)
    except Exception:
        pass


@rt.message(CommandStart())
async def start_message(message: Message, state: FSMContext, command: CommandObject):
    if await DBuser.check_user(message.from_user.id) == False:
        if command:
            try:
                refka = message.text.split(" ")
                await DBuser.add_ref(message.from_user.id, refka[1])
                await bot.send_message(chat_id=refka[1], text=f"Твой новый реферал @{message.from_user.username}")
            except Exception:
                pass
            ref = f"https://t.me/testi222_bot?start={message.from_user.id}"
            await DBuser.add_new(message.from_user.id, f'@{message.from_user.username}', ref)
            markup = await create_markup('inline', [[['Купить', 'buy'], ['Продать', 'sell']],
                                                [['Обменять', 'trade']],
                                                [["О нас", "we"]],
                                                [["📚 FAQ", "url.com"]],
                                                [["👤 Мой профиль", "profile"]]])
            photo = FSInputFile(f"photo\main.jpg", 'rb')
            name = await bot.get_me()
            await bot.send_photo(caption=f"""Привет, <b>{message.from_user.full_name}</b>. Добро пожаловать в бота по обмену криптовалют <b>{name.first_name}</b>.

🤖Это обмен в Telegram нового поколения. 
🔥Удобный интерфейс. 
👤Поддержка на связи 24/7. 
✅Только актуальные и выгодные курсы для наших клиентов.

⚡️БЫСТРЫЙ автоматический обмен.
⚡️Начните обмен с нами сейчас и ощутите преимущества простоты и удобства!
⚡️Покупайте криптовалюту быстро, анонимно и безопасно. 👇


Чтобы осуществить обмен, жмите кнопку “Купить” / “Продать” / “Обменять”. Выбирайте нужную криптовалюту и вводите сумму. Готово!""",
                reply_markup=markup, photo=photo, chat_id=message.from_user.id)
    else:
        if message.from_user.id in await DBuser.return_ban():
            await message.answer(f"Вы забанены!")
        else:
            markup = await create_markup('inline', [[['Купить', 'buy'], ['Продать', 'sell']],
                                                [['Обменять', 'trade']],
                                                [["О нас", "we"]],
                                                [["👤 Мой профиль", "profile"]]])
            photo = FSInputFile(f"photo\main.jpg", 'rb')
            name = await bot.get_me()
            await bot.send_photo(
                caption=f"""Привет, <b>{message.from_user.full_name}</b>. Добро пожаловать в бота по обмену криптовалют <b>{name.first_name}</b>.

🤖Это обмен в Telegram нового поколения. 
🔥Удобный интерфейс. 
👤Поддержка на связи 24/7. 
✅Только актуальные и выгодные курсы для наших клиентов.

⚡️БЫСТРЫЙ автоматический обмен.
⚡️Начните обмен с нами сейчас и ощутите преимущества простоты и удобства!
⚡️Покупайте криптовалюту быстро, анонимно и безопасно. 👇


Чтобы осуществить обмен, жмите кнопку “Купить” / “Продать” / “Обменять”. Выбирайте нужную криптовалюту и вводите сумму. Готово!""",
                reply_markup=markup, photo=photo, chat_id=message.from_user.id)


@rt.callback_query(F.data == 'back')
async def back(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await state.clear()
    markup = await create_markup('inline', [[['Купить', 'buy'], ['Продать', 'sell']],
                                            [['Обменять', 'trade']],
                                            [["О нас", "we"]],
                                            [["📚 FAQ", "url.com"]],
                                            [["👤 Мой профиль", "profile"]]])
    photo = FSInputFile(f"photo\main.jpg", 'rb')
    name = await bot.get_me()
    await bot.send_photo(
        caption=f"""Привет, <b>{call.from_user.full_name}</b>. Добро пожаловать в бота по обмену криптовалют <b>{name.first_name}</b>.

🤖Это обмен в Telegram нового поколения. 
🔥Удобный интерфейс. 
👤Поддержка на связи 24/7. 
✅Только актуальные и выгодные курсы для наших клиентов.

⚡️БЫСТРЫЙ автоматический обмен.
⚡️Начните обмен с нами сейчас и ощутите преимущества простоты и удобства!
⚡️Покупайте криптовалюту быстро, анонимно и безопасно. 👇


Чтобы осуществить обмен, жмите кнопку “Купить” / “Продать” / “Обменять”. Выбирайте нужную криптовалюту и вводите сумму. Готово!""",
        reply_markup=markup, photo=photo, chat_id=call.from_user.id)