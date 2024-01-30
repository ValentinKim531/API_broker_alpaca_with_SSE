# Проект Broker API

Проект предназначен для управления ордерами на акции через REST API, 
предоставляя функционал для создания, получения и удаления ордеров. 
Также в проекте реализована поддержка SSE (Server-Sent Events) для получения 
реальных обновлений.

## Начало работы

Эти инструкции помогут вам запустить копию проекта на вашей локальной машине 
для разработки и тестирования.

### Необходимые условия

- Docker
- Docker Compose

### Запуск проекта

1. Клонируйте репозиторий на вашу локальную машину:

```
git clone https://gitlab.com/Valentin531/broker_api.git
```

2. Перейдите в корневую директорию проекта:

```
cd broker_api
```

3. Переименуйте файл .env.example в .env и добавьте необходимые ключи
для работы приложения:

4. Запустите проект с помощью Docker Compose:

```
docker-compose up --build
```

Эта команда соберет и запустит все необходимые контейнеры.

### Подключение к Swagger UI

После запуска проекта Swagger UI будет доступен по адресу: 

`http://localhost:8000/api/schema/swagger-ui/`

### Выполнение запросов

#### Создание ордера

```
curl -X POST http://localhost:8000/orders/create/ -H 'Content-Type: application/json' -d '{"symbol": "AAPL", "quantity": 10, "order_type": "buy"}'
```


#### Получение списка ордеров

```
curl -X GET http://localhost:8000/orders/
```

#### Отмена ордера

```
curl -X DELETE http://localhost:8000/orders/<order_id>/
```


### Тестирование

Для запуска тестов используйте следующую команду:

```
docker-compose run backend python manage.py test
```


### Проверка кода с помощью Flake8

Для запуска Flake8 выполните следующую команду:

```
docker-compose run backend flake8
```
Это проверит ваш код на соответствие стандартам PEP8.

