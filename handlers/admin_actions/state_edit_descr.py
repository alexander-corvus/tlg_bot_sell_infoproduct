from logs.logs_settings import logger
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from utils.decorators import permission_state
from database.db_models import Course, UpdateCourses
from markup.m_admin import edit_markup
from handlers.admin_actions.admin_exist_data import now


class StatesEditDescr(StatesGroup):
    """
    Класс состояний администратора
    для редактирования описания курса.
    """
    course_id = State()

    get_new_descr = State()
    confirm_new_descr = State()


@permission_state
@logger.catch
async def new_descr(message: Message, state: FSMContext):
    """
    Получение первого ответа, сохранение описания в memory storage.
    """

    async with state.proxy() as data:
        course_id = data['course_id']
        course = Course.get_by_id(pk=course_id)
        data['get_new_descr'] = message.text

        await message.answer(
            f'<i>Старое описание</i>:\n{course.description}\n\n'
            f'<i>Новое описание:</i>\n{message.text}',
            parse_mode='HTML'
        )

    await StatesEditDescr.next()
    await message.answer('Подтверди изменения',
                         reply_markup=edit_markup(param='descr_edit',
                                                  course_id=course_id))


@permission_state
@logger.catch
async def confirm_new_descr(callback: CallbackQuery, state: FSMContext):
    """
    Обновление в БД описания курса после подтверждения корректности,
    сохранение истории изменений
    """
    async with state.proxy() as data:
        course_id = data['course_id']
        course_new_descr = data['get_new_descr']

        course = Course.get_by_id(pk=course_id)

        UpdateCourses.create(
            course=course,
            date_of_update=now(),
            admin_of_update=callback.from_user.username,
            update_field='description',
            old_value=course.description,
            new_value=course_new_descr
        )

        course.description = course_new_descr
        course.save()

    await state.finish()
    await callback.message.answer('Описание изменено.\n'
                                  'Для просмотра доступных команд нажми /admin')
    await callback.answer()


@logger.catch
def register_handlers(disp: Dispatcher):
    """
    Регистратор хэндлеров
    """
    logger.info('register_handlers for state_edit_descr')

    disp.register_message_handler(new_descr, content_types=['text'], state=StatesEditDescr.get_new_descr)
    disp.register_callback_query_handler(confirm_new_descr, text='confirm_change',
                                         state=StatesEditDescr.confirm_new_descr)
