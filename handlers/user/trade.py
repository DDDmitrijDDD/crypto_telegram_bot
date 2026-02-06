import asyncio
from datetime import datetime

import requests
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from okx import MarketData

from data.config import admins_id
from data.loader import rt, bot
from handlers.user.start import UserState
from utils.db.api.user import DBuser
from utils.system.inline_btns import create_markup


@rt.callback_query(F.data == 'trade')
async def trade(call: CallbackQuery, state: FSMContext):
    if call.from_user.id in await DBuser.return_ban():
        await call.message.answer(f"Вы забанены!")
    else:
        await state.clear()
        check = await DBuser.return_bid_sell(call.from_user.id)
        if not check:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            markup = await create_markup('inline', [[['SOL', 'sol'], ['BNB', 'bnb']],
                                                    [['BTC', 'btc'], ["LTC", "ltc"]],
                                                    [["USDT", "usdt_trade"], ["TON", "ton"]],
                                                    [["ETH", "eth"], ["TRON", "tron"]],
                                                    [["Отмена", "back"]]])
            await call.message.answer(f"<b>💵 Выберите из списка валюту, которую вы хотите обменять.</b>",
                                      reply_markup=markup)
            await state.set_state(UserState.trade)
        else:
            await call.message.answer(f"У вас уже есть активная заявка. Пожалуйста, завершите её перед созданием новой.")


