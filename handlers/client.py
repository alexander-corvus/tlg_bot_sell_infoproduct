import emoji
import peewee
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from loader import bot, YOOKASSA_TOKEN
from logs.logs_settings import logger
from markup.m_client import available_courses, buy_course
from database.db_models import Course, Buffer, UsersToCourses
from database.func_auto import user_create, user_last_activity, user_history_purchases
from aiogram.types import (Message,
                           BotCommand,
                           BotCommandScopeDefault,
                           CallbackQuery,
                           PreCheckoutQuery,
                           ContentType)

DEFAULT_COMMANDS = (
    ('help', 'Подсказка'),
    ('courses', 'Доступные курсы')
)

GREETINGS = 'Привет, {first_name}! {smile}\n' \
            '\nС удовольствием расскажу тебе, как всегда оставаться неотразимой{hug}'

PAYLOAD = 'beauty_course_{course_id}'
START_PARAMETER = 'start_parameter_{course_id}'


@logger.catch
async def set_commands(my_bot: Bot) -> None:
    """
    Функция, устанавливающая команды по умолчанию, которые выводятся в качестве подсказки пользователю.
    """
    logger.info('set_commands')

    commands = [
        BotCommand(command=name, description=description) for name, description in DEFAULT_COMMANDS
    ]

    await my_bot.set_my_commands(commands, BotCommandScopeDefault())


