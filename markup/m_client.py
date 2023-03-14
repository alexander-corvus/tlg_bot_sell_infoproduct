from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

available_courses = InlineKeyboardMarkup(row_width=1)
btn_courses = InlineKeyboardButton(text='Обзор продуктов', callback_data='available_products')
available_courses.add(btn_courses)


def buy_course(cost, course_id):
    """
    Кнопка для покупки курса, необходим course id
    """
    buy_course_markup = InlineKeyboardMarkup(row_width=1)
    button_buy = InlineKeyboardButton(text=f'Купить курс за {cost} руб.', callback_data=f'callback_buy_{course_id}')
    buy_course_markup.add(button_buy)

    return buy_course_markup

