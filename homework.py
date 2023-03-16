import os
import logging
import time

import requests

from dotenv import load_dotenv
import telegram

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s'
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    else:
        logging.critical('Отсутствует одна из переменных окружения.')
        return False


def send_message(bot, message):
    """Отправляет сообщение о состоянии работы в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(f'Сообщение -{message}- успешно отправлено.')
    except Exception:
        logging.error('Ошибка работы с ботом.')


def get_api_answer(timestamp):
    """Отправляет запрос к API Яндекс.Практикума.
    Возвращает данные о последней домашней работе.
    """
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        logging.debug(response)
    except requests.RequestException:
        logging.error('С ответом от сервера что-то не так.')
        return None
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logging.error('Status code ответа не 200')
        return None
    response = check_response(response.json())
    return response


def check_response(response):
    """Проверяет соответствие ответа документации Яндекс.Практикума."""
    if type(response) == dict and type(response.get('homeworks')) == list:
        if type(response['homeworks']) == list:
            return response
        else:
            logging.critical('Тип данных ответа от API '
                             'не соответствует ожидаемому.')
            raise TypeError
    else:
        logging.critical('Тип данных ответа от API '
                         'не соответствует ожидаемому.')
        raise TypeError


def parse_status(homework):
    """Получает на вход данные о последней домашней работе.
    Возвращает статус работы.
    """
    if homework_name := homework.get('homework_name'):
        if verdict := HOMEWORK_VERDICTS.get(homework['status']):
            return f'Изменился статус проверки работы ' \
                   f'"{homework_name}". {verdict}'
        else:
            logging.error('В домашке нет названия работы.')
            raise Exception('В домашке нет названия работы.')
    else:
        logging.error('В домашке нет названия работы.')
        raise Exception('В домашке нет названия работы.')


def main():
    """Основная логика работы бота."""
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        timestamp = int(time.time())
    else:
        return print('Недоступна одна из переменных окружения.')
    while True:
        try:
            if api_answer := get_api_answer(timestamp).get('homeworks')[0]:
                message = parse_status(api_answer)
                send_message(bot, message)
                timestamp = int(time.time())
            time.sleep(RETRY_PERIOD)
        except IndexError:
            print('Ничего нового')
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            logging.critical(error)
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            break


if __name__ == '__main__':
    main()
