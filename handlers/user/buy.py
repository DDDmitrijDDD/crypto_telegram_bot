import asyncio
import random
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


@rt.callback_query(F.data == 'buy')
async def buy(call: CallbackQuery, state: FSMContext):
    if call.from_user.id in await DBuser.return_ban():
        await call.message.answer(f"Вы забанены!")
    else:
        await state.clear()
        check = await DBuser.return_bid_sell(call.from_user.id)
        if not check:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            markup = await create_markup('inline', [[['SOL', 'sol'], ['BNB', 'bnb']],
                                                    [['BTC', 'btc'], ["LTC", "ltc"]],
                                                    [["USDT", "usdt_buy"], ["TON", "ton"]],
                                                    [["ETH", "eth"], ["TRON", "tron"]],
                                                    [["Отмена", "back"]]])
            await call.message.answer(f"<b>💵 Выберите из списка валюту, которую вы хотите купить.</b>", reply_markup=markup)
            await state.set_state(UserState.buy)
        else:
            await call.message.answer(f"У вас уже есть активная заявка. Пожалуйста, завершите её перед созданием новой.")


@rt.callback_query(F.data == 'usdt_buy', UserState.buy)
async def usdt_buy(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    markup = await create_markup('inline', [[['TRC20', 'trc'], ['ERC20', 'erc']],
                                            [["Назад", "buy"]]])
    await call.message.answer(f"<b>💵 Выберите из списка cеть валюты, которую вы хотите купить.</b>", reply_markup=markup)
    await state.set_state(UserState.buy)


@rt.callback_query(UserState.buy)
async def buy_state(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    name = call.data
    await state.update_data(name=name)
    await state.update_data(well="rub")
    markup = await create_markup('inline', [[['💸 Ввести сумму в рублях', 'rub_buy'], [f'🔗 Ввести сумму в {name.upper()}', 'crypt_buy']],
                                            [['Назад', 'buy']]])
    await call.message.answer(f"""<b>Криптовалюта на покупку: {name.upper()}

Выбранная валюта: Рубли </b>

Введите сумму в рублях, которую хотите купить или выберите, как ввести сумму:""", reply_markup=markup)
    await state.set_state(UserState.buy_sum)


@rt.callback_query(F.data == 'rub_buy', UserState.buy_sum)
async def rub_buy(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    data = await state.get_data()
    await state.update_data(well="rub")
    markup = await create_markup('inline', [[['💸 Ввести сумму в рублях', 'rub_buy'], [f'🔗 Ввести сумму в {data["name"].upper()}', 'crypt_buy']],
                                            [['Назад', 'buy']]])
    await call.message.answer(f"""<b>Криптовалюта на покупку: {data["name"].upper()}

Выбранная валюта: Рубли </b>

Введите сумму в рублях, которую хотите купить или выберите, как ввести сумму:""", reply_markup=markup)
    await state.set_state(UserState.buy_sum)


@rt.callback_query(F.data == 'crypt_buy', UserState.buy_sum)
async def crypt_buy(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    data = await state.get_data()
    await state.update_data(well=f"{data['name']}")
    markup = await create_markup('inline',
                                 [[['💸 Ввести сумму в рублях', 'rub_buy'], [f'🔗 Ввести сумму в {data["name"].upper()}', 'crypt_buy']],
                                  [['Назад', 'buy']]])
    await call.message.answer(f"""<b>Криптовалюта на покупку: {data["name"].upper()}

Выбранная валюта: Криптовалюта </b>

Введите сумму в выбранной криптовалюте, которую хотите купить или выберите, как ввести сумму:""", reply_markup=markup)
    await state.set_state(UserState.buy_sum)


@rt.message(UserState.buy_sum)
async def buy_sum_state(message: Message, state: FSMContext):
    data = await state.get_data()
    flag = "1"
    marketDataAPI = MarketData.MarketAPI(flag=flag)
    result = marketDataAPI.get_tickers(instType="SPOT")
    dollar = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    dollar = float(dollar['Valute']['USD']["Value"])
    sum = message.text
    name = data['name']
    well = data['well']
    if sum.isdigit() or float(sum):
        if well == "rub":
            if name == "btc":
                for i in result['data']:
                    if i["instId"] == "BTC-USDT":
                        crypt = float(i["last"])
                dol = 1 / dollar * float(sum)
                summ = 1 / crypt * dol
                min = crypt * 0.0005 * dollar
                if summ < 0.0005:
                    await message.answer(f"Минимальная сумма для создания заявки BTC на покупку <b>{round(min, 2)} руб.</b>")
                    await state.set_state(UserState.buy_sum)
                else:
                    for i in result['data']:
                        if i["instId"] == "BTC-USDT":
                            crypt = float(i["last"])
                    dol = 1 / dollar * float(sum)
                    summ = 1 / crypt * dol
                    plat = float(sum) + (float(sum) * 0.05)
                    await state.update_data(payment=summ)
                    await state.update_data(sum=plat)
                    await message.answer(f"Введите адрес кошелька для получения:")
                    await state.set_state(UserState.buy_card)
            else:
                if int(sum) < 2300:
                    await message.answer(f"Минимальная сумма для создания заявки на покупку <b>2300р.</b>")
                    await state.set_state(UserState.buy_sum)
                else:
                    if int(sum) > 1000000:
                        await message.answer(f"Максимальная сумма для создания заявки на покупку <b>1,000,000р.</b>")
                        await state.set_state(UserState.buy_sum)
                    else:
                        if name == "sol":
                            for i in result['data']:
                                if i["instId"] == "SOL-USDT":
                                    crypt = float(i["last"])
                            dol = 1 / dollar * float(sum)
                            summ = 1 / crypt * dol
                            plat = float(sum) + (float(sum) * 0.05)
                            await state.update_data(payment=summ)
                            await state.update_data(sum=plat)
                            await message.answer(f"Введите адрес кошелька для получения:")
                            await state.set_state(UserState.buy_card)
                        elif name == "bnb":
                            for i in result['data']:
                                if i["instId"] == "BNB-USDT":
                                    crypt = float(i["last"])
                            dol = 1 / dollar * float(sum)
                            summ = 1 / crypt * dol
                            plat = float(sum) + (float(sum) * 0.05)
                            await state.update_data(payment=summ)
                            await state.update_data(sum=plat)
                            await message.answer(f"Введите адрес кошелька для получения:")
                            await state.set_state(UserState.buy_card)
                        elif name == "ltc":
                            for i in result['data']:
                                if i["instId"] == "LTC-USDT":
                                    crypt = float(i["last"])
                            dol = 1 / dollar * float(sum)
                            summ = 1 / crypt * dol
                            plat = float(sum) + (float(sum) * 0.05)
                            await state.update_data(payment=summ)
                            await state.update_data(sum=plat)
                            await message.answer(f"Введите адрес кошелька для получения:")
                            await state.set_state(UserState.buy_card)
                        elif name == "trc":
                            for i in result['data']:
                                if i["instId"] == "USDC-USDT":
                                    crypt = float(i["last"])
                            dol = 1 / dollar * float(sum)
                            summ = 1 / crypt * dol
                            plat = float(sum) + (float(sum) * 0.05)
                            await state.update_data(payment=summ)
                            await state.update_data(sum=plat)
                            await message.answer(f"Введите адрес кошелька для получения:")
                            await state.set_state(UserState.buy_card)
                        elif name == "erc":
                            for i in result['data']:
                                if i["instId"] == "USDC-USDT":
                                    crypt = float(i["last"])
                            dol = 1 / dollar * float(sum)
                            summ = 1 / crypt * dol
                            plat = float(sum) + (float(sum) * 0.05)
                            await state.update_data(payment=summ)
                            await state.update_data(sum=plat)
                            await message.answer(f"Введите адрес кошелька для получения:")
                            await state.set_state(UserState.buy_card)
                        elif name == "ton":
                            for i in result['data']:
                                if i["instId"] == "TON-USDT":
                                    crypt = float(i["last"])
                            dol = 1 / dollar * float(sum)
                            summ = 1 / crypt * dol
                            plat = float(sum) + (float(sum) * 0.05)
                            await state.update_data(payment=summ)
                            await state.update_data(sum=plat)
                            await message.answer(f"Введите адрес кошелька для получения:")
                            await state.set_state(UserState.buy_card)
                        elif name == "eth":
                            for i in result['data']:
                                if i["instId"] == "ETH-USDT":
                                    crypt = float(i["last"])
                            dol = 1 / dollar * float(sum)
                            summ = 1 / crypt * dol
                            plat = float(sum) + (float(sum) * 0.05)
                            await state.update_data(payment=summ)
                            await state.update_data(sum=plat)
                            await message.answer(f"Введите адрес кошелька для получения:")
                            await state.set_state(UserState.buy_card)
                        elif name == "tron":
                            for i in result['data']:
                                if i["instId"] == "TRX-USDT":
                                    crypt = float(i["last"])
                            dol = 1 / dollar * float(sum)
                            summ = 1 / crypt * dol
                            plat = float(sum) + (float(sum) * 0.05)
                            await state.update_data(payment=summ)
                            await state.update_data(sum=plat)
                            await message.answer(f"Введите адрес кошелька для получения:")
                            await state.set_state(UserState.buy_card)
        else:
            if name == "sol":
                for i in result['data']:
                    if i["instId"] == "SOL-USDT":
                        crypt = float(i["last"])
                dol = 1 / dollar * 2300
                summ = 1 / crypt * dol
                dol_max = 1 / dollar * 1000000
                summ_max = 1 / crypt * dol_max
                if float(sum) < float(summ):
                    await message.answer(f"Минимальная сумма для создания заявки составляет {summ} {name.upper()}.")
                    await state.set_state(UserState.buy_sum)
                elif float(sum) > float(summ_max):
                    await message.answer(f"Максимальная сумма для создания заявки составляет {summ_max} {name.upper()}.")
                else:
                    rub = (float(sum) * crypt) * dollar
                    rub = rub + (rub * 0.05)
                    await state.update_data(sum=rub)
                    await state.update_data(payment=sum)
                    await message.answer(f"Введите адрес кошелька для получения:")
                    await state.set_state(UserState.buy_card)
            elif name == "bnb":
                for i in result['data']:
                    if i["instId"] == "BNB-USDT":
                        crypt = float(i["last"])
                dol = 1 / dollar * 2300
                summ = 1 / crypt * dol
                dol_max = 1 / dollar * 1000000
                summ_max = 1 / crypt * dol_max
                if float(sum) < float(summ):
                    await message.answer(f"Минимальная сумма для создания заявки составляет {summ} {name.upper()}.")
                    await state.set_state(UserState.buy_sum)
                elif float(sum) > float(summ_max):
                    await message.answer(
                        f"Максимальная сумма для создания заявки составляет {summ_max} {name.upper()}.")
                else:
                    rub = (float(sum) * crypt) * dollar
                    rub = rub + (rub * 0.05)
                    await state.update_data(sum=rub)
                    await state.update_data(payment=sum)
                    await message.answer(f"Введите адрес кошелька для получения:")
                    await state.set_state(UserState.buy_card)
            elif name == "btc":
                for i in result['data']:
                    if i["instId"] == "BTC-USDT":
                        crypt = float(i["last"])
                dol_max = 1 / dollar * 1000000
                summ_max = 1 / crypt * dol_max
                if float(sum) < 0.0005:
                    await message.answer(f"Минимальная сумма для создания заявки составляет 0.0005 {name.upper()}.")
                    await state.set_state(UserState.buy_sum)
                elif float(sum) > float(summ_max):
                    await message.answer(
                        f"Максимальная сумма для создания заявки составляет {summ_max} {name.upper()}.")
                else:
                    rub = (float(sum) * crypt) * dollar
                    rub = rub + (rub * 0.05)
                    await state.update_data(sum=rub)
                    await state.update_data(payment=sum)
                    await message.answer(f"Введите адрес кошелька для получения:")
                    await state.set_state(UserState.buy_card)
            elif name == "ltc":
                for i in result['data']:
                    if i["instId"] == "LTC-USDT":
                        crypt = float(i["last"])
                dol = 1 / dollar * 2300
                summ = 1 / crypt * dol
                dol_max = 1 / dollar * 1000000
                summ_max = 1 / crypt * dol_max
                if float(sum) < float(summ):
                    await message.answer(f"Минимальная сумма для создания заявки составляет {summ} {name.upper()}.")
                    await state.set_state(UserState.buy_sum)
                elif float(sum) > float(summ_max):
                    await message.answer(
                        f"Максимальная сумма для создания заявки составляет {summ_max} {name.upper()}.")
                else:
                    rub = (float(sum) * crypt) * dollar
                    rub = rub + (rub * 0.05)
                    await state.update_data(sum=rub)
                    await state.update_data(payment=sum)
                    await message.answer(f"Введите адрес кошелька для получения:")
                    await state.set_state(UserState.buy_card)
            elif name == "trc":
                for i in result['data']:
                    if i["instId"] == "USDC-USDT":
                        crypt = float(i["last"])
                dol = 1 / dollar * 2300
                summ = 1 / crypt * dol
                dol_max = 1 / dollar * 1000000
                summ_max = 1 / crypt * dol_max
                if float(sum) < float(summ):
                    await message.answer(f"Минимальная сумма для создания заявки составляет {summ} {name.upper()}.")
                    await state.set_state(UserState.buy_sum)
                elif float(sum) > float(summ_max):
                    await message.answer(
                        f"Максимальная сумма для создания заявки составляет {summ_max} {name.upper()}.")
                else:
                    rub = (float(sum) * crypt) * dollar
                    rub = rub + (rub * 0.05)
                    await state.update_data(sum=rub)
                    await state.update_data(payment=sum)
                    await message.answer(f"Введите адрес кошелька для получения:")
                    await state.set_state(UserState.buy_card)
            elif name == "erc":
                for i in result['data']:
                    if i["instId"] == "USDC-USDT":
                        crypt = float(i["last"])
                dol = 1 / dollar * 2300
                summ = 1 / crypt * dol
                dol_max = 1 / dollar * 1000000
                summ_max = 1 / crypt * dol_max
                if float(sum) < float(summ):
                    await message.answer(f"Минимальная сумма для создания заявки составляет {summ} {name.upper()}.")
                    await state.set_state(UserState.buy_sum)
                elif float(sum) > float(summ_max):
                    await message.answer(
                        f"Максимальная сумма для создания заявки составляет {summ_max} {name.upper()}.")
                else:
                    rub = (float(sum) * crypt) * dollar
                    rub = rub + (rub * 0.05)
                    await state.update_data(sum=rub)
                    await state.update_data(payment=sum)
                    await message.answer(f"Введите адрес кошелька для получения:")
                    await state.set_state(UserState.buy_card)
            elif name == "ton":
                for i in result['data']:
                    if i["instId"] == "TON-USDT":
                        crypt = float(i["last"])
                dol = 1 / dollar * 2300
                summ = 1 / crypt * dol
                dol_max = 1 / dollar * 1000000
                summ_max = 1 / crypt * dol_max
                if float(sum) < float(summ):
                    await message.answer(f"Минимальная сумма для создания заявки составляет {summ} {name.upper()}.")
                    await state.set_state(UserState.buy_sum)
                elif float(sum) > float(summ_max):
                    await message.answer(
                        f"Максимальная сумма для создания заявки составляет {summ_max} {name.upper()}.")
                else:
                    rub = (float(sum) * crypt) * dollar
                    rub = rub + (rub * 0.05)
                    await state.update_data(sum=rub)
                    await state.update_data(payment=sum)
                    await message.answer(f"Введите адрес кошелька для получения:")
                    await state.set_state(UserState.buy_card)
            elif name == "eth":
                for i in result['data']:
                    if i["instId"] == "ETH-USDT":
                        crypt = float(i["last"])
                dol = 1 / dollar * 2300
                summ = 1 / crypt * dol
                dol_max = 1 / dollar * 1000000
                summ_max = 1 / crypt * dol_max
                if float(sum) < float(summ):
                    await message.answer(f"Минимальная сумма для создания заявки составляет {summ} {name.upper()}.")
                    await state.set_state(UserState.buy_sum)
                elif float(sum) > float(summ_max):
                    await message.answer(
                        f"Максимальная сумма для создания заявки составляет {summ_max} {name.upper()}.")
                else:
                    rub = (float(sum) * crypt) * dollar
                    rub = rub + (rub * 0.05)
                    await state.update_data(sum=rub)
                    await state.update_data(payment=sum)
                    await message.answer(f"Введите адрес кошелька для получения:")
                    await state.set_state(UserState.buy_card)
            elif name == "tron":
                for i in result['data']:
                    if i["instId"] == "TRX-USDT":
                        crypt = float(i["last"])
                dol = 1 / dollar * 2300
                summ = 1 / crypt * dol
                dol_max = 1 / dollar * 1000000
                summ_max = 1 / crypt * dol_max
                if float(sum) < float(summ):
                    await message.answer(f"Минимальная сумма для создания заявки составляет {summ} {name.upper()}.")
                    await state.set_state(UserState.buy_sum)
                elif float(sum) > float(summ_max):
                    await message.answer(
                        f"Максимальная сумма для создания заявки составляет {summ_max} {name.upper()}.")
                else:
                    rub = (float(sum) * crypt) * dollar
                    rub = rub + (rub * 0.05)
                    await state.update_data(sum=rub)
                    await state.update_data(payment=sum)
                    await message.answer(f"Введите адрес кошелька для получения:")
                    await state.set_state(UserState.buy_card)
    else:
        await message.answer(f"Введите числовое значение. Например: <b>5000</b>")
        await state.set_state(UserState.buy_sum)


@rt.message(UserState.buy_card)
async def transaction(message: Message, state: FSMContext):
    url = await DBuser.url_return()
    markup = await create_markup('inline',
                                 [[['💴 Оплата переведена', 'translated'],
                                   [f'⛔️ Отменить заявку', 'canceled']],
                                  [['👤 Поддержка', f'{url}']]])
    card = message.text
    check = card.lower()
    data = await state.get_data()
    sum = data['sum']
    name = data["name"]
    await state.update_data(card=card)
    if name == "sol":
        if len(check) < 32:
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети SOL.</b>
            
Введите действительный адрес""")
            await state.set_state(UserState.buy_card)
        else:
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
            if float(money[0][1]) < float(data['payment']):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_card()
                rek = random.choice(rek)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Покупка")
                await DBuser.app(message.from_user.id)
                try:
                    sum1 = round(sum)
                except:
                    sum1 = sum
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                        text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Покупка

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                        reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Покупка

Пользователь @{message.from_user.username}

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>""", reply_markup=markup)
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
    elif name == "btc":
        if card[0] != "1" and card[0] != "3" and check[0:3] != "bc1":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети BTC.</b>
            
Введите действительный адрес""")
            await state.set_state(UserState.buy_card)
        else:
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
            if float(money[0][1]) < float(data['payment']):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_card()
                rek = random.choice(rek)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Покупка")
                await DBuser.app(message.from_user.id)
                try:
                    sum1 = round(sum)
                except:
                    sum1 = sum
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Покупка

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Покупка

Пользователь @{message.from_user.username}

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>""", reply_markup=markup)
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
    elif name == "bnb":
        if check[0:2] != "0x":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети BNB.</b>
            
Введите действительный адрес""")
            await state.set_state(UserState.buy_card)
        else:
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
            if float(money[0][1]) < float(data['payment']):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_card()
                rek = random.choice(rek)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Покупка")
                await DBuser.app(message.from_user.id)
                try:
                    sum1 = round(sum)
                except:
                    sum1 = sum
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Покупка

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Покупка

Пользователь @{message.from_user.username}

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>""", reply_markup=markup)
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
    elif name == "ltc":
        if check[0] != "m" and check[0] != "l":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети LTC.</b>

Введите действительный адрес""")
            await state.set_state(UserState.buy_card)
        else:
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
            if float(money[0][1]) < float(data['payment']):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_card()
                rek = random.choice(rek)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Покупка")
                await DBuser.app(message.from_user.id)
                try:
                    sum1 = round(sum)
                except:
                    sum1 = sum
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Покупка

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Покупка

Пользователь @{message.from_user.username}

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>""", reply_markup=markup)
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
    elif name == "ton":
        if card[0] != "E" and card[0] != "U":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети TON.</b>

