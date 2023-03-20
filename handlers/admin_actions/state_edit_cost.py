from logs.logs_settings import logger
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from utils.decorators import permission_state
from database.db_models import Course, UpdateCourses
from markup.m_admin import edit_markup
from database.func_auto import now


class StatesEditCost(StatesGroup):
    """
    Класс состояний администратора
    для редактирования стоимости курса.
    """
    course_id = State()

    get_new_cost = State()
    confirm_new_cost = State()


@permission_state
@logger.catch
async def new_cost(message: Message, state: FSMContext):
    """
    Получение первого ответа, сохранение цены в memory storage.
    """
    if message.text.isdigit():
        async with state.proxy() as data:
            course_id = data['course_id']
            course = Course.get_by_id(pk=course_id)
            data['get_new_cost'] = int(message.text)

            await message.answer(
                f'Старая цена: {course.cost} рублей\n\n'
                f'Новая цена: {message.text} рублей'
            )

        await StatesEditCost.next()
        await message.answer('Подтверди изменения',
                             reply_markup=edit_markup(param='cost_edit',
                                                      course_id=course_id))
    else:
        logger.warning(f'{message.from_user.username}, некорректно введена стоимость курса')
        await message.reply('Пожалуйста, введи стоимость курса в рублях, целым числом.')
        await StatesEditCost.get_new_cost.set()


@permission_state
@logger.catch
async def confirm_new_cost(callback: CallbackQuery, state: FSMContext):
    """
    Обновление в БД цены после подтверждения корректности,
    сохранение истории изменений
    """
    async with state.proxy() as data:
        course_id = data['course_id']
        course_new_cost = data['get_new_cost']

        course = Course.get_by_id(pk=course_id)

        UpdateCourses.create(
            course=course,
            date_of_update=now(),
            admin_of_update=callback.from_user.username,
            update_field='cost',
            old_value=course.cost,
            new_value=course_new_cost
        )

        course.cost = course_new_cost
        course.save()

    await state.finish()
    await callback.message.answer('Цена изменена.\n'
                                  'Для просмотра доступных команд нажми /admin')
    await callback.answer()


@logger.catch
def register_handlers(disp: Dispatcher):
    """
    Регистратор хэндлеров
    """
    logger.info('register_handlers for state_edit_cost')

    disp.register_message_handler(new_cost, content_types=['text'], state=StatesEditCost.get_new_cost)
    disp.register_callback_query_handler(confirm_new_cost, text='confirm_change',
                                         state=StatesEditCost.confirm_new_cost)
