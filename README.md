# spa_application
## Використані інструменти:
- контейнеризація: Docker, Docker-compose
- основний фреймвок: Django, DRF
- БД: PostgreSQL (основна), Redis (cache)
- обробка зображень для capcha: Pillow, captcha
- автотестування: Pytest
- документація: Swagger
- адміністрування БД: adminer

## Додаткові пояснення
- Згідно з домовленістю - реалізований тільки БЕ у вигляді RestAPI.
- У зв'язку з необхідністю зберігати деревовидну структуру було використано модель MP_Node з treebeard замість
стандартної Django.models.
- Всі дані зберігаються в реляційній базі PostgreSQL.
- Для зменшення навантаження на систему та БД було впроваджено кешування get запитів.
- Доданий CustomSessionMiddleware який забезпечує створення сесії користувача зразу з першого запиту. Ключі сесій
зберігаються в кеш (Redis). 
- Сесії використовуються для кешування запитів та як унікальний ключ для збереження капчі в кеш (Redis) 
- TTL кешу можна встановити в settings окремо для кожної задачі
- Для полегшеного тестування можна ініціалізувати створення тестових рандомних коментарів за допомогою команди
`python3 manage.py add_comments`.
- Схема БД (model_schema) знаходиться в цій же директорії.

## Запуск проекту 
- git clone https://github.com/kolesnikdi/dZENcode.git
- cd .\dZENcode\spa_application
- Скопіюй .env файл до \dZENcode\spa_application
- docker-compose up --build
- При потребі в рандомних коментарях. Термінал Docker -> spa_application `python3 manage.py add_comments`
- Запуск end-to-end тестів. Термінал Docker -> spa_application `pytest`


## Endpoints
### Список всіх заглавних коментарів
[COMMENTS](http://127.0.0.1:8000/comments) 
- Базова фільтрація LIFO. 
- На кожній сторінці по 25 записів.
### Перегляд коментаря та коментарі до нього
[COMMENT](http://127.0.0.1:8000/comments/1) 
- Каскадне відображення всіх записів.
### Сортування заглавних коментарів
- [ordering=-username](http://127.0.0.1:8000/comments/?page=2&ordering=-username) 
- [ordering=username](http://127.0.0.1:8000/comments/?page=2&ordering=username) 
- [ordering=-email](http://127.0.0.1:8000/comments/?ordering=-email) 
- [ordering=email](http://127.0.0.1:8000/comments/?ordering=email) 
- [ordering=created_date](http://127.0.0.1:8000/comments/?ordering=created_date) 
- [ordering=-created_date](http://127.0.0.1:8000/comments/?ordering=-created_date) 
### Додати коментар
[Коментар](http://127.0.0.1:8000/comments/new) 

[Коментар до коментаря](http://127.0.0.1:8000/comments/1/new) 
- На метод GET повертає зображення капчі як байтовий об'єкт. На метод POST приймає текст в поле captcha. 
- ТTL captcha = 120 сек.. В терміналі буде надруковано <<<<<<captcha_for_manual_test>>>>>>>>Capcha
- Обмеження в 100 кб для тексту реалізоване як обмеження в 102400 символів. Реалізована перевірка тегів в тексті. 
- Дозволені формати зображення: JPG, GIF, PNG. 
- Зображення які більше 320х240 пікселів конвертуються у розмір 320х240.

### Інші посилання 
[swagger](http://127.0.0.1:8000/swagger) Доступно в DEV-режимі.

[adminer](http://127.0.0.1:8082) Логін та Пароль в файлі .env