Введите действительный адрес""")
            await state.set_state(UserState.buy_card)
        else:
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
            if float(money[0][1]) < float(data['payment']):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_card()
                rek = random.choice(rek)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Покупка")
                await DBuser.app(message.from_user.id)
                try:
                    sum1 = round(sum)
                except:
                    sum1 = sum
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Покупка

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Покупка

Пользователь @{message.from_user.username}

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>""", reply_markup=markup)
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
    elif name == "eth":
        if check[0:2] != "0x":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети ETH.</b>

Введите действительный адрес""")
            await state.set_state(UserState.buy_card)
        else:
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
            if float(money[0][1]) < float(data['payment']):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_card()
                rek = random.choice(rek)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Покупка")
                await DBuser.app(message.from_user.id)
                try:
                    sum1 = round(sum)
                except:
                    sum1 = sum
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Покупка

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Покупка

Пользователь @{message.from_user.username}

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>""", reply_markup=markup)
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
    elif name == "tron":
        if card[0] != "T":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети TRON.</b>

Введите действительный адрес""")
            await state.set_state(UserState.buy_card)
        else:
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
            if float(money[0][1]) < float(data['payment']):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_card()
                rek = random.choice(rek)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Покупка")
                await DBuser.app(message.from_user.id)
                try:
                    sum1 = round(sum)
                except:
                    sum1 = sum
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Покупка

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Покупка

Пользователь @{message.from_user.username}

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>""", reply_markup=markup)
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
    elif name == "trc":
        if check[0:2] != "0x" and card[0] != "T":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети TRC20.</b>

