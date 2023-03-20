from logs.logs_settings import logger
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from utils.decorators import permission_state
from database.db_models import Course, UpdateCourses
from markup.m_admin import edit_markup
from database.func_auto import now


class StatesEditName(StatesGroup):
    """
    Класс состояний администратора
    для редактирования названия курса.
    """
    course_id = State()

    get_new_name = State()
    confirm_new_name = State()


@permission_state
@logger.catch
async def new_name(message: Message, state: FSMContext):
    """
    Получение первого ответа, сохранение названия в memory storage.
    """

    async with state.proxy() as data:
        course_id = data['course_id']
        course = Course.get_by_id(pk=course_id)
        data['get_new_name'] = message.text

        await message.answer(
            f'Старое название: {course.course_name}\n\n'
            f'Новое название: {message.text}'
        )

    await StatesEditName.next()
    await message.answer('Подтверди изменения',
                         reply_markup=edit_markup(param='name_edit',
                                                  course_id=course_id))


@permission_state
@logger.catch
async def confirm_name(callback: CallbackQuery, state: FSMContext):
    """
    Обновление в БД названия курса после подтверждения корректности,
    сохранение истории изменений
    """
    async with state.proxy() as data:
        course_id = data['course_id']
        course_new_name = data['get_new_name']

        course = Course.get_by_id(pk=course_id)

        UpdateCourses.create(
            course=course,
            date_of_update=now(),
            admin_of_update=callback.from_user.username,
            update_field='course_name',
            old_value=course.course_name,
            new_value=course_new_name
        )

        course.course_name = course_new_name
        course.save()

    await state.finish()
    await callback.message.answer('Наименование изменено.\n'
                                  'Для просмотра доступных команд нажми /admin')
    await callback.answer()


@logger.catch
def register_handlers(disp: Dispatcher):
    """
    Регистратор хэндлеров
    """
    logger.info('register_handlers for state_edit_name')

    disp.register_message_handler(new_name, content_types=['text'], state=StatesEditName.get_new_name)
    disp.register_callback_query_handler(confirm_name, text='confirm_change',
                                         state=StatesEditName.confirm_new_name)
