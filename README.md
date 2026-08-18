# MatchMe

Дипломный проект — веб-платформа знакомств с REST API.

## Возможности
- Регистрация и JWT-авторизация пользователей (email)
- Профили с фото (одна главная), городом, возрастом, увлечениями, статусом
- Просмотр ленты профилей с фильтрами (пол, возраст, город, статус)
- Случайный профиль с учётом фильтров
- Система лайков и дизлайков
- История просмотренных профилей
- Приглашения на свидание и обмен контактами
- Документация Swagger, CORS, Docker

## Порядок запуска

### Через Docker (рекомендуется)
1. `docker compose up -d --build` — поднимает PostgreSQL и Django
2. `docker compose exec web python manage.py createsuperuser` — создать администратора
3. API: http://localhost:8002/api/ · Swagger: http://localhost:8002/swagger/ · админка: http://localhost:8002/admin/
4. Остановка: `docker compose down` (данные БД сохраняются в томе `pgdata`)

### Локально без Docker
1. `python -m venv venv && venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. Запустить PostgreSQL с БД `matchme_db`, пользователем `matchme_user`/`matchme_pass`
4. `python manage.py migrate`
5. `python manage.py createsuperuser`
6. `python manage.py runserver`

## Тесты
`python manage.py test` — 10 тестов API, лайков, фильтров, удаления фото с диска.

## Кодстайл
Отформатировано с помощью `black` и `isort`.