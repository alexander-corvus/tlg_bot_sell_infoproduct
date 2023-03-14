from logs.logs_settings import logger
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from markup.m_admin import create_edit_markup, cancel_kb
from utils.decorators import permission, permission_state
from database.db_models import Course
from handlers.admin_actions import (state_edit_image,
                                    state_edit_name,
                                    state_edit_descr,
                                    state_edit_cost,
                                    state_edit_link)


@permission
@logger.catch
async def edit_course(callback: CallbackQuery):
    """
    Вход в меню редактирования курса
    """

    course_id = int(callback.data.split('_')[-1])
    course = Course.get_by_id(pk=course_id)

    await callback.message.answer(
        f'Что именно ты хочешь изменить в <b>{course.course_name}</b>?', parse_mode='HTML',
        reply_markup=create_edit_markup(course_id=course_id)
    )
    await callback.answer()


@permission
@logger.catch
async def edit_course_cancellation(callback: CallbackQuery):
    """
    Выход из меню редактирования курса
    """
    await callback.message.delete()
    await callback.answer()


@permission_state
@logger.catch
async def end_edit(callback: CallbackQuery, state: FSMContext):
    """
    Выход из логики редактирования параметра курса
    """
    current_state = await state.get_state()

    if current_state is None:
        return

    logger.info(f'state before cancelled: {current_state}')

    await state.finish()
    await callback.message.answer(f'Редактирование отменено.\n'
                                  f'Введи <i>/admin</i> для просмотра команд админки',
                                  parse_mode='HTML')
    await callback.answer()


@permission_state
@logger.catch
async def edit_image(callback: CallbackQuery, state: FSMContext):
    """
    Изменение обложки курса
    """
    course_id = int(callback.data.split('_')[-1])
    course = Course.get_by_id(pk=course_id)

    async with state.proxy() as data:
        data['course_id'] = course_id

    await state_edit_image.StatesEditImg.get_new_img.set()
    await callback.message.answer(f'Загрузи новую обложку для курса <b>{course.course_name}</b>',
                                  parse_mode='HTML',
                                  reply_markup=cancel_kb)
    await callback.answer()


@permission_state
@logger.catch
async def edit_name(callback: CallbackQuery, state: FSMContext):
    """
    Изменение наименования курса
    """
    course_id = int(callback.data.split('_')[-1])
    course = Course.get_by_id(pk=course_id)

    async with state.proxy() as data:
        data['course_id'] = course_id

    await state_edit_name.StatesEditName.get_new_name.set()
    await callback.message.answer(f'Введи новое название для курса <b>{course.course_name}</b>',
                                  parse_mode='HTML',
                                  reply_markup=cancel_kb)
    await callback.answer()


@permission_state
@logger.catch
async def edit_description(callback: CallbackQuery, state: FSMContext):
    """
    Изменение описания курса
    """
    course_id = int(callback.data.split('_')[-1])
    course = Course.get_by_id(pk=course_id)

    async with state.proxy() as data:
        data['course_id'] = course_id

    await state_edit_descr.StatesEditDescr.get_new_descr.set()
    await callback.message.answer(f'Введи новое описание для курса <b>{course.course_name}</b>',
                                  parse_mode='HTML',
                                  reply_markup=cancel_kb)
    await callback.answer()


@permission_state
@logger.catch
async def edit_cost(callback: CallbackQuery, state: FSMContext):
    """
    Изменение стоимости курса
    """
    course_id = int(callback.data.split('_')[-1])
    course = Course.get_by_id(pk=course_id)

    async with state.proxy() as data:
        data['course_id'] = course_id

    await state_edit_cost.StatesEditCost.get_new_cost.set()
    await callback.message.answer(f'Введи новую стоимость для курса <b>{course.course_name}</b>',
                                  parse_mode='HTML',
                                  reply_markup=cancel_kb)
    await callback.answer()


@permission_state
@logger.catch
async def edit_link(callback: CallbackQuery, state: FSMContext):
    """
    Изменение ссылки на скачивание курса
    """
    course_id = int(callback.data.split('_')[-1])
    course = Course.get_by_id(pk=course_id)

    async with state.proxy() as data:
        data['course_id'] = course_id

    await state_edit_link.StatesEditLink.get_new_link.set()
    await callback.message.answer(f'Введи новую ссылку для скачивания курса <b>{course.course_name}</b>',
                                  parse_mode='HTML',
                                  reply_markup=cancel_kb)
    await callback.answer()


@logger.catch
def register_handlers(disp: Dispatcher):
    """
    Регистратор хэндлеров
    """
    logger.info('register_handlers for admin_edit_course')

    disp.register_callback_query_handler(edit_course, lambda call: call.data.startswith(f'edit_'))
    disp.register_callback_query_handler(edit_course_cancellation, text='no_edit_course')
    disp.register_callback_query_handler(end_edit, text='exit_edit', state='*')
    disp.register_callback_query_handler(edit_image, lambda call: call.data.startswith('img_edit_'), state='*')
    disp.register_callback_query_handler(edit_name, lambda call: call.data.startswith('name_edit_'), state='*')
    disp.register_callback_query_handler(edit_description, lambda call: call.data.startswith('descr_edit_'), state='*')
    disp.register_callback_query_handler(edit_cost, lambda call: call.data.startswith('cost_edit_'), state='*')
    disp.register_callback_query_handler(edit_link, lambda call: call.data.startswith('link_edit_'), state='*')

    state_edit_image.register_handlers(disp=disp)
    state_edit_name.register_handlers(disp=disp)
    state_edit_descr.register_handlers(disp=disp)
    state_edit_cost.register_handlers(disp=disp)
    state_edit_link.register_handlers(disp=disp)
