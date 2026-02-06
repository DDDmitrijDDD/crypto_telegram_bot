from aiogram import F
from aiogram.types import CallbackQuery, FSInputFile
from data.loader import rt, bot
from utils.system.inline_btns import create_markup
from utils.db.api.user import DBuser


@rt.callback_query(F.data == 'profile')
async def profile(call: CallbackQuery):
    if call.from_user.id in await DBuser.return_ban():
        await call.message.answer(f"Вы забанены!")
    else:
        user = await DBuser.return_user(call.from_user.id)
        if user[0][3] == 0:
            status = "Новичок"
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        markup = await create_markup('inline', [[['📖 История обменов', 'story']],
                                                [["Назад", "back"]]])
        photo = FSInputFile(f"photo\profile.jpg", 'rb')
        await bot.send_photo(chat_id=call.from_user.id, photo=photo, caption=f"""Это ваш личный кабинет

<b>Количество заявок:</b> {user[0][2]}

<b>Статус</b>: {status}""", reply_markup=markup)


@rt.callback_query(F.data == 'story')
async def story(call: CallbackQuery):
    story = await DBuser.return_story(call.from_user.id)
    if not story:
        await call.message.answer(f"У вас нет заявок.")
    else:
        text = f""
        for i in story:
            text += f"Заявка № <b>{i[0]}</b> -> {i[2]} -> {i[3]}\n"
        await call.message.answer(f"""🔎 Мои заявки:
        
{text}""")