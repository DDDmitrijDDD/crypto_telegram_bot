from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from data.loader import rt, bot
from aiogram import F
from handlers.admin.start import AdminState, command_start, edit_tech, read_tech, del_mes
from utils.system.inline_btns import create_markup
from utils.system.adminka import AdminIs
from utils.db.api.user import DBuser


@rt.message(Command('tech'), StateFilter(default_state))
@rt.message(F.text == 'Тех. работы', AdminIs(), StateFilter(default_state))
async def tech_message(message: Message, state: FSMContext):
    """при кнопке Тех.работы"""
    await del_mes(message.from_user.id, message.message_id)

    markup = await create_markup('inline', [[
        ["📛 OFF", 'off'] if (await read_tech()) == '1' else ["✅ ON", 'on']],
                                            [['❌ Отмена', 'cancel']]])
    await state.set_state(AdminState.tech_work)
    ms = await message.answer(f"Ты админ", reply_markup=markup)


@rt.message(AdminState.tech_work, AdminIs())
async def del_tech_work_message(message: Message):
    """удаляет сообщение"""
    await message.delete()


@rt.callback_query(AdminState.tech_work, AdminIs())
async def tech_process(call: CallbackQuery, state: FSMContext):
    """изменяет статус тех.работ"""
    if call.data == 'on':
        try:
            for i in await DBuser.return_all_id():
                await bot.send_message(chat_id=i[0], text='Бот на тех. работах!')
        except Exception:
            pass
        await edit_tech(True)
    elif call.data == 'off':
        try:
            for i in await DBuser.return_all_id():
                await bot.send_message(chat_id=i[0], text='Бот снова работает!')
        except Exception:
            pass
        await edit_tech(False)
    await command_start(call.message, state)
