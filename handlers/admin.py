from logs.logs_settings import logger
from aiogram import Dispatcher
from aiogram.types import Message
from loader import bot
from markup.m_admin import admin_start_kb
from utils.decorators import permission
from handlers.admin_actions import (
                            admin_create_course,
                            admin_exist_data,
                            admin_edit_course
)


@permission
@logger.catch
async def admin_start(message: Message):
    """
    Запуск администрирования бота
    """
    logger.info(f'{message.from_user.id}, {message.from_user.username}, выполнен вход в админку')
    await bot.send_message(
        message.from_user.id,
        f'Привет, {message.from_user.first_name}! Что ты хочешь сделать?',
        reply_markup=admin_start_kb
    )


@logger.catch
def register_handlers(disp: Dispatcher):
    """
    Регистратор хэндлеров администратора
    """
    logger.info('register_handlers for admin')

    disp.register_message_handler(admin_start, commands=['admin'])
    admin_exist_data.register_handlers(disp=disp)
    admin_create_course.register_handlers(disp=disp)
    admin_edit_course.register_handlers(disp=disp)
