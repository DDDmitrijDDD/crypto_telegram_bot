async def on_startup(bot):
    from utils.system.notify_admins import on_startup_notify
    # уведомление админа о запуске
    await on_startup_notify(bot)

    from utils.system.commands import set_default_commands
    # установка команд
    await set_default_commands(bot)


async def main():
    """запуск бота"""
    from data.loader import dp, bot
    from handlers import rt

    dp.include_router(rt)
    await on_startup(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    print("Бот запущен")
    import asyncio
    asyncio.run(main())
