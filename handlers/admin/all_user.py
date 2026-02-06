from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from data.loader import rt
from aiogram import F
from handlers.admin.start import AdminState, command_start
from utils.db.api.user import DBuser
from utils.system.inline_btns import create_markup
from utils.system.adminka import AdminIs


@rt.message(Command('all_user'), StateFilter(default_state))
@rt.message(F.text == 'Все пользователи', AdminIs(), StateFilter(default_state))
async def all_users(message: Message, state: FSMContext):
    markup = await create_markup('inline', [*[[_] for _ in await DBuser.return_all_name()], [["❌Отмена", "cancel"]]])
    await message.answer(f"Пользователи:", reply_markup=markup)
    await state.set_state(AdminState.all_user)


@rt.callback_query(AdminState.all_user, AdminIs())
async def all_user_state(call: CallbackQuery, state: FSMContext):
        await state.update_data(us=f'{call.data}')
        markup = await create_markup("inline",
                                       [[["Написать", "one2"], ["Забанить", "bans"]],
                                        [["Отмена", "cancel"]]])
        info = await DBuser.return_info_user_name(call.data)
        await state.update_data(ids=f'{info[1]}')
        if info[3] == 0:
            status = "Новичок"
        await call.message.answer(f"""Информация пользователя {info[5]}

id: {info[1]}
количество заявок: {info[2]}
статус: {status}
баланс: {info[4]}
""",
                         reply_markup=markup)
        await state.set_state(AdminState.ban)


@rt.callback_query(AdminIs(), F.data == 'bans', AdminState.ban)
async def bans(call: CallbackQuery):
    keyboard = await create_markup("inline", [[["Да", "ban_yes"], ["Отмена", "cancel"]]])
    await call.message.answer(f"Вы уверены?", reply_markup=keyboard)


@rt.callback_query(AdminIs(), F.data == 'ban_yes')
async def ban_yes(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await DBuser.ban(data['ids'])
    await call.message.answer(f"Пользователь забанен")
    await command_start(call.message, state)