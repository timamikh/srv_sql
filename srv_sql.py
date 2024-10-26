from flask import Flask, request, render_template_string, redirect
import mysql.connector
import os
import time
from mysql.connector import Error

app = Flask(__name__)

# Настройка соединения с базой данных MySQL через переменные окружения
db_config = {
    'user': os.environ.get('DB_USER', 'user'),
    'password': os.environ.get('DB_PASS', 'user'),
    'host': os.environ.get('DB_HOST', 'db'),  # 'db' если используете Docker Compose
    'database': os.environ.get('DB_NAME', 'db_srv_sql'),
    'port': int(os.environ.get('DB_PORT', 3306))
}

# SQL для создания таблицы, если она еще не существует
create_table_sql = """
CREATE TABLE IF NOT EXISTS words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(255) NOT NULL
)
"""

def wait_for_database():
    while True:
        try:
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                break
        except Error as e:
            print("Error while connecting to MySQL", e)
            time.sleep(5)

wait_for_database()

def create_table():
    # Подключение к базе данных и создание таблицы
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()
    cursor.execute(create_table_sql)
    db.commit()
    cursor.close()
    db.close()

create_table()

# Шаблон HTML для отображения формы ввода и результатов
page_template = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Word Input</title>
  </head>
  <body>
    <h1>Введите слова</h1>
    <form method="post">
      <input type="text" name="word" required>
      <button type="submit">Сохранить</button>
    </form>
    <h2>Первые буквы введенных слов:</h2>
    <ul>
      {% for letter in letters %}
      <li>{{ letter }}</li>
      {% endfor %}
    </ul>
  </body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        word = request.form['word']

        # Сохранение слова в базе данных
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        insert_sql = "INSERT INTO words (word) VALUES (%s)"
        cursor.execute(insert_sql, (word,))
        db.commit()
        cursor.close()
        db.close()

        return redirect('/')  # Перенаправляем обратно к форме

    # Извлечение первых букв введенных слов
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()
    select_sql = "SELECT word FROM words"
    cursor.execute(select_sql)
    words = cursor.fetchall()
    cursor.close()
    db.close()

    letters = [word[0][0] for word in words if word[0]]  # Первая буква каждого слова

    return render_template_string(page_template, letters=letters)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)