@logger.catch
async def command_start(message: Message):
    """
    Обработчик команды "start".
    Установка доступных команд для бота,
    внесение пользователя в БД.
    """
    logger.info(f'{message.from_user.id}, {message.from_user.username}, command_start')
    await user_create(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    await set_commands(my_bot=bot)

    await bot.send_message(
        message.from_user.id,
        GREETINGS.format(first_name=message.from_user.first_name,
                         smile=emoji.emojize(':smiling_face_with_smiling_eyes:'),
                         hug=emoji.emojize(':smiling_face_with_open_hands:')),
        reply_markup=available_courses
    )


@logger.catch
async def command_help(message: Message):
    """
    Обработчик команды "help".
    Проверка, не было ли попыток купить продукт ранее.
    """
    logger.info(f'{message.from_user.id}, {message.from_user.username}, command_help')
    await user_create(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    user_last_activity(user_id=message.from_user.id)

    buffer = Buffer.get_or_none(client=message.from_user.id)
    if buffer:
        buffer.delete_instance()

    def_commands = [f'/{command} - {description}' for command, description in DEFAULT_COMMANDS]
    await bot.send_message(message.from_user.id,
                           '\n'.join(def_commands),
                           reply_markup=available_courses)


@logger.catch
async def show_courses_callback(callback: CallbackQuery):
    """
    Показываем клиенту доступные курсы (callback)
    """
    logger.info(f'{callback.from_user.id}, {callback.from_user.username}, show_courses')
    await user_create(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name
    )
    user_last_activity(user_id=callback.from_user.id)
    courses = Course.select().filter(archived=False)

    if not courses:
        logger.warning('обращение клиента к пустой БД Courses')
        await callback.message.answer('Сейчас я делаю свои продукты лучше.\n'
                                      'Зайди чуть позже - все будет готово!')
    else:
        await callback.message.answer(f'Смотри, что у меня для тебя есть! '
                                      f'{emoji.emojize(":smiling_cat_with_heart-eyes:")}')
        for course in courses:
            await bot.send_photo(
                chat_id=callback.from_user.id,
                photo=course.image_id,
                caption=f'<b>Название курса</b>: {course.course_name}\n'
                        f'\n<b>Описание:</b> {course.description}\n'
                        f'\n<b>Цена:</b> {course.cost} руб.\n',
                parse_mode='HTML',
                reply_markup=buy_course(cost=course.cost, course_id=course.id)
            )
    await callback.answer()


@logger.catch
async def show_courses_command(message: Message):
    """
    Показываем клиенту доступные курсы (command)
    """
    logger.info(f'{message.from_user.id}, {message.from_user.username}, show_courses_command')
    await user_create(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    user_last_activity(user_id=message.from_user.id)

    courses = Course.select().filter(archived=False)

    if not courses:
        logger.warning('обращение клиента к пустой БД Courses')
        await message.answer('Сейчас я делаю свои продукты лучше.\n'
                             'Зайди чуть позже - все будет готово!')
    else:
        await message.answer(f'Смотри, что у меня для тебя есть! {emoji.emojize(":smiling_face_with_heart-eyes:")}')
        for course in courses:
            await bot.send_photo(
                chat_id=message.from_user.id,
                photo=course.image_id,
                caption=f'<b>Название курса</b>: {course.course_name}\n'
                        f'\n<b>Описание:</b> {course.description}\n'
                        f'\n<b>Цена:</b> {course.cost} руб.\n',
                parse_mode='HTML',
                reply_markup=buy_course(cost=course.cost, course_id=course.id)
            )


@logger.catch
async def callback_buy(callback: CallbackQuery):
    """
    Обработчик покупки из callback. Проверка, не куплен ли ранее данный продукт.
    """
    logger.info(f'{callback.from_user.id}, {callback.from_user.username}, callback_buy')
    user_last_activity(user_id=callback.from_user.id)

    course_id = int(callback.data.split('_')[-1])
    course = Course.get_by_id(pk=course_id)

    existing_purchase = UsersToCourses.select().where(
        UsersToCourses.user_id == callback.from_user.id, UsersToCourses.course_id == course_id
    )

    if not existing_purchase:
        cost_for_yookassa = int(str(course.cost) + '00')

        try:
            Buffer.create(client=callback.from_user.id,
                          course_id=course_id)
        except peewee.IntegrityError as ex_name:
            logger.error(f'{callback.from_user.id}, exception: {ex_name}, callback_buy, '
                         f'попытка новой покупки, не завершив предыдущую')
            await callback.message.answer('Кажется, ты что-то хотела купить, но не вышло.\n'
                                          'Пожалуйста, нажми /help и попробуй заново.')
        else:
            await callback.message.answer('Прекрасный выбор!')
            await callback.answer()

            await bot.send_invoice(
                chat_id=callback.from_user.id,
                title=course.course_name,
                description=course.description,
                payload=PAYLOAD.format(course_id=course_id),
                provider_token=YOOKASSA_TOKEN,
                currency='RUB',
                start_parameter=START_PARAMETER.format(course_id=course_id),
                prices=[{'label': 'Руб', 'amount': cost_for_yookassa}]
            )
    else:
        logger.info(f'{callback.from_user.id}, {callback.from_user.username}, попытка купить ранее приобретенный курс')
        await callback.message.answer(f'У тебя уже есть доступ к этому курсу! '
                                      f'{emoji.emojize(":smiling_face_with_smiling_eyes:")}\n'
                                      f'Напоминаю ссылку: {course.download_link}',
                                      reply_markup=available_courses)
        await callback.answer()


@logger.catch
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    """
    Подтверждение наличия заказа, ответ для платежной системы.
    """
    logger.info(f'{pre_checkout_query.from_user.id},'
                f'{pre_checkout_query.from_user.username},'
                f'process_pre_checkout_query')
    await bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id, ok=True)


@logger.catch
async def process_pay(message: Message):
    """
    Прием ответа от платежной системы с подтверждением оплаты,
    сохранение истории покупок, удаление буфера.
    """
    buffer = Buffer.get_or_none(client=message.from_user.id)
    link = Course.get_by_id(pk=buffer.course_id).download_link

    if buffer:
        if message.successful_payment.invoice_payload == PAYLOAD.format(course_id=buffer.course_id):
            await bot.send_message(
                chat_id=message.from_user.id,
                text=f'Поздравляю с прекрасным приобретением, {message.from_user.first_name}! '
                     f'{emoji.emojize(":red_heart:")}\n'
                     f'Ссылка на скачивание курса: {link}',
                disable_web_page_preview=True
            )
            user_history_purchases(user_id=buffer.client, course_id=buffer.course_id)
            buffer.delete_instance()
            user_last_activity(user_id=message.from_user.id)
        else:
            logger.error(f'{message.from_user.id}, process_pay, ошибка совпадения payload.')
            await bot.send_message(message.from_user.id, 'Платеж не прошел. Пожалуйста, проверьте данные.')
    else:
        logger.error(f'{message.from_user.id}, process_pay, ошибка получения буфера.')
        await bot.send_message(message.from_user.id, 'Платеж не прошел. Пожалуйста, проверьте данные.')


@logger.catch
def register_handlers(disp: Dispatcher):
    """
    Регистратор хэндлеров
    """
    logger.info('register_handlers for client')

    disp.register_message_handler(command_start, commands=['start'])
    disp.register_message_handler(command_help, commands=['help'])
    disp.register_callback_query_handler(show_courses_callback, text='available_products')
    disp.register_message_handler(show_courses_command, commands=['courses'])
    disp.register_callback_query_handler(callback_buy, lambda call: call.data.startswith('callback_buy_'))

    disp.register_pre_checkout_query_handler(process_pre_checkout_query)
    disp.register_message_handler(process_pay, content_types=ContentType.SUCCESSFUL_PAYMENT)

    disp.register_message_handler(command_help)
