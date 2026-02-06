from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from data.loader import rt, bot
from aiogram import F
from utils.db.api.user import DBuser
from utils.system.adminka import AdminIs


@rt.callback_query(F.data == 'paid_sell', AdminIs())
async def paid_sell(call: CallbackQuery):
    text = call.message.text.split(" ")
    await call.message.answer(f"Успешно")
    us = text[11].replace("\n\n⚙️", "")
    us = await DBuser.return_info_user_name(us)
    await bot.send_message(chat_id=us[1], text="Средства были вам выплачены")


@rt.callback_query(F.data == 'paid_buy', AdminIs())
async def paid_buy(call: CallbackQuery):
    text = call.message.text.split(" ")
    await call.message.answer(f"Успешно")
    us = text[11].replace("\n\n⚙️", "")
    us = await DBuser.return_info_user_name(us)
    name = text[16]
    name = name.replace("\n⚙️", "")
    sum = text[15]
    await DBuser.rek_sum_change(name, sum)
    await bot.send_message(chat_id=us[1], text="Средства были вам выплачены")


@rt.callback_query(F.data == 'no_paid', AdminIs())
async def no_paid(call: CallbackQuery):
    text = call.message.text.split(" ")
    await call.message.answer(f"Успешно")
    us = text[11].replace("\n\n⚙️", "")
    us = await DBuser.return_info_user_name(us)
    await bot.send_message(chat_id=us[1], text="Ваша заявка была отклонена")