# Android Project Backend

## Ссылки на репозитории

- Android приложение: [https://github.com/Emeteil/android-learning](https://github.com/Emeteil/android-learning)
- C++ desktop приложение: [https://github.com/Emeteil/andlean_cpp_frontend](https://github.com/Emeteil/andlean_cpp_frontend)

## Описание

Cерверная часть для мобильного приложения на Android. Изначально сервер был написан на **Flask** по шаблону **flask_template**.

[https://github.com/Emeteil/flask_template](https://github.com/Emeteil/flask_template)

Но после был переписан на **FastAPI** с использованием нового шаблона **fastapi_template**, для повышения производительности, улучшения типизации и документации.

[https://github.com/Emeteil/fastapi_template](https://github.com/Emeteil/fastapi_template)

## Основные возможности

### REST API
- **Маршруты:** Все API эндпоинты сгруппированы в директории `api/`.
- **Валидация:** Строгая проверка входных данных через Pydantic.

### WebSocket
- **Эндпоинт:** `/api/mobile-network/ws`
- **Функционал:** Авторизованные пользователи могут отправлять данные о мобильной сети в реальном времени. Эти данные сохраняются в БД (пока в txt файлы) и мгновенно рассылаются всем подключенным "анонимным" клиентам.

### Авторизация
- **Токены:** Поддержка передачи токена через Cookie (`token`), заголовок `Authorization: Bearer <token>`, параметры запроса или JSON тело.
- **Защита:** Использование зависимостей FastAPI (`Depends`) для контроля доступа к эндпоинтам.
- **Сессии:** Возможность проверки статуса входа (`is_logged`) как для HTTP, так и для WebSocket соединений.

## Документация

Интерактивная документация API: [http://94.159.111.243:5678/docs](http://94.159.111.243:5678/docs)

## Сервер

- Ссылка 1: [http://94.159.111.243:5678](http://94.159.111.243:5678)
- Ссылка 2: [http://friendsshield.duckdns.org:5678](http://friendsshield.duckdns.org:5678)