# Custom Auth & RBAC

Мини-бэкенд на **FastAPI + SQLAlchemy (SQLite)** с **собственной аутентификацией** (opaque session tokens, хранение в БД) и **системой разграничения прав (RBAC)**.  
Не использует «из коробки» аутентификацию фреймворка. Реализованы: регистрация, вход/выход, обновление профиля, «мягкое» удаление, идентификация по токену, проверки доступа, 401/403, админ-API управления ролями/правами/ресурсами, а также мок-эндпоинты «бизнес-объектов».

## Содержание

- [Архитектура и модели доступа (RBAC)](#архитектура-и-модели-доступа-rbac)
- [Схема БД](#схема-бд)
- [Алгоритмы аутентификации и авторизации](#алгоритмы-аутентификации-и-авторизации)
- [API: пользовательские операции](#api-пользовательские-операции)
- [API: администрирование RBAC](#api-администрирование-rbac)
- [Моки «бизнес-объектов»](#моки-бизнесобъектов)
- [Установка и запуск (локально)](#установка-и-запуск-локально)
- [Запуск в Docker](#запуск-в-docker)
- [e2e-тест](#e2e-тест)
- [Примеры запросов](#примеры-запросов)
- [Ошибки и коды статусов](#ошибки-и-коды-статусов)
- [Расширение и дальнейшие шаги](#расширение-и-дальнейшие-шаги)
- [Структура проекта](#структура-проекта)

---

## Архитектура и модели доступа (RBAC)

Модель доступа — **RBAC (Role-Based Access Control)**:

- **Пользователь** имеет набор **ролей** (многие-ко-многим).
- **Роль** имеет набор **прав** (многие-ко-многим).
- **Право (permission)** = пара **{resource, action}**.
  - `resource` — логическое имя области (например, `project`, `report`, `access_control`).
  - `action` — операция над ресурсом (`read`, `create`, `update`, `delete`, `manage` и пр.).

Проверка доступа: у текущего пользователя должна существовать роль, которой назначено право с требуемыми `resource` и `action`.  
Если пользователь не идентифицирован — **401**. Идентифицирован, но права нет — **403**.

### Почему не JWT?

JWT удобен, но «ре-вокация» и мгновенная блокировка доступа при деактивации/удалении пользователя требует дополнительной инфраструктуры. В учебной задаче удобнее **opaque-токены**, хранящиеся в таблице `sessions`: можно инвалидавать токен и сразу лишить доступа.

---

## Схема БД

Используется **SQLite** (по умолчанию), SQLAlchemy 2.x.

### Таблицы

- `users`
  - `id` INT PK
  - `first_name`, `last_name`, `patronymic` TEXT
  - `email` TEXT UNIQUE
  - `password_hash` TEXT (bcrypt)
  - `is_active` BOOL (мягкое удаление = `False`)
  - `created_at` DATETIME (UTC, naive)

- `sessions`
  - `id` INT PK
  - `user_id` FK → users.id
  - `token` TEXT UNIQUE (opaque: `uuid4`.`hex`)
  - `created_at` DATETIME (UTC)
  - `expires_at` DATETIME (UTC)
  - `is_active` BOOL

- `resources`
  - `id` INT PK
  - `code` TEXT UNIQUE (напр. `project`, `report`, `access_control`)

- `permissions`
  - `id` INT PK
  - `resource_id` FK → resources.id
  - `action` TEXT (напр. `read`, `create`, `manage`)
  - `UNIQUE(resource_id, action)`

- `roles`
  - `id` INT PK
  - `name` TEXT UNIQUE (напр. `admin`, `manager`)

- `role_permissions` (многие-ко-многим)
  - `id` INT PK
  - `role_id` FK → roles.id
  - `permission_id` FK → permissions.id
  - `UNIQUE(role_id, permission_id)`

- `user_roles` (многие-ко-многим)
  - `id` INT PK
  - `user_id` FK → users.id
  - `role_id` FK → roles.id
  - `UNIQUE(user_id, role_id)`

### ER-диаграмма (ASCII)

```
users 1---* sessions

users *---* roles        via user_roles
roles *---* permissions  via role_permissions
permissions *---1 resources
```

### Сидинг (при старте)

- Создаётся ресурс `access_control` и право `manage` на него.
- Создаётся роль `admin` и к ней привязывается `access_control:manage`.
- Создаётся пользователь-админ:
  - email: `admin@example.com`
  - пароль: `admin123`
  - роль: `admin`

Админ-аккаунт и параметры настраиваются через переменные окружения.

---

## Алгоритмы аутентификации и авторизации

- **Регистрация**: запись в `users` с хешем пароля (bcrypt).
- **Вход**: по `email + password`. Если ок — создаётся запись в `sessions` с `token` и `expires_at`.  
  Клиент передаёт токен в заголовке: `Authorization: Bearer <token>`.
- **Идентификация**: по токену из `sessions` (`is_active == True` и не истёк).
- **Выход**: текущая сессия помечается `is_active=False`.
- **Мягкое удаление**: `users.is_active=False`, все активные сессии пользователя инвалидируются.
- **Авторизация (RBAC)**: декоратор `require_permission(resource, action)` проверяет, есть ли у пользователя соответствующее право.

Время хранится в **naive UTC** (через `datetime.utcnow()`), т.к. SQLite не хранит TZ-инфо.

---

## API: пользовательские операции

Базовый путь: `/`

- `POST /auth/register` — Регистрация  
  Вход: `first_name, last_name, patronymic, email, password, password_repeat`  
  Выход: профиль пользователя (без пароля).

- `POST /auth/login` — Вход  
  Вход: `email, password`  
  Выход: `{ token, expires_at }`.

- `POST /auth/logout` — Выход  
  Требует `Authorization: Bearer`.

- `GET /me` — Текущий пользователь  
  Требует `Authorization: Bearer`.

- `PATCH /me` — Обновить профиль/пароль  
  Требует `Authorization: Bearer`.

- `DELETE /me` — Мягкое удаление аккаунта  
  Требует `Authorization: Bearer`.

---

## API: администрирование RBAC

Все ручки ниже требуют права `access_control:manage` (т.е. роль `admin` из сидинга):

- `POST /admin/resources` — создать ресурс `{ "code": "project" }`
- `GET /admin/resources` — список ресурсов
- `POST /admin/permissions` — создать право `{ "resource_code": "project", "action": "read" }`
- `GET /admin/permissions` — список прав
- `POST /admin/roles` — создать роль `{ "name": "manager" }`
- `GET /admin/roles` — список ролей
- `POST /admin/role-permissions` — привязать право к роли  
  `{ "role_name": "manager", "resource_code": "project", "action": "read" }`
- `POST /admin/user-roles` — выдать роль пользователю  
  `{ "user_email": "ivan@example.com", "role_name": "manager" }`

---

## Моки «бизнес-объектов»

Таблицы создавать не нужно — эндпоинты возвращают фиктивные данные или 403:

- `GET /projects` — **требует** право `project:read`
- `POST /projects` — **требует** право `project:create`
- `GET /reports` — **требует** право `report:read`

---

## Установка и запуск (локально)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
# http://127.0.0.1:8000/docs
```

### Кнопка Authorize в Swagger

В `main.py` задан кастомный OpenAPI с `bearerAuth`, поэтому в правом верхнем углу **/docs** есть кнопка **Authorize**.  
Вставляйте туда `Bearer <token>` после логина.

---

## Запуск в Docker

Сначала установите Docker Desktop (WSL2-движок), добавьте себя в группу `docker-users`, перезапустите сессию.

Сборка и запуск:

```bash
docker build -t auth-rbac .
docker run --rm -p 8000:8000 auth-rbac
# http://127.0.0.1:8000/docs
```

С БД на хосте:
```bash
docker run --rm -p 8000:8000 -v ${PWD}/app.db:/app/app.db auth-rbac
```

Переменные окружения (можно переопределять при `docker run -e ...`):
- `DATABASE_URL` (по умолчанию `sqlite:////app/app.db`)
- `TOKEN_TTL_HOURS` (по умолчанию `24`)
- `ADMIN_EMAIL` (по умолчанию `admin@example.com`)
- `ADMIN_PASSWORD` (по умолчанию `admin123`)

---

## e2e-тест

В репозитории есть скрипт `tests/e2e.py`:

- Локально (при запущенном `uvicorn`):
  ```bash
  python tests/e2e.py
  ```
- В Docker:
  ```bash
  docker run --rm auth-rbac test
  ```

Контейнер в режиме `test` поднимает сервер, ждёт готовности, выполняет e2e и завершает работу.

---

## Примеры запросов

### Логин админа
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
 -H "Content-Type: application/json" \
 -d '{"email":"admin@example.com","password":"admin123"}'
```

### Создание ресурсов и прав (под админ-токеном)
```bash
# ресурс
curl -X POST http://127.0.0.1:8000/admin/resources \
 -H "Authorization: Bearer <ADMIN_TOKEN>" -H "Content-Type: application/json" \
 -d '{"code":"project"}'

# право
curl -X POST http://127.0.0.1:8000/admin/permissions \
 -H "Authorization: Bearer <ADMIN_TOKEN>" -H "Content-Type: application/json" \
 -d '{"resource_code":"project","action":"read"}'
```

### Регистрация пользователя и выдача роли
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
 -H "Content-Type: application/json" \
 -d '{"first_name":"Иван","last_name":"Иванов","patronymic":"","email":"ivan@example.com","password":"qwerty1","password_repeat":"qwerty1"}'

curl -X POST http://127.0.0.1:8000/admin/user-roles \
 -H "Authorization: Bearer <ADMIN_TOKEN>" -H "Content-Type: application/json" \
 -d '{"user_email":"ivan@example.com","role_name":"manager"}'
```

### Доступ к мок-ресурсам (под токеном пользователя)
```bash
curl -H "Authorization: Bearer <USER_TOKEN>" http://127.0.0.1:8000/projects     # 200
curl -X POST -H "Authorization: Bearer <USER_TOKEN>" http://127.0.0.1:8000/projects  # 200
curl -H "Authorization: Bearer <USER_TOKEN>" http://127.0.0.1:8000/reports      # 403 (если право не выдавали)
```

---

## Ошибки и коды статусов

- **401 Unauthorized**
  - Отсутствует/неверный заголовок `Authorization`.
  - Токен не найден/просрочен/отключён.
  - Пользователь неактивен (`is_active=False`).

- **403 Forbidden**
  - Пользователь идентифицирован, но не имеет требуемого `{resource, action}`.

- **400 Bad Request**
  - Бизнес-валидация (например, email уже занят, пароли не совпадают, дубликаты ресурсов/прав).

---

## Расширение и дальнейшие шаги

- **Условия доступа (ABAC-элементы)**: в `permissions` добавить `condition` (JSON) и проверять, например, «владелец объекта», «подразделение», «временные окна».
- **Аудит**: таблица `audit_logs` для фиксации действий пользователей.
- **Refresh-tokens** и «скользящие» сессии.
- **PostgreSQL** и Alembic-миграции.
- **Rate limiting** и блокировки при подборе пароля.

---
