from logs.logs_settings import logger
from loader import bot, ADMIN_ID_1, ADMIN_ID_2
from handlers.client import DEFAULT_COMMANDS


def permission(func):
    """
    Декоратор, проверяющий ID администратора
    """
    async def wrapper(mess_call):
        logger.info(f'permission decorator worked')

        if (mess_call.from_user.id == ADMIN_ID_1) or (mess_call.from_user.id == ADMIN_ID_2):
            logger.info(f'{mess_call.from_user.id}, {mess_call.from_user.username}, {func.__name__}')

            await func(mess_call)

        else:
            logger.warning(f'{mess_call.from_user.id}, {mess_call.from_user.username}, попытка входа в админку')

            def_commands = [f'/{command} - {description}' for command, description in DEFAULT_COMMANDS]
            await bot.send_message(mess_call.from_user.id,
                                   '\n'.join(def_commands))

    return wrapper


def permission_state(func):
    """
    Декоратор, проверяющий ID администратора для state
    """

    async def wrapper(mess_call, state):
        logger.info(f'permission_state decorator worked')

        if (mess_call.from_user.id == ADMIN_ID_1) or (mess_call.from_user.id == ADMIN_ID_2):
            logger.info(f'{mess_call.from_user.id}, {mess_call.from_user.username}, {func.__name__}')

            await func(mess_call, state)

        else:
            logger.warning(f'{mess_call.from_user.id}, {mess_call.from_user.username}, попытка входа в админку')

            def_commands = [f'/{command} - {description}' for command, description in DEFAULT_COMMANDS]
            await bot.send_message(mess_call.from_user.id,
                                   '\n'.join(def_commands))

    return wrapper

