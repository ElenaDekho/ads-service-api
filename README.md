# Ads Service API

Сервис объявлений купли/продажи с авторизацией и ролями (user/admin).

## Запуск

docker-compose up --build

API будет доступно по адресу: http://localhost:8000

Документация Swagger: http://localhost:8000/docs

## Переменные окружения

Скопируйте .env.example в .env и заполните:

POSTGRES_USER=postgres 

POSTGRES_PASSWORD=postgres

POSTGRES_DB=ads_db

POSTGRES_HOST=db

POSTGRES_PORT=5432

## Роли

user — управляет только своими объявлениями и своими данными

admin — управляет любыми объявлениями и пользователями

## Эндпоинты

Метод	            Эндпоинт	            Описание

POST	            /user	                  Создать пользователя

GET	              /user/{id}	            Получить пользователя

PATCH	            /user/{id}	            Обновить пользователя

DELETE	          /user/{id}	            Удалить пользователя

POST	            /login	                Авторизация, возвращает токен

POST	            /advertisement	        Создать объявление (требуется токен)

GET	              /advertisement/{id}	    Получить объявление

PATCH	            /advertisement/{id}	    Обновить объявление (требуется токен)

DELETE	          /advertisement/{id}	    Удалить объявление (требуется токен)

GET	              /advertisement	        Поиск объявлений (по title, price_min, price_max)

## Тестирование

python client.py