@rt.callback_query(F.data == 'usdt_trade', UserState.trade)
async def usdt_trade(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    markup = await create_markup('inline', [[['TRC', 'trc'], ['ERC', 'erc']],
                                            [["Назад", "trade"]]])
    await call.message.answer(f"<b>💵 Выберите из списка cеть валюты, которую вы хотите обменять.</b>",
                              reply_markup=markup)
    await state.set_state(UserState.trade)


@rt.callback_query(UserState.trade)
async def trade2(call: CallbackQuery, state: FSMContext):
    markup = await create_markup('inline', [[['SOL', 'sol'], ['BNB', 'bnb']],
                                            [['BTC', 'btc'], ["LTC", "ltc"]],
                                            [["USDT", "usdt_trade"], ["TON", "ton"]],
                                            [["ETH", "eth"], ["TRON", "tron"]],
                                            [["Отмена", "back"]]])
    name = call.data
    await state.update_data(name=name)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer(f"""<b>💵  Криптовалюта на обмен: {name.upper()}</b>

Выберите направление, которое хотите обменять""", reply_markup=markup)
    await state.set_state(UserState.trade2)


@rt.callback_query(F.data == 'usdt_trade', UserState.trade2)
async def usdt_trade2(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    markup = await create_markup('inline', [[['TRC', 'trc'], ['ERC', 'erc']],
                                            [["Назад", "trade"]]])
    await call.message.answer(f"<b>💵 Выберите из списка cеть валюты, которую вы хотите обменять.</b>",
                              reply_markup=markup)
    await state.set_state(UserState.trade2)


@rt.callback_query(UserState.trade2)
async def sum(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    markup = await create_markup('inline', [[["Вернуться в главное меню", "back"]]])
    data = await state.get_data()
    name = data['name']
    name2 = call.data
    await state.update_data(name2=name2)
    if name == name2:
        await call.message.answer(f"""⛔️ Невозможно обменять <b>{name.upper()} -> {name2.upper()}</b>

Выберите другое направление""", reply_markup=markup)
        await state.clear()
    else:
        await call.message.answer(f"""Меняем <b>{name.upper()} -> {name2.upper()}</b>

Укажите сумму обмена в $.""")
    await state.set_state(UserState.trade_sum)


@rt.message(UserState.trade_sum)
async def wallet(message: Message, state: FSMContext):
    data = await state.get_data()
    flag = "1"
    marketDataAPI = MarketData.MarketAPI(flag=flag)
    result = marketDataAPI.get_tickers(instType="SPOT")
    dollar = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    dollar = float(dollar['Valute']['USD']["Value"])
    name = data['name']
    name2 = data['name2']
    sum = message.text
    if name == "btc" or name2 == "btc":
        for i in result['data']:
            if i["instId"] == "BTC-USDT":
                crypt = float(i["last"])
        summ = 1 / crypt * float(sum)
        min = crypt * 0.0005
        if summ < 0.0005:
            await message.answer(f"Минимальная сумма для создания заявки BTC <b>{round(min, 2)}$.</b>")
            await state.set_state(UserState.trade_sum)
        else:
            await state.update_data(sum=int(message.text))
            await message.answer(f"Введите адрес кошелька для получения:")
            await state.set_state(UserState.trade_card)
    else:
        if sum.isdigit():
            if int(sum) < 30:
                await message.answer(f"Минимальная сумма для создания заявки на обмен 30$.")
                await state.set_state(UserState.trade_sum)
            elif int(sum) > 11500:
                await message.answer(f"Максимальная сумма для создания заявки на обмен 11500$.")
                await state.set_state(UserState.trade_sum)
            else:
                await state.update_data(sum=int(message.text))
                await message.answer(f"Введите адрес кошелька для получения:")
                await state.set_state(UserState.trade_card)
        else:
            await message.answer("Введите числовое значение. Например: 500")
            await state.set_state(UserState.trade_sum)


@rt.message(UserState.trade_card)
async def transaction(message: Message, state: FSMContext):
    url = await DBuser.url_return()
    markup = await create_markup('inline',
                                 [[['💴 Оплата переведена', 'translated'],
                                   [f'⛔️ Отменить заявку', 'canceled']],
                                  [['👤 Поддержка', f'{url}']]])
    data = await state.get_data()
    flag = "1"
    marketDataAPI = MarketData.MarketAPI(flag=flag)
    result = marketDataAPI.get_tickers(instType="SPOT")
    name = data['name']
    name2 = data["name2"]
    sum = data['sum']
    check1 = name
    check2 = name2
    if check1 == "erc":
        check1 = "USDC"
    if check1 == "trc":
        check1 = "USDC"
    if check1 == "tron":
        check1 = "TRX"
    if check2 == "erc":
        check2 = "USDC"
    if check2 == "trc":
        check2 = "USDC"
    if check2 == "tron":
        check2 = "TRX"
    card = message.text
    check = card.lower()
    if name2 == "sol":
        if len(check) < 32:
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети SOL.</b>

Введите действительный адрес""")
            await state.set_state(UserState.trade_card)
        else:
            for i in result['data']:
                if i["instId"] == f"{check1.upper()}-USDT":
                    crypt1 = float(i["last"])
                if i["instId"] == f"{check2.upper()}-USDT":
                    crypt2 = float(i["last"])
            summ = (1 / crypt2 * float(sum)) * 0.95
            plat = 1 / crypt1 * float(sum)
            text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
            await message.answer(f"{text}")
            a = 0
            for i in range(0, 9):
                if a == 3:
                    a = 0
                    text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
                text += "."
                a += 1
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"{text}")
                await asyncio.sleep(0.5)
            money = await DBuser.return_crypt(name)
            if float(money[0][1]) < float(summ):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_crypt(name)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Обмен")
                await DBuser.app(message.from_user.id)
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Обмен

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Обмен

Пользователь @{message.from_user.username}

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>""", reply_markup=markup)
                mes = await DBuser.return_bid_sell_message(sum, name, card)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await asyncio.sleep(30 * 60)
                try:
                    us = await DBuser.return_bid_sell_user(sum, name, card)
                    markup = await create_markup('inline',
                                                 [[["Вернуться в главное меню", "back"]]])
                    await bot.delete_message(chat_id=message.from_user.id, message_id=mes)
                    await message.answer(f"⛔️ Время действия заявки #<code>{ids}</code> истекло.", reply_markup=markup)
                    await DBuser.delete_bid_sell(ids)
                except:
                    pass
    elif name2 == "btc":
        if card[0] != "1" and card[0] != "3" and check[0:3] != "bc1":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети BTC.</b>

Введите действительный адрес""")
            await state.set_state(UserState.trade_card)
        else:
            for i in result['data']:
                if i["instId"] == f"{check1.upper()}-USDT":
                    crypt1 = float(i["last"])
                if i["instId"] == f"{check2.upper()}-USDT":
                    crypt2 = float(i["last"])
            summ = (1 / crypt2 * float(sum)) * 0.95
            plat = 1 / crypt1 * float(sum)
            text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
            await message.answer(f"{text}")
            a = 0
            for i in range(0, 9):
                if a == 3:
                    a = 0
                    text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
                text += "."
                a += 1
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"{text}")
                await asyncio.sleep(0.5)
            money = await DBuser.return_crypt(name)
            if float(money[0][1]) < float(summ):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_crypt(name)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Обмен")
                await DBuser.app(message.from_user.id)
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Обмен

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Обмен

Пользователь @{message.from_user.username}

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>""", reply_markup=markup)
                mes = await DBuser.return_bid_sell_message(sum, name, card)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await asyncio.sleep(30 * 60)
                try:
                    us = await DBuser.return_bid_sell_user(sum, name, card)
                    markup = await create_markup('inline',
                                                 [[["Вернуться в главное меню", "back"]]])
                    await bot.delete_message(chat_id=message.from_user.id, message_id=mes)
                    await message.answer(f"⛔️ Время действия заявки #<code>{ids}</code> истекло.", reply_markup=markup)
                    await DBuser.delete_bid_sell(ids)
                except:
                    pass
    elif name2 == "bnb":
        if check[0:2] != "0x":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети BNB.</b>

Введите действительный адрес""")
            await state.set_state(UserState.trade_card)
        else:
            for i in result['data']:
                if i["instId"] == f"{check1.upper()}-USDT":
                    crypt1 = float(i["last"])
                if i["instId"] == f"{check2.upper()}-USDT":
                    crypt2 = float(i["last"])
            summ = (1 / crypt2 * float(sum)) * 0.95
            plat = 1 / crypt1 * float(sum)
            text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
            await message.answer(f"{text}")
            a = 0
            for i in range(0, 9):
                if a == 3:
                    a = 0
                    text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
                text += "."
                a += 1
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"{text}")
                await asyncio.sleep(0.5)
            money = await DBuser.return_crypt(name)
            if float(money[0][1]) < float(summ):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_crypt(name)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Обмен")
                await DBuser.app(message.from_user.id)
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Обмен

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Обмен

Пользователь @{message.from_user.username}

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>""", reply_markup=markup)
                mes = await DBuser.return_bid_sell_message(sum, name, card)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await asyncio.sleep(30 * 60)
                try:
                    us = await DBuser.return_bid_sell_user(sum, name, card)
                    markup = await create_markup('inline',
                                                 [[["Вернуться в главное меню", "back"]]])
                    await bot.delete_message(chat_id=message.from_user.id, message_id=mes)
                    await message.answer(f"⛔️ Время действия заявки #<code>{ids}</code> истекло.", reply_markup=markup)
                    await DBuser.delete_bid_sell(ids)
                except:
                    pass
    elif name2 == "ltc":
        if check[0] != "m" and check[0] != "l":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети LTC.</b>

