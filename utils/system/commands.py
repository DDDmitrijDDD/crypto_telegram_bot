from aiogram.types import BotCommand
from aiogram.types.bot_command_scope_chat import BotCommandScopeChat
from data.config import admins_id
from data.loader import Bot


async def set_default_commands(bot: Bot):
    """команды пользователя
    """
    await bot.set_my_commands(
        [
            BotCommand(command='start', description='Запуск бота'),
        ]
    )


async def set_admin_commands(bot: Bot):
    """команды админа"""
    for _ in admins_id:
        await bot.set_my_commands(
            [
                BotCommand(command='start', description='💤 Запустить бота'),
            ],
            scope=BotCommandScopeChat(chat_id=_)
        )
