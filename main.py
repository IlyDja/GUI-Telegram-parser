import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PasswordHashInvalid, PhoneNumberBanned, FloodWait
from datetime import datetime, timedelta
import os
import time

usernames_folder_path = f"{os.getcwd()}\\usernames"


def open_file_and_return_list(path) -> list[str]:
    with open(path, 'r', encoding='utf-8') as file:
        return [line.strip().lower().replace('https://t.me/', '') for line in file.readlines() if line.strip()]


def start_search():
    try:
        links = open_file_and_return_list('links.txt')
    except:
        messagebox.showerror(title="Ошибка", message="В папке с приложением отсутствует файл links.txt")
        return

    try:
        keywords = open_file_and_return_list('keywords.txt')
    except:
        messagebox.showerror(title="Ошибка", message="В папке с приложением отсутствует файл keywords.txt")
        return

    try:
        with open('api_id and api_hash.txt', 'r', encoding='utf-8') as api_datas_file:
            API_ID = int(api_datas_file.readline()[33:])
            API_HASH = api_datas_file.readline(-1)[35:]

        if not start_date_input.get():
            start_date = datetime(2007, 1, 1)
        else:
            start_date: str = start_date_input.get()
            if len(start_date.split('.')[2]) == 2:
                start_date = start_date[:-2] + '20' + start_date.split('.')[-1]
            start_date = datetime.strptime(start_date, "%d.%m.%Y")

        if not end_date_input.get():
            end_date = datetime.today() + timedelta(1)
        else:
            end_date: str = end_date_input.get()
            if len(end_date.split('.')[2]) == 2:
                end_date = end_date[:-2] + '20' + end_date.split('.')[-1]
            end_date = datetime.strptime(end_date, "%d.%m.%Y") + timedelta(1)


        application = Client("my_session", api_id=API_ID, api_hash=API_HASH)
        if 'my_session.session' not in os.listdir(os.getcwd()):
            messagebox.showinfo(title="Добро пожаловать!", message="Внимание! Номер телефона "
                                                                   "нужно ввести в международном формате. "
                                                                   "Например +79207777777")
            result_label.config(text='Подключение...')
            root.update()
            application.connect()
            result_label.config(text='')
            root.update()
            while True:
                user_number = simpledialog.askstring(title="Введите номер телефона", prompt="Ваш номер телефона:")
                sent_code_info = application.send_code(phone_number=user_number)
                phone_code = simpledialog.askstring(title="Введите код подтверждения", prompt="Ваш код:")
                try:
                    application.sign_in(user_number, sent_code_info.phone_code_hash, phone_code)
                    break
                except SessionPasswordNeeded:
                    password = simpledialog.askstring(title="Введите пароль", prompt="Ваш пароль:")
                    try:
                        application.check_password(password)
                        break
                    except PasswordHashInvalid:
                        messagebox.showerror(title="Ошибка", message="Пароль неверный")
                except PhoneCodeInvalid:
                    messagebox.showerror(title="Ошибка", message="Код неверный")
                except PhoneNumberBanned:
                    messagebox.showerror(title="Ошибка", message="Этот номер заблокирован. "
                                                                 "Закройте программу, "
                                                                 "удалите файл my_session.session и "
                                                                 "авторизуйтесь с другим номером телефона")

        usernames = set()

        def find_username_and_add_to_set(app, url):
            messages = app.get_chat_history(url, offset_date=end_date)
            for message in messages:
                if not message.date:
                    continue
                if message.date < start_date:
                    break
                if message.from_user:
                    if message.text:
                        text = message.text
                    elif message.caption:
                        text = message.caption
                    else:
                        continue
                    for keyword in keywords:
                        if keyword in text.lower():
                            if message.from_user.username is not None:
                                usernames.add(message.from_user.username)


        with application as app:
            result_label.config(text='Поиск юзернеймов может занять длительное время. Если система пишет что программа '
                                     'не отвечает - не обращайте внимания. Ждите...')
            root.update()
            while True:
                try:
                    for url in links:
                        find_username_and_add_to_set(app, url)
                        links = links[links.index(url):]
                    else:
                        break
                except FloodWait as e:
                    time.sleep(e.value)

        if usernames:
            curr = datetime.now()  # current date and time
            out_filename = f'usernames {curr.day}-{curr.month}-{curr.year} {curr.hour}h{curr.minute}m{curr.second}s.txt'
            file_path = os.path.join(usernames_folder_path, out_filename)
            with open(file_path, 'w', encoding='utf-8') as usernames_output_file:
                usernames_output_file.write('\n'.join(usernames))
            result_label.config(text=f'Поиск завершён. Юзернеймы сохранены в файл "{out_filename}", '
                                     f'этот файл находится в папке usernames. Папка usernames находится '
                                     f'в папке с этим приложением')
        else:
            result_label.config(text=f'Поиск завершён. Юзернеймы не найдены')

    except Exception as e:
        result_label.config(text=f'Произошла ошибка. Проверьте корректность вводимых данных, '
                                 f'перезапустите программу и попробуйте снова. Если проблема '
                                 f'сохраняется - свяжитесь с разработчиком. Описание ошибки: {e}')


# Создаем главное окно приложения
root = tk.Tk()
root.title("Get usernames from Telegram chats")

# Создаем метку с пояснительным текстом
label = tk.Label(root, text="Файл со ссылками на чаты может содержать неограниченное количество ссылок. "
                            "Каждая ссылка должна располагаться на новой строке. "
                            'Если поиск будет происходить по "супергруппе", должна быть ссылка именно на эту группу, '
                            'а не на её отдельную комнату. '
                            "Положите файл в папку с этим приложением, название должно быть links.txt")
label.config(wraplength=800)
label.pack()  # Размещаем метку в окне

label = tk.Label(root, text="Файл с ключевыми словами/фразами может содержать неограниченное количество ключевых "
                            "слов/фраз. Каждое ключевое слово/фраза на новой строке. "
                            "Положите файл в папку с этим приложением, название должно быть keywords.txt")
label.config(wraplength=800)
label.pack()  # Размещаем метку в окне

label = tk.Label(root, text="Даты нужно вводить в формате день.месяц.год (через точку). Граничные значения включены. "
                            "Если не ввести какую-то из дат, программа возьмёт максимальную границу. Например, если не "
                            "ввести начальную - поиск будет происходить с момента создания чата.")
label.config(wraplength=800)
label.pack()  # Размещаем метку в окне

# Создаем метку с пояснительным текстом
label = tk.Label(root, text="Введите начальную дату:")
label.pack()  # Размещаем метку в окне

# поле ввода начальной даты
start_date_input = tk.Entry(root, width=30)
start_date_input.pack(pady=10)

# Создаем метку с пояснительным текстом
label = tk.Label(root, text="Введите конечную дату:")
label.pack()  # Размещаем метку в окне

# поле ввода конечной даты
end_date_input = tk.Entry(root, width=30)
end_date_input.pack(pady=10)

# Создаем кнопку для старта поиска
start_button = tk.Button(root, text="Начать поиск", command=start_search, fg='red')
start_button.pack(pady=10)

# Создаем метку для вывода результата
result_label = tk.Label(root, text="", font=("Helvetica", 12))
result_label.config(wraplength=800)
result_label.pack(pady=10)

# Запускаем основной цикл приложения
root.mainloop()
