from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from data.loader import rt, bot
from aiogram import F
from handlers.admin.start import AdminState
from utils.db.api.user import DBuser
from utils.system.inline_btns import create_markup
from utils.system.adminka import AdminIs


@rt.message(F.text == 'Реквизиты', AdminIs(), StateFilter(default_state))
async def details(message: Message, state: FSMContext):
    markup = await create_markup('inline', [[["Карта", "cards"]],
                                            [['SOL', 'sol'], ['BNB', 'bnb']],
                                            [['BTC', 'btc'], ["LTC", "ltc"]],
                                            [["USDT", "usdt_admin"], ["TON", "ton"]],
                                            [["ETH", "eth"], ["TRON", "tron"]],
                                            [["Отмена", "cancel"]]])
    await message.answer(f"Выберите валюту", reply_markup=markup)
    await state.set_state(AdminState.rek)


@rt.callback_query(F.data == 'reks', AdminIs())
async def reks(call: CallbackQuery, state: FSMContext):
    markup = await create_markup('inline', [[["Карта", "cards"]],
                                            [['SOL', 'sol'], ['BNB', 'bnb']],
                                            [['BTC', 'btc'], ["LTC", "ltc"]],
                                            [["USDT", "usdt_admin"], ["TON", "ton"]],
                                            [["ETH", "eth"], ["TRON", "tron"]],
                                            [["Отмена", "cancel"]]])
    await call.message.answer(f"Выберите валюту", reply_markup=markup)
    await state.set_state(AdminState.rek)


@rt.callback_query(F.data == 'cards', AdminIs(), AdminState.rek)
async def cards(call: CallbackQuery, state: FSMContext):
    card = await DBuser.return_card()
    if not card:
        markup = await create_markup('inline', [[["Добавить", "add_card"]],
                                                [["Назад", "reks"]]])
        await call.message.answer(f"Карта еще не добавлена", reply_markup=markup)
        await state.set_state(AdminState.cards)
    else:
        markup = await create_markup('inline',
                                     [*[[_] for _ in await DBuser.return_cards()], [["Добавить карту", "add_card"]], [["❌Отмена", "cancel"]]])
        await call.message.answer(f"Выберите карту", reply_markup=markup)
        await state.set_state(AdminState.cards)


@rt.callback_query(F.data == 'change_card', AdminIs(), AdminState.dels)
async def change_card(call: CallbackQuery, state: FSMContext):
    card = await state.get_data()
    await DBuser.delete_card(card["card"])
    await call.message.answer(f"Успешно")
    await state.clear()


@rt.message(AdminState.change_card, AdminIs())
async def change_card_state(message: Message, state: FSMContext):
    await DBuser.change_card(message.text)
    await message.answer(f"Успешно")
    await state.clear()


@rt.callback_query(F.data == 'add_card', AdminIs(), AdminState.cards)
async def add_card(call: CallbackQuery, state: FSMContext):
    await call.message.answer(f"Введите карту")
    await state.set_state(AdminState.card)


@rt.message(AdminState.card, AdminIs())
async def card_state(message: Message, state: FSMContext):
    await DBuser.add_card(message.text)
    await message.answer(f"Успешно")
    await state.clear()


@rt.callback_query(AdminState.cards, AdminIs())
async def cards_state(call: CallbackQuery, state: FSMContext):
    markup = await create_markup('inline', [[["Удалить", "change_card"]],
                                                        [["Назад", "cards"]]])
    card = call.data
    await state.update_data(card=card)
    await call.message.answer(f"{card}", reply_markup=markup)
    await state.set_state(AdminState.dels)


