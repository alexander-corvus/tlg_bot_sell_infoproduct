from logs.logs_settings import logger
from loader import bot
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from utils.decorators import permission_state
from database.db_models import Course, UpdateCourses
from markup.m_admin import edit_markup
from handlers.admin_actions.admin_exist_data import now


class StatesEditImg(StatesGroup):
    """
    Класс состояний администратора
    для редактирования обложки курса.
    """
    course_id = State()

    get_new_img = State()
    confirm_new_img = State()


@permission_state
@logger.catch
async def new_img(message: Message, state: FSMContext):
    """
    Получение первого ответа, сохранение photo_id в memory storage.
    """

    async with state.proxy() as data:
        course_id = data['course_id']
        course = Course.get_by_id(pk=course_id)
        data['get_new_img'] = message.photo[0].file_id

        await bot.send_photo(
            chat_id=message.chat.id,
            photo=course.image_id,
            caption='Старая обложка'
        )

        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=data['get_new_img'],
            caption='Новая обложка'
        )

    await StatesEditImg.next()
    await message.answer('Подтверди изменения',
                         reply_markup=edit_markup(param='img_edit',
                                                        course_id=course_id))


@permission_state
@logger.catch
async def confirm_img(callback: CallbackQuery, state: FSMContext):
    """
    Обновление в БД обложки курса после подтверждения корректности,
    сохранение истории изменений
    """
    async with state.proxy() as data:
        course_id = data['course_id']
        new_img_id = data['get_new_img']

        course = Course.get_by_id(pk=course_id)

        UpdateCourses.create(
            course=course,
            date_of_update=now(),
            admin_of_update=callback.from_user.username,
            update_field='image_id',
            old_value=course.image_id,
            new_value=new_img_id
        )

        course.image_id = new_img_id
        course.save()

    await state.finish()
    await callback.message.answer('Обложка изменена.\n'
                                  'Для просмотра доступных команд нажми /admin')
    await callback.answer()


@logger.catch
def register_handlers(disp: Dispatcher):
    """
    Регистратор хэндлеров
    """
    logger.info('register_handlers for state_edit_image')

    disp.register_message_handler(new_img, content_types=['photo'], state=StatesEditImg.get_new_img)
    disp.register_callback_query_handler(confirm_img, text='confirm_change',
                                         state=StatesEditImg.confirm_new_img)