Введите действительный адрес""")
            await state.set_state(UserState.trade_card)
        else:
            for i in result['data']:
                if i["instId"] == f"{check1.upper()}-USDT":
                    crypt1 = float(i["last"])
                if i["instId"] == f"{check2.upper()}-USDT":
                    crypt2 = float(i["last"])
            summ = (1 / crypt2 * float(sum)) * 0.95
            plat = 1 / crypt1 * float(sum)
            text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
            await message.answer(f"{text}")
            a = 0
            for i in range(0, 9):
                if a == 3:
                    a = 0
                    text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
                text += "."
                a += 1
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"{text}")
                await asyncio.sleep(0.5)
            money = await DBuser.return_crypt(name)
            if float(money[0][1]) < float(summ):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_crypt(name)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Обмен")
                await DBuser.app(message.from_user.id)
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Обмен

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Обмен

Пользователь @{message.from_user.username}

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>""", reply_markup=markup)
                mes = await DBuser.return_bid_sell_message(sum, name, card)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await asyncio.sleep(30 * 60)
                try:
                    us = await DBuser.return_bid_sell_user(sum, name, card)
                    markup = await create_markup('inline',
                                                 [[["Вернуться в главное меню", "back"]]])
                    await bot.delete_message(chat_id=message.from_user.id, message_id=mes)
                    await message.answer(f"⛔️ Время действия заявки #<code>{ids}</code> истекло.", reply_markup=markup)
                    await DBuser.delete_bid_sell(ids)
                except:
                    pass
    elif name2 == "ton":
        if card[0] != "E" and card[0] != "U":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети TON.</b>

