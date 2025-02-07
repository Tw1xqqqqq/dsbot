from random import randint
import requests as r
import time

s = r.Session()
s.headers['authorization'] = input('Token: ')
chat_id = input('Input chat id: ')
target_user_id = input('Target user ID: ')  # ID пользователя, на сообщения которого отвечаем
participant = int(input("Choose participant (1 or 2): "))  # Выбор участника
delay_from = int(input("Delay from: "))
delay_to = int(input("Delay to: "))

def load_messages():
    """Загружает сообщения из файла и выбирает строки в зависимости от участника."""
    with open('msg.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]  # Убираем пустые строки
    
    messages = []
    for line in lines:
        if line.startswith("User 1: ") or line.startswith("User 2: "):
            messages.append(line.split(": ", 1)[1])
    
    # Фильтруем сообщения в зависимости от выбора участника
    if participant == 1:
        return messages[::2]  # Берём нечётные (0, 2, 4 → с точки зрения индексации)
    else:
        return messages[1::2]  # Берём чётные (1, 3, 5)

msg_set = load_messages()
msg_index = 0  # Индекс текущего сообщения
total_sent = 0
last_replied_message_id = None  # Запоминаем последнее обработанное сообщение

def get_last_message():
    """Получает последнее сообщение из чата."""
    resp = s.get(f'https://discord.com/api/v9/channels/{chat_id}/messages?limit=1').json()
    if resp and isinstance(resp, list):
        return resp[0]  # Возвращаем последнее сообщение
    return None

while True:
    try:
        last_message = get_last_message()

        if last_message:
            msg_author = last_message.get('author', {}).get('id')
            msg_id = last_message.get('id')

            # Проверяем, от нужного ли пользователя сообщение и не отвечали ли уже на него
            if msg_author == target_user_id and msg_id != last_replied_message_id:
                if not msg_set:
                    print("Повторная загрузка сообщений...")
                    msg_set = load_messages()
                    msg_index = 0  # Обнуляем индекс после перезагрузки

                msg = msg_set[msg_index]  # Берём сообщение по порядку
                msg_index = (msg_index + 1) % len(msg_set)  # Увеличиваем индекс, зацикливаем если нужно

                print(f'Replying to {target_user_id} with message: {msg}')
                _data = {
                    'content': msg,
                    'tts': False,
                    'message_reference': {'message_id': msg_id}  # Ответ на сообщение
                }
                resp = s.post(
                    f'https://discord.com/api/v9/channels/{chat_id}/messages', json=_data
                ).json()

                if resp.get('id'):
                    total_sent += 1
                    last_replied_message_id = msg_id  # Запоминаем, что мы уже ответили на это сообщение
                    print(f'Message sent (Already {total_sent} in total).')

        delay = randint(delay_from, delay_to)  # Генерация случайной задержки в указанном диапазоне
        print(f'Sleeping {delay} seconds...')
        time.sleep(delay)

    except Exception as e:
        print(f'Some error: {e}')
        time.sleep(20)
