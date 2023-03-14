from logs.logs_settings import logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import emoji

emoji_no = emoji.emojize(':cross_mark:')

admin_start_kb = InlineKeyboardMarkup(row_width=1)
button_1 = InlineKeyboardButton(text='Добавить курс', callback_data='add_course')
button_2 = InlineKeyboardButton(text='Доступные курсы', callback_data='courses_list')
button_3 = InlineKeyboardButton(text='Курсы в архиве', callback_data='all_archived_courses')
button_4 = InlineKeyboardButton(text='Пользователи (выгрузка csv)', callback_data='users_data')
button_5 = InlineKeyboardButton(text='Покупатели (выгрузка csv)', callback_data='buyers_data')
button_6 = InlineKeyboardButton(text='История изменений курсов (выгрузка csv)', callback_data='history_data')
button_7 = InlineKeyboardButton(text='DB file', callback_data='database_file')
button_8 = InlineKeyboardButton(text='Logs zip', callback_data='logs_files')
button_9 = InlineKeyboardButton(text=f'{emoji_no} Выход', callback_data='return_admin')
admin_start_kb.add(
    button_1, button_2, button_3, button_4, button_5, button_6
).row(
    button_7, button_8
).row(
    button_9
)

create_course_checkup = InlineKeyboardMarkup(row_width=1)
button_create = InlineKeyboardButton(text='Загрузить курс', callback_data="download_course")
button_cancel = InlineKeyboardButton(text='Отмена', callback_data="cancel")
create_course_checkup.add(button_create, button_cancel)

cancel_kb = InlineKeyboardMarkup(row_width=1)
cancel_kb.add(button_cancel)


@logger.catch
def create_edit_markup(course_id):
    """
    Клавиатура для редактирования курса
    """

    edit_course_kb = InlineKeyboardMarkup(row_width=2)

    btn_image = InlineKeyboardButton(text='Обложка', callback_data=f'img_edit_{course_id}')
    btn_name = InlineKeyboardButton(text='Название', callback_data=f'name_edit_{course_id}')
    btn_descr = InlineKeyboardButton(text='Описание', callback_data=f'descr_edit_{course_id}')
    btn_cost = InlineKeyboardButton(text='Цена', callback_data=f'cost_edit_{course_id}')
    btn_link = InlineKeyboardButton(text='Ссылка на скачивание', callback_data=f'link_edit_{course_id}')
    btn_cancel = InlineKeyboardButton(text=f'{emoji_no} Отмена редактирования {emoji_no}',
                                      callback_data='no_edit_course')

    edit_course_kb.add(btn_image, btn_name, btn_descr, btn_cost).row(btn_link).row(btn_cancel)

    return edit_course_kb


@logger.catch
def edit_markup(param, course_id):
    """
    Клавиатура для обработки нового значения данных курса
    """
    markup = InlineKeyboardMarkup(row_width=2)

    change_conf = InlineKeyboardButton(text='Принять', callback_data='confirm_change')
    change_cancel = InlineKeyboardButton(text='Загрузить заново', callback_data=f'{param}_{course_id}')
    cancel = InlineKeyboardButton(text='Выход из редактора', callback_data='exit_edit')

    markup.add(change_conf, change_cancel).row(cancel)

    return markup
