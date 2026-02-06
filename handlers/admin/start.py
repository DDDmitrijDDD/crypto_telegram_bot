import configparser
from aiogram import F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.types import Message, CallbackQuery
from data.loader import rt, bot
from utils.system.inline_btns import create_markup
from utils.system.adminka import AdminIs


class AdminState(StatesGroup):
    url = State()
    bal_rek = State()
    rek = State()
    rek_change = State()
    add_rek = State()
    add_rek2 = State()
    tech_work = State()
    all_user = State()
    all_mail = State()
    send_mail = State()
    finish_mail = State()
    one_mail = State()
    card = State()
    change_card = State()
    ban = State()
    cards = State()
    dels = State()


async def del_mes(chat: int, id_: int) -> None:
    """
    удаляет сообщение
    :param chat: id чата
    :param id_: id сообщения
    """
    try: await bot.delete_message(chat, id_)
    except Exception: ...


async def read_tech():
    """
    возвращает статус тех.работ
    :return: статус тех.работ
    """
    config = configparser.ConfigParser()
    config.sections()
    config.read('data/tech.ini')
    config.sections()
    return config['TECH']['Work']


async def edit_tech(b00l: bool) -> None:
    """
    изменяет статус тех.работ
    :param b00l: статус
    """
    config = configparser.ConfigParser()
    config['TECH'] = {'work': '1' if b00l else '0'}
    with open('data/tech.ini', 'w') as configfile:
        config.write(configfile)


@rt.message(CommandStart(), AdminIs(), StateFilter(default_state))
async def command_start(message: Message, state: FSMContext):
    """старт бота"""
    await state.clear()
    markup = await create_markup('reply', [
                                           [['Все пользователи'], ['Рассылка']],
                                           [["Тех. работы"], ['Реквизиты']],
                                           [["Поддержка"]]])
    await message.answer(f"Ты админ", reply_markup=markup)


@rt.callback_query(AdminIs(), F.data == 'cancel')
async def cancel_callback(call: CallbackQuery, state: FSMContext):
    """инлайн-кнопка с "cancel" """
    await state.clear()
    await command_start(call.message, state)

