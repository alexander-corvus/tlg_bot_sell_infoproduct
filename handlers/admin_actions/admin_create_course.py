from logs.logs_settings import logger
from loader import bot
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from markup.m_admin import create_course_checkup, cancel_kb
from utils.decorators import permission, permission_state
from database.db_models import Course
from datetime import datetime


class StatesCreateCourse(StatesGroup):
    """
    Класс состояний администратора
    для создания нового курса.
    """
    course_img = State()
    course_name = State()
    course_description = State()
    course_cost = State()
    course_link = State()
    checkup_data = State()


@permission
@logger.catch
async def create_course_start(callback: CallbackQuery):
    """
    Активация логики создания курса.
    """
    await StatesCreateCourse.course_img.set()
    await callback.message.answer('Загрузи фото (обложку) курса.', reply_markup=cancel_kb)
    await callback.answer()


@permission_state
@logger.catch
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    """
    Выход из логики создания курса
    """
    current_state = await state.get_state()

    if current_state is None:
        return

    logger.info(f'state before cancelled: {current_state}')

    await state.finish()
    await callback.answer('CANCELLED', show_alert=True)
    await callback.message.answer(f'Ок, {callback.from_user.first_name}, выходим.\n'
                                  f'Введи /admin для просмотра команд админки')


@permission_state
@logger.catch
async def set_image(message: Message, state: FSMContext):
    """
    Получение первого ответа, сохранение photo_id в memory storage.
    """
    async with state.proxy() as data:
        data['course_img'] = message.photo[0].file_id

    await StatesCreateCourse.next()
    await message.answer('Напиши название нового курса.', reply_markup=cancel_kb)


@permission_state
@logger.catch
async def set_course_name(message: Message, state: FSMContext):
    """
    Получение второго ответа, сохранение названия в memory storage.
    """
    async with state.proxy() as data:
        data['course_name'] = message.text

    await StatesCreateCourse.next()
    await message.answer('Введи описание нового курса.', reply_markup=cancel_kb)


@permission_state
@logger.catch
async def set_course_description(message: Message, state: FSMContext):
    """
    Получение третьего ответа, сохранение описания в memory storage.
    """
    async with state.proxy() as data:
        data['course_description'] = message.text

    await StatesCreateCourse.next()
    await message.answer('Укажи стоимость курса, целое число в рублях.', reply_markup=cancel_kb)


@permission_state
@logger.catch
async def set_course_cost(message: Message, state: FSMContext):
    """
    Получение четвертого ответа, сохранение стоимости курса в memory storage.
    """

    if message.text.isdigit():
        async with state.proxy() as data:
            data['course_cost'] = message.text

        await StatesCreateCourse.next()
        await message.answer('Введи ссылку на скачивание курса.', reply_markup=cancel_kb)
    else:
        logger.warning(f'{message.from_user.username}, некорректно введена стоимость курса')
        await message.reply('Пожалуйста, введи стоимость курса в рублях, целым числом.')
        await StatesCreateCourse.course_cost.set()


@permission_state
@logger.catch
async def set_course_link(message: Message, state: FSMContext):
    """
    Получение пятого, последнего ответа, сохранение ссылки на курс в memory storage,
    запрос подтверждения корректности введенных данных.
    """
    new_course = '<b>Вот что получилось:</b>\n'
    photo_id = ''
    async with state.proxy() as data:
        data['course_link'] = message.text

        for field, val in data.items():
            if field == 'course_img':
                photo_id = val
            else:
                new_course = new_course + '\n' + f'<i><b>{str(field)}</b></i>' + ' : ' + str(val) + '\n'

    await StatesCreateCourse.next()
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=photo_id,
                         caption=new_course,
                         parse_mode='HTML')
    await message.answer('Проверь данные. Если все хорошо, нажми "Загрузить курс", '
                         'если надо что-то исправить - "Отмена"', reply_markup=create_course_checkup)


@permission_state
@logger.catch
async def check_new_course(callback: CallbackQuery, state: FSMContext):
    """
    Загрузка в БД нового курса после подтверждения корректности данных.
    """
    async with state.proxy() as data:
        try:
            Course.create(
                image_id=data['course_img'],
                course_name=data['course_name'],
                description=data['course_description'],
                cost=data['course_cost'],
                upload_date=datetime.now().strftime('%Y.%m.%d_%H:%M:%S'),
                download_link=data['course_link']
            )
        except Exception as ex_name:
            logger.error(f'ошибка загрузки нового курса в БД: {ex_name}')
            await state.finish()
            await callback.answer('ERROR :(', show_alert=True)
            await callback.message.answer(f'При загрузке нового курса в БД произошла ошибка <b>{ex_name}</b>. '
                                          f'Пожалуйста, свяжитесь с разработчиком.', parse_mode='HTML')
        else:
            await state.finish()
            await callback.answer('GREAT!', show_alert=True)
            await callback.message.answer('Курс загружен в БД. Введи /admin для просмотра доступных команд.')


@logger.catch
def register_handlers(disp: Dispatcher):
    """
    Регистратор хэндлеров
    """
    logger.info('register_handlers for admin_create_course')

    disp.register_callback_query_handler(create_course_start, text='add_course', state=None)

    disp.register_callback_query_handler(cancel_handler, text='cancel', state='*')

    disp.register_message_handler(set_image, content_types=['photo'], state=StatesCreateCourse.course_img)
    disp.register_message_handler(set_course_name, state=StatesCreateCourse.course_name)
    disp.register_message_handler(set_course_description, state=StatesCreateCourse.course_description)
    disp.register_message_handler(set_course_cost, state=StatesCreateCourse.course_cost)
    disp.register_message_handler(set_course_link, state=StatesCreateCourse.course_link)
    disp.register_callback_query_handler(check_new_course, state=StatesCreateCourse.checkup_data)