@rt.callback_query(F.data == 'usdt_admin', AdminIs(), AdminState.rek)
async def usdt_admin(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    markup = await create_markup('inline', [[['TRC20', 'trc'], ['ERC20', 'erc']],
                                            [["Назад", "reks"]]])
    await call.message.answer(f"Выберите сеть", reply_markup=markup)
    await state.set_state(AdminState.rek)


@rt.callback_query(AdminState.rek, AdminIs())
async def rek_state(call: CallbackQuery, state: FSMContext):
    if call.data == "sol":
        sol = await DBuser.return_sol()
        if not sol:
            markup = await create_markup('inline', [[["Добавить", "add_rek"], ["Назад", "reks"]]])
            await call.message.answer("Ничего нету", reply_markup=markup)
            await state.update_data(name="sol")
            await state.update_data(check=0)
            await state.set_state(AdminState.add_rek)
        else:
            markup = await create_markup('inline', [[["Изменить реквизиты", "rek_change"], ["Изменить баланс", "bal_rek"]],
                                                    [["Назад", "reks"]]])
            await call.message.answer(f"адрес: <code>{sol[0][0]}</code> баланс: <code>{sol[0][1]}</code>", reply_markup=markup)
            await state.update_data(name="sol")
            await state.update_data(check=0)
            await state.set_state(AdminState.rek_change)
    elif call.data == "bnb":
        bnb = await DBuser.return_bnb()
        if not bnb:
            markup = await create_markup('inline', [[["Добавить", "add_rek"], ["Назад", "reks"]]])
            await call.message.answer("Ничего нету", reply_markup=markup)
            await state.update_data(name="bnb")
            await state.update_data(check=0)
            await state.set_state(AdminState.add_rek)
        else:
            markup = await create_markup('inline', [[["Изменить реквизиты", "rek_change"], ["Изменить баланс", "bal_rek"]],
                                                    [["Назад", "reks"]]])
            await call.message.answer(f"адрес: <code>{bnb[0][0]}</code> баланс: <code>{bnb[0][1]}</code>", reply_markup=markup)
            await state.update_data(name="bnb")
            await state.update_data(check=0)
            await state.set_state(AdminState.rek_change)
    elif call.data == "btc":
        btc = await DBuser.return_btc()
        if not btc:
            markup = await create_markup('inline', [[["Добавить", "add_rek"], ["Назад", "reks"]]])
            await call.message.answer("Ничего нету", reply_markup=markup)
            await state.update_data(name="btc")
            await state.update_data(check=0)
            await state.set_state(AdminState.add_rek)
        else:
            markup = await create_markup('inline', [[["Изменить реквизиты", "rek_change"], ["Изменить баланс", "bal_rek"]],
                                                    [["Назад", "reks"]]])
            await call.message.answer(f"адрес: <code>{btc[0][0]}</code> баланс: <code>{btc[0][1]}</code>", reply_markup=markup)
            await state.update_data(name="btc")
            await state.update_data(check=0)
            await state.set_state(AdminState.rek_change)
    elif call.data == "ltc":
        ltc = await DBuser.return_ltc()
        if not ltc:
            markup = await create_markup('inline', [[["Добавить", "add_rek"], ["Назад", "reks"]]])
            await call.message.answer("Ничего нету", reply_markup=markup)
            await state.update_data(name="ltc")
            await state.update_data(check=0)
            await state.set_state(AdminState.add_rek)
        else:
            markup = await create_markup('inline', [[["Изменить реквизиты", "rek_change"], ["Изменить баланс", "bal_rek"]],
                                                    [["Назад", "reks"]]])
            await call.message.answer(f"адрес: <code>{ltc[0][0]}</code> баланс: <code>{ltc[0][1]}</code>", reply_markup=markup)
            await state.update_data(name="ltc")
            await state.update_data(check=0)
            await state.set_state(AdminState.rek_change)
    elif call.data == "ton":
        ton = await DBuser.return_ton()
        if not ton:
            markup = await create_markup('inline', [[["Добавить", "add_rek"], ["Назад", "reks"]]])
            await call.message.answer("Ничего нету", reply_markup=markup)
            await state.update_data(name="ton")
            await state.update_data(check=0)
            await state.set_state(AdminState.add_rek)
        else:
            markup = await create_markup('inline', [[["Изменить реквизиты", "rek_change"], ["Изменить баланс", "bal_rek"]],
                                                    [["Назад", "reks"]]])
            await call.message.answer(f"адрес: <code>{ton[0][0]}</code> баланс: <code>{ton[0][1]}</code>", reply_markup=markup)
            await state.update_data(name="ton")
            await state.update_data(check=0)
            await state.set_state(AdminState.rek_change)
    elif call.data == "eth":
        eth = await DBuser.return_eth()
        if not eth:
            markup = await create_markup('inline', [[["Добавить", "add_rek"], ["Назад", "reks"]]])
            await call.message.answer("Ничего нету", reply_markup=markup)
            await state.update_data(name="eth")
            await state.update_data(check=0)
            await state.set_state(AdminState.add_rek)
        else:
            markup = await create_markup('inline', [[["Изменить реквизиты", "rek_change"], ["Изменить баланс", "bal_rek"]],
                                                    [["Назад", "reks"]]])
            await call.message.answer(f"адрес: <code>{eth[0][0]}</code> баланс: <code>{eth[0][1]}</code>", reply_markup=markup)
            await state.update_data(name="eth")
            await state.update_data(check=0)
            await state.set_state(AdminState.rek_change)
    elif call.data == "tron":
        tron = await DBuser.return_tron()
        if not tron:
            markup = await create_markup('inline', [[["Добавить", "add_rek"], ["Назад", "reks"]]])
            await call.message.answer("Ничего нету", reply_markup=markup)
            await state.update_data(name="tron")
            await state.update_data(check=0)
            await state.set_state(AdminState.add_rek)
        else:
            markup = await create_markup('inline', [[["Изменить реквизиты", "rek_change"], ["Изменить баланс", "bal_rek"]],
                                                    [["Назад", "reks"]]])
            await call.message.answer(f"адрес: <code>{tron[0][0]}</code> баланс: <code>{tron[0][1]}</code>", reply_markup=markup)
            await state.update_data(name="tron")
            await state.update_data(check=0)
            await state.set_state(AdminState.rek_change)
    elif call.data == "trc":
        trc = await DBuser.return_trc()
        if not trc:
            markup = await create_markup('inline', [[["Добавить", "add_rek"], ["Назад", "reks"]]])
            await call.message.answer("Ничего нету", reply_markup=markup)
            await state.update_data(name="trc")
            await state.update_data(check=0)
            await state.set_state(AdminState.add_rek)
        else:
            markup = await create_markup('inline', [[["Изменить реквизиты", "rek_change"], ["Изменить баланс", "bal_rek"]],
                                                    [["Назад", "reks"]]])
            await call.message.answer(f"адрес: <code>{trc[0][0]}</code> баланс: <code>{trc[0][1]}</code>", reply_markup=markup)
            await state.update_data(name="trc")
            await state.update_data(check=0)
            await state.set_state(AdminState.rek_change)
    elif call.data == "erc":
        erc = await DBuser.return_erc()
        if not erc:
            markup = await create_markup('inline', [[["Добавить", "add_rek"], ["Назад", "reks"]]])
            await call.message.answer("Ничего нету", reply_markup=markup)
            await state.update_data(name="erc")
            await state.update_data(check=0)
            await state.set_state(AdminState.add_rek)
        else:
            markup = await create_markup('inline', [[["Изменить реквизиты", "rek_change"], ["Изменить баланс", "bal_rek"]],
                                                    [["Назад", "reks"]]])
            await call.message.answer(f"адрес: <code>{erc[0][0]}</code> баланс: <code>{erc[0][1]}</code>", reply_markup=markup)
            await state.update_data(name="erc")
            await state.update_data(check=0)
            await state.set_state(AdminState.rek_change)


@rt.callback_query(F.data == 'rek_change', AdminIs(), AdminState.rek_change)
async def rek_change(call: CallbackQuery, state: FSMContext):
    await state.update_data(check=1)
    markup = await create_markup('inline', [[["Назад", "reks"]]])
    await call.message.answer(f"Введите реквизиты", reply_markup=markup)
    await state.set_state(AdminState.rek_change)


@rt.callback_query(F.data == 'bal_rek', AdminIs(), AdminState.rek_change)
async def bal_rek(call: CallbackQuery, state: FSMContext):
    markup = await create_markup('inline', [[["Назад", "reks"]]])
    await call.message.answer(f"Введите баланс", reply_markup=markup)
    await state.set_state(AdminState.bal_rek)


@rt.callback_query(F.data == 'add_rek', AdminIs(), AdminState.add_rek)
async def add_rek(call: CallbackQuery, state: FSMContext):
    await state.update_data(check=1)
    markup = await create_markup('inline', [[["Назад", "reks"]]])
    await call.message.answer(f"Введите реквизиты", reply_markup=markup)
    await state.set_state(AdminState.add_rek)


@rt.message(AdminState.add_rek, AdminIs())
async def add_rek_state(message: Message, state: FSMContext):
    data = await state.get_data()
    if data["check"] == 1:
        await state.update_data(rek=message.text)
        markup = await create_markup('inline', [[["Назад", "reks"]]])
        await message.answer(f"Введите баланс", reply_markup=markup)
        await state.set_state(AdminState.add_rek2)


@rt.message(AdminState.add_rek2, AdminIs())
async def add_rek2(message: Message, state: FSMContext):
    bal = message.text
    if bal.isdigit():
        data = await state.get_data()
        await DBuser.add_rek(data['name'], data["rek"], bal)
        await message.answer(f"Добавлено")
        await state.clear()
    else:
        markup = await create_markup('inline', [[["Назад", "reks"]]])
        await message.answer(f"Введите сумму", reply_markup=markup)
        await state.set_state(AdminState.add_rek2)


@rt.message(AdminState.rek_change, AdminIs())
async def rek_change_state(message: Message, state: FSMContext):
    data = await state.get_data()
    if data['check'] == 1:
        await DBuser.rek_name(data['name'], message.text)
        await message.answer(f"Изменено")
        await state.clear()


@rt.message(AdminState.bal_rek, AdminIs())
async def bal_rek_state(message: Message, state: FSMContext):
    bal = message.text
    if bal.isdigit():
        data = await state.get_data()
        await DBuser.rek_sum(data['name'], bal)
        await message.answer(f"Изменено")
        await state.clear()
    else:
        markup = await create_markup('inline', [[["Назад", "reks"]]])
        await message.answer(f"Введите сумму", reply_markup=markup)
        await state.set_state(AdminState.bal_rek)
