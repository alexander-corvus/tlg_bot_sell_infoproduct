import os
import zipfile
from logs.logs_settings import logger
from loader import bot, BASE_DIR
from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.decorators import permission
from database.db_models import Course, User, UsersToCourses, UpdateCourses
from database.func_auto import (path_dir_db,
                                create_csv_users,
                                create_csv_history_change,
                                create_csv_buyers,
                                csv_file_name,
                                name_all_users,
                                name_buyers,
                                name_history_change,
                                path_to_db,
                                path_to_db_zip,
                                path_to_log_dir,
                                path_to_logs_zip)


@permission
@logger.catch
async def get_courses(callback: CallbackQuery):
    """
    Получение данных о существующих продуктах.
    """
    courses = Course.select().filter(archived=False)

    if not courses:
        logger.info('обращение к пустой БД Courses')
        await callback.answer('Ни один курс не загружен. Пожалуйста, добавьте продукт.', show_alert=True)
    else:
        for course in courses:
            course_markup = InlineKeyboardMarkup(row_width=1)
            edit = InlineKeyboardButton(text=f'Редактировать {course.course_name}',
                                        callback_data=f'edit_{course.id}')
            arch = InlineKeyboardButton(text=f'Архивировать {course.course_name}',
                                        callback_data=f'archived_{course.id}')
            course_markup.add(edit, arch)

            await callback.answer('Показываю доступные курсы', show_alert=True)
            await bot.send_photo(
                chat_id=callback.from_user.id,
                photo=course.image_id,
                caption=f'<b>Название курса</b>: {course.course_name}\n'
                        f'\n<b>Описание:</b> {course.description}\n'
                        f'\n<b>Цена:</b> {course.cost} руб.\n'
                        f'\n<b>Дата загрузки курса:</b> {course.upload_date}\n'
                        f'\n<b>Ссылка на скачивание:</b> <i>{course.download_link}</i>\n'
                        f'\n\n/admin',
                parse_mode='HTML',
                reply_markup=course_markup
            )
        await callback.answer()


@permission
@logger.catch
async def archived_course(callback: CallbackQuery):
    """
    Обработчик архивирования курса
    """
    course_id = int(callback.data.split('_')[1])
    course = Course.get_by_id(pk=course_id)
    course.archived = True
    course.save()

    await callback.message.answer(f'{course.course_name} архивирован и недоступен для покупки.'
                                  f'\nДля просмотра доступных команд нажми /admin')
    await callback.answer()


@permission
@logger.catch
async def get_archived_courses(callback: CallbackQuery):
    """
    Получение заархивированных продуктов.
    """
    courses = Course.select().filter(archived=True)

    if not courses:
        await callback.answer('В архиве сейчас нет курсов', show_alert=True)
    else:
        for course in courses:
            course_markup = InlineKeyboardMarkup(row_width=1)
            restore = InlineKeyboardButton(text=f'Восстановить {course.course_name}',
                                           callback_data=f'restore_{course.id}')
            delete = InlineKeyboardButton(text=f'Полностью удалить {course.course_name}',
                                          callback_data=f'delete_{course.id}')
            course_markup.add(restore, delete)

            await callback.answer('Показываю курсы в архиве', show_alert=True)
            await bot.send_photo(
                chat_id=callback.from_user.id,
                photo=course.image_id,
                caption=f'<b>Название курса</b>: {course.course_name}\n'
                        f'\n<b>Описание:</b> {course.description}\n'
                        f'\n<b>Цена:</b> {course.cost}\n'
                        f'\n<b>Дата загрузки курса:</b> {course.upload_date}\n'
                        f'\n<b>Ссылка на скачивание:</b> <i>{course.download_link}</i>\n'
                        f'\n\n/admin',
                parse_mode='HTML',
                reply_markup=course_markup
            )
        await callback.answer()


@permission
@logger.catch
async def restore_course(callback: CallbackQuery):
    """
    Обработчик восстановления курса из архива
    """
    course_id = int(callback.data.split('_')[1])
    course = Course.get_by_id(pk=course_id)
    course.archived = False
    course.save()

    await callback.message.answer(f'{course.course_name} '
                                  f'восстановлен из архива и доступен для покупки.\n\n/admin')
    await callback.answer()


@permission
@logger.catch
async def remove_course(callback: CallbackQuery):
    """
    Обработчик полного удаления курса из архива
    """
    course_id = int(callback.data.split('_')[1])
    course = Course.get_by_id(pk=course_id)

    if course.archived:
        confirm_markup = InlineKeyboardMarkup(row_width=2)
        btn_del = InlineKeyboardButton(text='Да, удалить', callback_data=f'full-remove-course_{course.id}')
        btn_no_del = InlineKeyboardButton(text='Не удалять', callback_data='return_admin')
        confirm_markup.add(btn_del, btn_no_del)

        await callback.message.answer(f'{callback.from_user.first_name}, ты правда хочешь удалить'
                                      f'курс {course.course_name}?\n'
                                      f'Восстановить его будет невозможно.',
                                      reply_markup=confirm_markup)
        await callback.answer('ВОССТАНОВИТЬ УДАЛЕННЫЙ ПРОДУКТ НЕВОЗМОЖНО!', show_alert=True)
    else:
        await callback.message.answer(f'Курс {course.course_name} не в архиве.\n'
                                      f'Удалять можно только архивированные курсы\n'
                                      f'Для просмотра доступных команд нажми /admin')
        await callback.answer()


