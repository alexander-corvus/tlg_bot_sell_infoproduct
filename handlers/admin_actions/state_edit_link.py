from logs.logs_settings import logger
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from utils.decorators import permission_state
from database.db_models import Course, UpdateCourses
from markup.m_admin import edit_markup
from handlers.admin_actions.admin_exist_data import now


class StatesEditLink(StatesGroup):
    """
    Класс состояний администратора
    для редактирования ссылки на скачивание курса.
    """
    course_id = State()

    get_new_link = State()
    confirm_new_link = State()


@permission_state
@logger.catch
async def new_link(message: Message, state: FSMContext):
    """
    Получение первого ответа, сохранение ссылки в memory storage.
    """

    async with state.proxy() as data:
        course_id = data['course_id']
        course = Course.get_by_id(pk=course_id)
        data['get_new_link'] = message.text

        await message.answer(
            f'Старая ссылка:\n{course.download_link}\n\n'
            f'Новая ссылка:\n{message.text}'
        )

    await StatesEditLink.next()
    await message.answer('Подтверди изменения',
                         reply_markup=edit_markup(param='link_edit',
                                                  course_id=course_id))


@permission_state
@logger.catch
async def confirm_link(callback: CallbackQuery, state: FSMContext):
    """
    Обновление в БД ссылки на скачивание курса после подтверждения корректности,
    сохранение истории изменений
    """
    async with state.proxy() as data:
        course_id = data['course_id']
        course_new_link = data['get_new_link']

        course = Course.get_by_id(pk=course_id)

        UpdateCourses.create(
            course=course,
            date_of_update=now(),
            admin_of_update=callback.from_user.username,
            update_field='download_link',
            old_value=course.download_link,
            new_value=course_new_link
        )

        course.download_link = course_new_link
        course.save()

    await state.finish()
    await callback.message.answer(f'Ссылка для скачивания <b>{course.course_name}</b> изменена.\n'
                                  'Для просмотра доступных команд нажми /admin',
                                  parse_mode='HTML')
    await callback.answer()


@logger.catch
def register_handlers(disp: Dispatcher):
    """
    Регистратор хэндлеров
    """
    logger.info('register_handlers for state_edit_link')

    disp.register_message_handler(new_link, content_types=['text'], state=StatesEditLink.get_new_link)
    disp.register_callback_query_handler(confirm_link, text='confirm_change',
                                         state=StatesEditLink.confirm_new_link)