Введите действительный адрес""")
            await state.set_state(UserState.buy_card)

        else:
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
            if float(money[0][1]) < float(data['payment']):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_card()
                rek = random.choice(rek)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Покупка")
                await DBuser.app(message.from_user.id)
                try:
                    sum1 = round(sum)
                except:
                    sum1 = sum
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                            text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Покупка

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                            reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Покупка

Пользователь @{message.from_user.username}

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>""", reply_markup=markup)
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
    elif name == "erc":
        if check[0:2] != "0x":
            await message.answer(f"""<b>Веденный вами адрес не соответствует сети ERC20.</b>

Введите действительный адрес""")
            await state.set_state(UserState.buy_card)
        else:
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
            if float(money[0][1]) < float(data['payment']):
                markup = await create_markup('inline',
                                             [[["Вернуться в главное меню", "back"]]])
                await message.answer(f"""<b>⛔️ Ошибка: для указанной суммы нет доступных реквизитов.</b>

Попробуйте позже или обратитесь в поддержку.""", reply_markup=markup)
            else:
                await DBuser.bid_sell(name, card, sum, message.message_id + 1, message.from_user.id)
                ids = await DBuser.return_bid_sell_id(sum, name, card)
                await state.update_data(ids=ids)
                rek = await DBuser.return_card()
                rek = random.choice(rek)
                current = datetime.now()
                await DBuser.add_story(message.from_user.id, f"{current.day}.{current.month}", "Покупка")
                await DBuser.app(message.from_user.id)
                try:
                    sum1 = round(sum)
                except:
                    sum1 = sum
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=f"{message.message_id + 1}",
                                        text=f"""➖Время заявки действует 30 минут➖

<b>📄 Номер заявки — {ids} → Покупка

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>


🔆 Если вдруг у вас возникли трудности или вам что то не понятно, напишите Оператору...""",
                                        reply_markup=markup)
                markup = await create_markup('inline',
                                             [[["Оплатил", "paid_buy"], ["Отклонить", "no_paid"]]])
                await bot.send_message(chat_id=admins_id[0], text=f"""➖Время заявки действует 30 минут➖

<b>📄 Новая заявка — {ids} → Покупка

Пользователь @{message.from_user.username}

⚙️ К получению — {data["payment"]} {name.upper()}
⚙️ Адрес Кошелька получателя — {card}

Способ оплаты: По номеру карты
Реквизиты: 
<pre>{rek[0][0]}</pre>
К оплате: 
<pre>{sum1} RUB</pre></b>""", reply_markup=markup)
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