Введите действительный адрес""")
            await state.set_state(UserState.trade_card)
        else:
            for i in result['data']:
                if i["instId"] == f"{check1.upper()}-USDT":
                    crypt1 = float(i["last"])
                if i["instId"] == f"{check2.upper()}-USDT":
                    crypt2 = float(i["last"])
            summ = (1 / crypt2 * float(sum)) * 0.95
            plat = 1 / crypt1 * float(sum)
            text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
            await message.answer(f"{text}")
            a = 0
            for i in range(0, 9):
                if a == 3:
                    a = 0
                    text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
                text += "."
                a += 1
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"{text}")
                await asyncio.sleep(0.5)
            money = await DBuser.return_crypt(name)
            if float(money[0][1]) < float(summ):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_crypt(name)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Обмен")
                await DBuser.app(message.from_user.id)
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Обмен

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Обмен

Пользователь @{message.from_user.username}

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>""", reply_markup=markup)
                mes = await DBuser.return_bid_sell_message(sum, name, card)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await asyncio.sleep(30 * 60)
                try:
                    us = await DBuser.return_bid_sell_user(sum, name, card)
                    markup = await create_markup('inline',
                                                 [[["Вернуться в главное меню", "back"]]])
                    await bot.delete_message(chat_id=message.from_user.id, message_id=mes)
                    await message.answer(f"⛔️ Время действия заявки #<code>{ids}</code> истекло.", reply_markup=markup)
                    await DBuser.delete_bid_sell(ids)
                except:
                    pass
    elif name2 == "eth":
        if check[0:2] != "0x":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети ETH.</b>

Введите действительный адрес""")
            await state.set_state(UserState.trade_card)
        else:
            for i in result['data']:
                if i["instId"] == f"{check1.upper()}-USDT":
                    crypt1 = float(i["last"])
                if i["instId"] == f"{check2.upper()}-USDT":
                    crypt2 = float(i["last"])
            summ = (1 / crypt2 * float(sum)) * 0.95
            plat = 1 / crypt1 * float(sum)
            text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
            await message.answer(f"{text}")
            a = 0
            for i in range(0, 9):
                if a == 3:
                    a = 0
                    text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
                text += "."
                a += 1
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"{text}")
                await asyncio.sleep(0.5)
            money = await DBuser.return_crypt(name)
            if float(money[0][1]) < float(summ):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_crypt(name)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Обмен")
                await DBuser.app(message.from_user.id)
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Обмен

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Обмен

Пользователь @{message.from_user.username}

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>""", reply_markup=markup)
                mes = await DBuser.return_bid_sell_message(sum, name, card)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await asyncio.sleep(30 * 60)
                try:
                    us = await DBuser.return_bid_sell_user(sum, name, card)
                    markup = await create_markup('inline',
                                                 [[["Вернуться в главное меню", "back"]]])
                    await bot.delete_message(chat_id=message.from_user.id, message_id=mes)
                    await message.answer(f"⛔️ Время действия заявки #<code>{ids}</code> истекло.", reply_markup=markup)
                    await DBuser.delete_bid_sell(ids)
                except:
                    pass
    elif name2 == "tron":
        if card[0] != "T":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети TRON.</b>

