from peewee import *
from loader import BASE_DIR
from datetime import datetime
import os

db_dir = os.path.dirname(__file__)
db_filename = 'database.sqlite3'
db_path = os.path.join(BASE_DIR, db_dir, db_filename)

db = SqliteDatabase(db_path)


def now():
    """
    Вызов текущей даты и времени
    """
    return datetime.now().strftime('%Y.%m.%d_%H:%M:%S')


class BaseModel(Model):
    """
    Базовая модель для дальнейшего наследования.
    """
    class Meta:
        """
        Подключение к БД
        """
        database = db


class User(BaseModel):
    """
    Таблица пользователей бота
    """
    class Meta:
        """
        Установка имени таблицы в БД
        """
        db_table = 'users'

    user_id = IntegerField(unique=True)
    username = CharField(max_length=200, null=True)
    first_name = CharField(max_length=200, null=True)
    first_activity = DateTimeField(default=now())
    last_activity = DateTimeField(default=now())


class Course(BaseModel):
    """
    Таблица доступных курсов
    """
    class Meta:
        """
        Установка имени таблицы в БД
        """
        db_table = 'courses'

    image_id = TextField()
    course_name = CharField(max_length=200)
    description = TextField()
    cost = IntegerField(default=0)
    upload_date = DateTimeField(default=now())
    download_link = TextField()
    archived = BooleanField(default=False)


class UsersToCourses(BaseModel):
    """
    Связь пользователей с приобретенными курсами
    """
    class Meta:
        """
        Установка имени таблицы в БД
        """
        db_table = 'users_to_courses'

    user_id = IntegerField(default=0)
    user = CharField(max_length=200)
    course_id = IntegerField(default=0)
    course = CharField(max_length=200)
    date_of_purchase = DateTimeField(default=now())
    cost = IntegerField(default=0)


class UpdateCourses(BaseModel):
    """
    История редактирования продуктов
    """
    class Meta:
        """
        Установка имени таблицы в БД
        """
        db_table = 'users_update_history'

    course = ForeignKeyField(model=Course)
    date_of_update = DateTimeField(default=now())
    admin_of_update = CharField(max_length=200)
    update_field = CharField(max_length=200)
    old_value = TextField()
    new_value = TextField()


class Buffer(BaseModel):
    """
    Хранение course id, пока клиент оплачивает покупку
    """
    class Meta:
        """
        Установка имени таблицы в БД
        """
        db_table = 'buffer'

    client = IntegerField(unique=True)
    course_id = IntegerField()
