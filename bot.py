import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

n = 0
s = 0
a = 0
p = 0

# Включим ведение журнала
logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем константы этапов диалога
NAME, SIZE, ADDRESS, PAY, CONFIRM = range(5)

# функция начального сообщения
def start(update, _):
    update.message.reply_text(
        "Меня зовут Calli'sPizzaBot. У меня вы можете заказать пиццу. \n"
        'Чтобы прекратить заказ, отправьте /cancel.\n\n'
        'Как вас зовут?')
    return NAME

# Обрабатываем имя пользователя
def name(update, _):
  # Список кнопок для ответа
    reply_keyboard = [['большую', 'среднюю', 'маленькую']]
    # Создаем простую клавиатуру для ответа
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    # определяем пользователя
    user = update.message.from_user
    # Пишем в журнал имя пользователя
    logger.info("%s: name: %s", user.first_name, update.message.text)
    #глобальная переменная для хранения ответа
    global n
    n = update.message.text
    update.message.reply_text(
        'Хорошо. Какую вы хотите пиццу? большую, среднюю или маленькую?',
        reply_markup=markup_key,
    )
    # переходим к этапу `SIZE`
    return SIZE

def size(update, _):
    user = update.message.from_user
    logger.info("%s: size: %s", user.first_name, update.message.text)
    global s
    s = update.message.text
    update.message.reply_text(
        'Великолепно! Какой у вас адрес доставки?',
        reply_markup=ReplyKeyboardRemove()
    )
    return ADDRESS

def address(update, _):
    reply_keyboard = [['наличкой', 'безналом', 'безналом при получении']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    user = update.message.from_user
    user_location = update.message.location
    logger.info("%s: address: %s", user.first_name, update.message.text)
    global a
    a = update.message.text
    update.message.reply_text(
        'Как вы будете платить?',
        reply_markup=markup_key,
    )
    return PAY

def pay(update, _):
    reply_keyboard = [['Да', 'Нет']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    user = update.message.from_user
    logger.info("%s: payment: %s", user.first_name, update.message.text)
    p = update.message.text
    update.message.reply_text('{}, вы хотите {} пиццу, оплата – {}, доставить по адресу {}? '.format(n, s, p, a),
      reply_markup=markup_key,
    )
    return CONFIRM


def confirm(update, _):
    user = update.message.from_user
    c = update.message.text
    logger.info("%s: confirm: %s", user.first_name, c)
    if c == 'Да':
      update.message.reply_text('Cool! IСallian пицца будет у вас в ближайшее время! \n \n ' 
        'Для нового заказа отправьте /start \n \n PEACE!',
        reply_markup=ReplyKeyboardRemove()
      )
      pf = open('calli.gif', 'rb')
      update.message.reply_animation(pf)
      pf.close()
    else:
      update.message.reply_text('Заказ отменен :с \nДля оформления нового заказа отправьте /start',
        reply_markup=ReplyKeyboardRemove()
      )
    # Заканчиваем разговор.
    return ConversationHandler.END

# Обрабатываем команду /cancel если пользователь отменил разговор
def cancel(update, _):
    user = update.message.from_user
    logger.info("Пользователь %s отменил заказ.", user.first_name)
    # Отвечаем на отказ поговорить
    update.message.reply_text(
        'Вы отменили оформление заказа \n'
        'Для оформления нового заказа отправьте /start', 
        reply_markup=ReplyKeyboardRemove()
    )
    # Заканчиваем разговор.
    return ConversationHandler.END


if __name__ == '__main__':
    # Создаем Updater и передаем ему токен вашего бота.
    updater = Updater("5305935306:AAFKoiJuhJlM8aHtCzHhlUsDfAOQfBsFFb8")
    # получаем диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Определяем обработчик разговоров `ConversationHandler` 
    # с состояниями NAME, SIZE, ADDRESS, PAY и CONFIRM
    conv_handler = ConversationHandler( # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[CommandHandler('start', start)],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            SIZE: [MessageHandler(Filters.regex('^(большую|среднюю|маленькую)$'), size)],
            ADDRESS: [MessageHandler(Filters.text & ~Filters.command, address)],
            PAY: [MessageHandler(Filters.regex('^(наличкой|безналом|безналом при получении)$'), pay)],
            CONFIRM: [MessageHandler(Filters.regex('^(Да|Нет)$'), confirm)],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Добавляем обработчик разговоров `conv_handler`
    dispatcher.add_handler(conv_handler)

    # Запуск бота
    updater.start_polling()
    updater.idle()