@permission
@logger.catch
async def return_to_admin(callback: CallbackQuery):
    """
    Предлагаем пользователю вернуться в админ-меню
    """
    await callback.message.answer(
        f'Ok, {callback.from_user.first_name}!\nДля просмотра команд администратора нажми /admin\n'
        f'Для возврата в режим клиента нажми /courses'
    )
    await callback.answer()


@permission
@logger.catch
async def full_delete_product(callback: CallbackQuery):
    """
    Обработчик полного удаления продукта
    """
    course_id = int(callback.data.split('_')[1])
    course = Course.get_by_id(pk=course_id)
    course_name = course.course_name

    if course.archived:
        course.delete_instance()

        await callback.message.answer(f'Курс {course_name} удален.\nДля просмотра доступных команд нажми /admin')
        await callback.answer('Удаление успешно')
    else:
        await callback.message.answer(f'Курс {course.course_name} не в архиве.\n'
                                      f'Удалять можно только архивированные курсы\n'
                                      f'Для просмотра доступных команд нажми /admin')
        await callback.answer()


@permission
@logger.catch
async def get_all_users(callback: CallbackQuery):
    """
    Получение всех пользователей бота
    """
    users = User.select()
    name = csv_file_name(difference=name_all_users)

    if users:
        create_csv_users(users=users)
        data_users_path = os.path.join(BASE_DIR, path_dir_db, name)
        await callback.message.answer(f'Количество пользователей бота: {len(users)}.')
        await callback.message.reply_document(open(file=data_users_path,
                                                   mode='rb'))
        os.remove(path=data_users_path)
    else:
        await callback.message.answer('Сейчас ботом никто не пользуется')
    await callback.answer()


@permission
@logger.catch
async def get_buyers(callback: CallbackQuery):
    """
    Получение покупателей
    """
    buyers = UsersToCourses.select()
    name = csv_file_name(difference=name_buyers)

    if buyers:
        create_csv_buyers(buyers=buyers)
        data_buyers_path = os.path.join(BASE_DIR, path_dir_db, name)
        await callback.message.answer(f'Количество продаж: {len(buyers)}.')
        await callback.message.reply_document(open(file=data_buyers_path,
                                                   mode='rb'))
        os.remove(path=data_buyers_path)
    else:
        await callback.message.answer('Продукты еще не покупали.')
    await callback.answer()


@permission
@logger.catch
async def get_history(callback: CallbackQuery):
    """
    Получение истории изменений продуктов
    """
    updates = UpdateCourses.select()
    name = csv_file_name(difference=name_history_change)

    if updates:
        create_csv_history_change(updates=updates)
        data_history_path = os.path.join(BASE_DIR, path_dir_db, name)
        await callback.message.answer(f'Количество внесенных изменений: {len(updates)}.')
        await callback.message.reply_document(open(file=data_history_path,
                                                   mode='rb'))
        os.remove(path=data_history_path)
    else:
        await callback.message.answer('Изменения не вносились в продукты')
    await callback.answer()


@permission
@logger.catch
async def get_db_file(callback: CallbackQuery):
    """
    Выгрузка базы данных zip-архивом
    """
    path = path_to_db_zip()

    if os.path.isfile(path=path_to_db):
        db_zip = zipfile.ZipFile(file=path, mode='w')
        db_zip.write(path_to_db)
        db_zip.close()
        await callback.message.reply_document(open(file=path, mode='rb'))
        os.remove(path=path)
    else:
        await callback.message.answer('База данных отсутствует')
    await callback.answer()


@permission
@logger.catch
async def get_logs_file(callback: CallbackQuery):
    """
    Выгрузка логов
    """
    path = path_to_logs_zip()

    if os.path.isdir(s=path_to_log_dir):
        logs_zip = zipfile.ZipFile(file=path, mode='w')
        for root, dirs, files in os.walk(path_to_log_dir):
            for file in files:
                logs_zip.write(os.path.join(str(root), str(file)))
        logs_zip.close()
        await callback.message.reply_document(open(file=path, mode='rb'))
        os.remove(path=path)
    else:
        await callback.message.answer('Директория для лог-файлов отсутствует.')
    await callback.answer()


@logger.catch
def register_handlers(disp: Dispatcher):
    """
    Регистратор хэндлеров
    """
    logger.info('register_handlers for admin_exist_data')

    disp.register_callback_query_handler(return_to_admin, text='return_admin')
    disp.register_callback_query_handler(get_courses, text='courses_list')
    disp.register_callback_query_handler(archived_course, lambda call: call.data.startswith('archived_'))
    disp.register_callback_query_handler(get_archived_courses, text='all_archived_courses')
    disp.register_callback_query_handler(restore_course, lambda call: call.data.startswith('restore_'))
    disp.register_callback_query_handler(remove_course, lambda call: call.data.startswith('delete_'))
    disp.register_callback_query_handler(full_delete_product, lambda call: call.data.startswith('full-remove-course_'))

    disp.register_callback_query_handler(get_all_users, text='users_data')
    disp.register_callback_query_handler(get_buyers, text='buyers_data')
    disp.register_callback_query_handler(get_history, text='history_data')
    disp.register_callback_query_handler(get_db_file, text='database_file')
    disp.register_callback_query_handler(get_logs_file, text='logs_files')
