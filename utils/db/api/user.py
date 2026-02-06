import os
import aiosqlite


class DBuser:
    """API к БД с пользователями"""
    path = 'utils/db/files/users.db'
    userka = 'utils/db/files/users/{}.db'

    @staticmethod
    async def create():
        """создание таблицы"""
        if not os.path.exists('utils/db/files/'):
            os.mkdir('utils/db/files/')

        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute('CREATE TABLE IF NOT EXISTS Users '
                             '(id INTEGER, '
                             'username TEXT, '
                             'fullname TEXT, '
                             'date TEXT, '
                             'balance INTEGER DEFAULT 0, '
                             'rating TEXT DEFAULT новичок, '
                             'ref INTEGER, '
                             'sign BOOL DEFAULT false,'
                             'odin DEFAULT 2,'
                             'arenda DEFAULT 0);')
            await db.commit()

            if not os.path.exists(f'utils/db/files/users/'):
                os.mkdir(f'utils/db/files/users/')

    @staticmethod
    async def add_new(id_, username, ref):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute('INSERT INTO Users (user_id, name, ref_link) '
                                 'VALUES (?, ?, ?)',
                                 (id_, username, ref))
            await db.commit()

    @staticmethod
    async def return_user(id_):
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute(f'SELECT * FROM users WHERE user_id=?', (id_,)):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def return_sol():
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute(f'SELECT * FROM sol'):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def return_crypt(crypt):
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute(f'SELECT * FROM {crypt}'):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def return_bnb():
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute(f'SELECT * FROM bnb'):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def return_btc():
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute(f'SELECT * FROM btc'):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def return_erc():
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute(f'SELECT * FROM erc'):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def return_eth():
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute(f'SELECT * FROM eth'):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def return_ltc():
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute(f'SELECT * FROM ltc'):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def return_ton():
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute(f'SELECT * FROM ton'):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def return_card():
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute(f'SELECT * FROM card'):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def return_trc():
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute(f'SELECT * FROM trc'):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def return_tron():
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute(f'SELECT * FROM tron'):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def add_ref(id_, ref):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'INSERT INTO ref (user_id, referal) VALUES (?, ?)',
                             (id_, ref))
            await db.commit()

    @staticmethod
    async def add_story(id_, date, type):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'INSERT INTO story (user_id, date, type) VALUES (?, ?, ?)',
                             (id_, date, type))
            await db.commit()

    @staticmethod
    async def add_card(card):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'INSERT INTO card (card) VALUES (?)',
                             (card,))
            await db.commit()

    @staticmethod
    async def add_rek(name, rek, sum):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'INSERT INTO {name} (rek, sum) VALUES (?, ?)',
                             (rek, sum))
            await db.commit()

    @staticmethod
    async def bid_sell(crypt, rek, sum, mess, ids):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'INSERT INTO bid_sell (card, sum, crypt, message_id, user_id) VALUES (?, ?, ?, ?, ?)',
                             (rek, sum, crypt, mess, ids))
            await db.commit()

    @staticmethod
    async def return_bid_sell_id(sum, crypt, card):
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute('SELECT id FROM bid_sell WHERE sum=? AND crypt=? AND card=?', (sum, crypt, card)):
                return [_ async for _ in info][0][0]
            return None

    @staticmethod
    async def delete_bid_sell(id_):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'DELETE FROM bid_sell WHERE id=?', (id_,))
            await db.commit()

    @staticmethod
    async def delete_card(card):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'DELETE FROM card WHERE card=?', (card,))
            await db.commit()

    @staticmethod
    async def return_bid_sell_message(sum, crypt, card):
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute('SELECT message_id FROM bid_sell WHERE sum=? AND crypt=? AND card=?',
                                        (sum, crypt, card)):
                return [_ async for _ in info][0][0]
            return None

    @staticmethod
    async def return_bid_sell_user(sum, crypt, card):
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute('SELECT message_id FROM bid_sell WHERE sum=? AND crypt=? AND card=?',
                                        (sum, crypt, card)):
                return [_ async for _ in info][0][0]
            return None

    @staticmethod
    async def url_return():
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute('SELECT url FROM url'):
                return [_ async for _ in info][0][0]
            return None

    @staticmethod
    async def return_bid_sell(ids):
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute('SELECT * FROM bid_sell WHERE user_id=?',
                                        (ids,)):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def return_bid_sell_id2(ids):
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute('SELECT message_id FROM bid_sell WHERE id=?',
                                        (ids,)):
                return [_ async for _ in info][0][0]
            return None

    @staticmethod
    async def return_info_user_name(name):
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute('SELECT * FROM users WHERE name=?', (name,)):
                return [_ async for _ in info][0]
            return None

    @staticmethod
    async def return_all_id():
        async with aiosqlite.connect(DBuser.path) as db:
            return [_[0] async for _ in await db.execute(f'SELECT user_id FROM Users')]

    @staticmethod
    async def ban(id_):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'INSERT INTO ban (user_id) VALUES (?)',
                             (id_,))
            await db.commit()

    @staticmethod
    async def return_all_name():
        async with aiosqlite.connect(DBuser.path) as db:
            return [[str(_[0]), str(_[0])] async for _ in await db.execute(f'SELECT name FROM users')]

    @staticmethod
    async def return_cards():
        async with aiosqlite.connect(DBuser.path) as db:
            return [[str(_[0]), str(_[0])] async for _ in await db.execute(f'SELECT * FROM card')]

    @staticmethod
    async def return_story(id_):
        async with aiosqlite.connect(DBuser.path) as db:
            if info := await db.execute(f'SELECT * FROM story WHERE user_id=?', (id_,)):
                return [_ async for _ in info]
            return None

    @staticmethod
    async def rek_name(name, rek):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'UPDATE {name} SET rek=?', (rek,))
            await db.commit()

    @staticmethod
    async def url(url):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'UPDATE url SET url=?', (url,))
            await db.commit()

    @staticmethod
    async def change_card(rek):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'UPDATE card SET card=?', (rek,))
            await db.commit()

    @staticmethod
    async def rek_sum_change(name, sum):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'UPDATE {name} SET sum=sum - ?', (sum,))
            await db.commit()

    @staticmethod
    async def app(ids):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'UPDATE users SET app=app+1 WHERE user_id=?', (ids,))
            await db.commit()

    @staticmethod
    async def rek_sum(name, sum):
        async with aiosqlite.connect(DBuser.path) as db:
            await db.execute(f'UPDATE {name} SET sum=?', (sum,))
            await db.commit()

    @staticmethod
    async def return_ban():
        async with aiosqlite.connect(DBuser.path) as db:
            return [_[0] async for _ in await db.execute(f'SELECT user_id FROM ban')]

    @staticmethod
    async def check_user(id_):
        async with aiosqlite.connect(DBuser.path) as db:
            async with db.execute('SELECT * FROM Users WHERE user_id=?', (id_,)) as cursor:
                async for _ in cursor:
                    return True
                return False