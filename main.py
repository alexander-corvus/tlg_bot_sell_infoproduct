from aiogram.utils import executor
from database import func_auto
from logs.logs_settings import logger
from loader import dp
from handlers import client, admin


@logger.catch
async def on_startup(_):
    logger.info('bot is running')
    func_auto.create_tables()


if __name__ == '__main__':
    admin.register_handlers(disp=dp)
    client.register_handlers(disp=dp)

    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    except Exception as exception_name:
        logger.error(f'bot launch error in {__file__}, 19: {exception_name}')

