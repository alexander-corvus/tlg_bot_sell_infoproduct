from database.db_models import *
from logs.logs_settings import logger, logs_dir, log_dir_name
from datetime import datetime
from loader import BASE_DIR
import csv


path_dir_db = os.path.abspath(os.path.dirname(__file__))
path_to_db = os.path.join(path_dir_db, db_filename)
path_to_log_dir = os.path.join(logs_dir, log_dir_name)


def now():
    """
    Вызов текущей даты и времени
    """
    return datetime.now().strftime('%Y.%m.%d_%H:%M:%S')


def csv_file_name(difference: str):
    """
    Формирование названия csv-файла
    """
    name = difference + f'_{now()}.csv'
    return name


name_all_users = 'all_users'
name_buyers = 'buyers'
name_history_change = 'history_change'


def path_to_logs_zip():
    """
    Формирование пути к файлу выгрузки логов
    """
    logs_zip_file = f'logs_{now()}.zip'
    path = os.path.join(logs_dir, logs_zip_file)
    return path


def path_to_db_zip():
    """
    Формирование пути к файлу выгрузки БД
    """
    db_zip_file = f'db_zip_{now()}.zip'
    path = os.path.join(path_dir_db, db_zip_file)
    return path


@logger.catch
def create_tables():
    """
    Создание таблиц в БД
    """
    logger.info('DB connected')

    User.create_table()
    Course.create_table()
    UsersToCourses.create_table()
    UpdateCourses.create_table()
    Buffer.create_table()


@logger.catch
async def user_create(user_id, username, first_name):
    """
    Создание записи в БД о пользователе бота,
    используется с командой /start.
    """
    result = User.get_or_create(user_id=user_id)

    if result[1]:
        logger.info(f'create_user: {user_id}, {username}, {first_name}')
        user = User.get(user_id=user_id)
        user.username = username
        user.first_name = first_name
        user.save()
    else:
        logger.info(f'user {user_id} created earlier')


@logger.catch
def user_last_activity(user_id):
    """
    Обновление значения последней активности пользователя
    """
    user = User.get_or_none(user_id=user_id)
    if user:
        logger.info(f'update last_activity for {user_id}')
        user.last_activity = now()
        user.save()
    else:
        logger.error(f'{user_id}, user_last_activity, последняя активность для пользователя не из БД')


@logger.catch
def user_history_purchases(user_id, course_id):
    """
    Сохранение истории покупок в БД
    """
    user = User.get_or_none(user_id=user_id)
    course = Course.get_or_none(course_id)

    if user:
        if course:
            logger.info(f'user_history_purchases for {user_id}')
            UsersToCourses.create(
                user_id=user_id,
                user=user.first_name,
                course_id=course_id,
                course=course.course_name,
                date_of_purchase=now(),
                cost=course.cost
            )
        else:
            logger.error(f'клиент: {user_id}, курс: {course_id} покупка курса не из БД, user_history_purchases')
    else:
        logger.error(f'клиент: {user_id}, курс: {course_id} покупка курса пользователем не из БД')


@logger.catch
def create_csv_users(users):
    """
    Создание csv-файла со всеми пользователями бота
    """
    csv_file_path = os.path.join(BASE_DIR, path_dir_db, csv_file_name(difference=name_all_users))

    with open(file=csv_file_path, mode='w') as csvfile:
        titles = 'user_id|username|first_name|first_activity|last_activity'.split(sep='|')
        writer = csv.writer(csvfile,
                            dialect='excel',
                            delimiter='|',
                            quotechar='"')
        writer.writerow(titles)

        for user in users:
            users_str = f'{user.user_id}|' \
                        f'{user.username}|' \
                        f'{user.first_name}|' \
                        f'{user.first_activity}|' \
                        f'{user.last_activity}'.split(sep='|')
            writer.writerow(users_str)


@logger.catch
def create_csv_history_change(updates):
    """
    Создание csv-файла с историей изменений продукта
    """
    csv_file_path = os.path.join(BASE_DIR, path_dir_db, csv_file_name(difference=name_history_change))

    with open(file=csv_file_path, mode='w') as csvfile:
        titles = 'course_name|date_of_update|admin_of_update|update_field|old_value|new_value'.split(sep='|')
        writer = csv.writer(csvfile,
                            dialect='excel',
                            delimiter='|',
                            quotechar='"')
        writer.writerow(titles)

        for row in updates:
            update_str = f'{row.course.course_name}|' \
                         f'{row.date_of_update}|' \
                         f'{row.admin_of_update}|' \
                         f'{row.update_field}|' \
                         f'{row.old_value}|' \
                         f'{row.new_value}'.split(sep='|')
            writer.writerow(update_str)


@logger.catch
def create_csv_buyers(buyers):
    """
    Создание csv-файла с покупателями продуктов
    """
    csv_file_path = os.path.join(BASE_DIR, path_dir_db, csv_file_name(difference=name_buyers))

    with open(file=csv_file_path, mode='w') as csvfile:
        titles = 'user|course|date_of_purchase|cost'.split(sep='|')
        writer = csv.writer(csvfile,
                            dialect='excel',
                            delimiter='|',
                            quotechar='"')
        writer.writerow(titles)

        for data_row in buyers:
            buyers_str = f'{data_row.user}|' \
                        f'{data_row.course}|' \
                        f'{data_row.date_of_purchase}|' \
                        f'{data_row.cost}'.split(sep='|')
            writer.writerow(buyers_str)