Введите действительный адрес""")
            await state.set_state(UserState.trade_card)
        else:
            for i in result['data']:
                if i["instId"] == f"{check1.upper()}-USDT":
                    crypt1 = float(i["last"])
                if i["instId"] == f"{check2.upper()}-USDT":
                    crypt2 = float(i["last"])
            summ = (1 / crypt2 * float(sum)) * 0.95
            plat = 1 / crypt1 * float(sum)
            text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
            await message.answer(f"{text}")
            a = 0
            for i in range(0, 9):
                if a == 3:
                    a = 0
                    text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
                text += "."
                a += 1
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"{text}")
                await asyncio.sleep(0.5)
            money = await DBuser.return_crypt(name)
            if float(money[0][1]) < float(summ):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_crypt(name)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Обмен")
                await DBuser.app(message.from_user.id)
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Обмен

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Обмен

Пользователь @{message.from_user.username}

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>""", reply_markup=markup)
                mes = await DBuser.return_bid_sell_message(sum, name, card)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await asyncio.sleep(30 * 60)
                try:
                    us = await DBuser.return_bid_sell_user(sum, name, card)
                    markup = await create_markup('inline',
                                                 [[["Вернуться в главное меню", "back"]]])
                    await bot.delete_message(chat_id=message.from_user.id, message_id=mes)
                    await message.answer(f"⛔️ Время действия заявки #<code>{ids}</code> истекло.", reply_markup=markup)
                    await DBuser.delete_bid_sell(ids)
                except:
                    pass
    elif name2 == "trc":
        if check[0:2] != "0x" and card[0] != "T":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети TRC20.</b>

Введите действительный адрес""")
            await state.set_state(UserState.trade_card)
        else:
            for i in result['data']:
                if i["instId"] == f"{check1.upper()}-USDT":
                    crypt1 = float(i["last"])
                if i["instId"] == f"{check2.upper()}-USDT":
                    crypt2 = float(i["last"])
            summ = (1 / crypt2 * float(sum)) * 0.95
            plat = 1 / crypt1 * float(sum)
            text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
            await message.answer(f"{text}")
            a = 0
            for i in range(0, 9):
                if a == 3:
                    a = 0
                    text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
                text += "."
                a += 1
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"{text}")
                await asyncio.sleep(0.5)
            money = await DBuser.return_crypt(name)
            if float(money[0][1]) < float(summ):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_crypt(name)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Обмен")
                await DBuser.app(message.from_user.id)
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Обмен

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Обмен

Пользователь @{message.from_user.username}

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>""", reply_markup=markup)
                mes = await DBuser.return_bid_sell_message(sum, name, card)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await asyncio.sleep(30 * 60)
                try:
                    us = await DBuser.return_bid_sell_user(sum, name, card)
                    markup = await create_markup('inline',
                                                 [[["Вернуться в главное меню", "back"]]])
                    await bot.delete_message(chat_id=message.from_user.id, message_id=mes)
                    await message.answer(f"⛔️ Время действия заявки #<code>{ids}</code> истекло.", reply_markup=markup)
                    await DBuser.delete_bid_sell(ids)
                except:
                    pass
    elif name2 == "erc":
        if check[0:2] != "0x":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети ERC20.</b>

Введите действительный адрес""")
            await state.set_state(UserState.trade_card)
        else:
            for i in result['data']:
                if i["instId"] == f"{check1.upper()}-USDT":
                    crypt1 = float(i["last"])
                if i["instId"] == f"{check2.upper()}-USDT":
                    crypt2 = float(i["last"])
            summ = (1 / crypt2 * float(sum)) * 0.95
            plat = 1 / crypt1 * float(sum)
            text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
            await message.answer(f"{text}")
            a = 0
            for i in range(0, 9):
                if a == 3:
                    a = 0
                    text = """Идёт создание заявки. Ожидайте.

Создание заявки"""
                text += "."
                a += 1
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"{text}")
                await asyncio.sleep(0.5)
            money = await DBuser.return_crypt(name)
            if float(money[0][1]) < float(summ):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_crypt(name)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Обмен")
                await DBuser.app(message.from_user.id)
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Обмен

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Обмен

Пользователь @{message.from_user.username}

⚙️ К получению — {summ} {name2.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: Криптовалюта · {name.upper()}
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{plat} {name.upper()}</pre></b>""", reply_markup=markup)
                mes = await DBuser.return_bid_sell_message(sum, name, card)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await asyncio.sleep(30 * 60)
                try:
                    us = await DBuser.return_bid_sell_user(sum, name, card)
                    markup = await create_markup('inline',
                                                 [[["Вернуться в главное меню", "back"]]])
                    await bot.delete_message(chat_id=message.from_user.id, message_id=mes)
                    await message.answer(f"⛔️ Время действия заявки #<code>{ids}</code> истекло.", reply_markup=markup)
                    await DBuser.delete_bid_sell(ids)
                except:
                    pass
