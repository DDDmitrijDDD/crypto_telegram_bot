from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from data.loader import rt
from aiogram import F
from handlers.admin.start import AdminState, del_mes
from utils.db.api.user import DBuser
from utils.system.inline_btns import create_markup
from utils.system.adminka import AdminIs


@rt.message(F.text == 'Поддержка', AdminIs(), StateFilter(default_state))
async def url_change(message: Message, state: FSMContext):
    markup = await create_markup('inline', [[['Отмена', 'cancel']]])
    await message.answer(f"Введите ссылку", reply_markup=markup)
    await state.set_state(AdminState.url)


@rt.message(AdminState.url, AdminIs())
async def url_state(message: Message, state: FSMContext):
    await DBuser.url(message.text)
    await message.answer(f"Успешно")
    await state.clear()