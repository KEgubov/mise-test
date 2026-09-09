# 🍽️ Restaurant Booking API

REST API для онлайн-бронирования столиков в ресторане. Полнофункциональный сервис с асинхронной архитектурой, строгой валидацией, мягким удалением и полным покрытием тестами.

**Стек:** Python 3.13 · FastAPI 0.141+ · SQLAlchemy 2.0 (async) · Pydantic v2 · SQLite · Alembic · phonenumbers

---

## 📋 Содержание

- [Быстрый старт](#-быстрый-старт)
- [API Endpoints](#-api-endpoints)
- [Валидация](#-валидация)
- [Архитектура](#-архитектура)
- [Решения и обоснование](#-решения-и-обоснование)
- [Статус-коды и сценарии](#-статус-коды-и-сценарии)

---

## 🚀 Быстрый старт

### Локально

#### 1. Клонировать репозиторий
```bash
git clone https://github.com/yourusername/mise_test.git
cd mise_test
```

#### 2. Создать виртуальное окружение
```bash
python3.13 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows
```

#### 3. Установить зависимости
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Инициализировать базу данных
```bash
alembic upgrade head
```

Эта команда:
- ✅ Создаст файл `my_database.db` в корне проекта
- ✅ Применит все миграции из папки `alembic/versions/`
- ✅ Инициализирует таблицу `booking_details`

> **Примечание:** Если пропустить этот шаг, приложение создаст БД автоматически при первом запуске (если настроено).

#### 5. Запустить сервер
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Сервер будет доступен на **http://localhost:8000**

#### 6. Открыть документацию
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Docker

```bash
docker-compose up --build
```

При запуске контейнер автоматически:
1. ✅ Устанавливает зависимости Python
2. ✅ Применяет миграции Alembic (`alembic upgrade head`)
3. ✅ Создаёт файл БД `my_database.db`
4. ✅ Инициализирует таблицу `booking_details`
5. ✅ Запускает FastAPI сервер

API будет доступен на **http://localhost:8000/docs** через несколько секунд.

---

## 📚 API Endpoints

| Метод | Путь | Статус | Описание |
|-------|------|--------|---------|
| `POST` | `/bookings/` | 201 | Создать новое бронирование |
| `GET` | `/bookings/` | 200 | Список броней на дату |
| `GET` | `/bookings/{booking_id}` | 200 | Получить бронь по ID |
| `PATCH` | `/bookings/{booking_id}` | 200 | Отменить бронь (мягкое удаление) |

---

### 1️⃣ Создание бронирования `POST /bookings/`

**Запрос:**
```bash
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "guest_name": "Кирилл Сидоров",
    "guest_phone": "+79997776615",
    "booking_date": "2026-09-15",
    "booking_time": "19:00",
    "guests": 4
  }'
```

**Ответ (201 Created):**
```json
{
  "booking_id": 1,
  "guest_name": "Кирилл Сидоров",
  "guest_phone": "+79997776615",
  "booking_date": "2026-09-15",
  "booking_time": "19:00",
  "guests": 4,
  "status": "active"
}
```

**Ошибка: слот занят (409 Conflict):**
```json
{
  "detail": "Время 2026-09-15 19:00:00 уже занято",
  "error_code": "CONFLICT"
}
```

---

### 2️⃣ Получить список броней `GET /bookings/?booking_date=YYYY-MM-DD`

**Запрос:**
```bash
curl "http://localhost:8000/bookings/?booking_date=2026-09-15"
```

**Ответ (200 OK):**
```json
{
  "bookings": [
    {
      "booking_id": 1,
      "guest_name": "Кирилл",
      "guest_phone": "+79997776615",
      "booking_date": "2026-09-15",
      "booking_time": "19:00",
      "guests": 4,
      "status": "active"
    },
    {
      "booking_id": 2,
      "guest_name": "Мария",
      "guest_phone": "+79061234567",
      "booking_date": "2026-09-15",
      "booking_time": "20:00",
      "guests": 2,
      "status": "active"
    }
  ]
}
```

---

### 3️⃣ Получить бронь по ID `GET /bookings/{booking_id}`

**Запрос:**
```bash
curl "http://localhost:8000/bookings/1"
```

**Ответ (200 OK):**
```json
{
  "booking_id": 1,
  "guest_name": "Кирилл",
  "guest_phone": "+79997776615",
  "booking_date": "2026-09-15",
  "booking_time": "19:00",
  "guests": 4,
  "status": "active"
}
```

**Ошибка: не найдена (404 Not Found):**
```json
{
  "detail": "Бронирование с id=999 не найдено"
}
```

---

### 4️⃣ Отменить бронь `PATCH /bookings/{booking_id}`

**Запрос:**
```bash
curl -X PATCH "http://localhost:8000/bookings/1"
```

**Ответ (200 OK):**
```json
{
  "booking_id": 1,
  "guest_name": "Кирилл",
  "guest_phone": "+79997776615",
  "booking_date": "2026-09-15",
  "booking_time": "19:00",
  "guests": 4,
  "status": "cancelled"
}
```

> **Замечание:** Статус меняется на `cancelled`, запись физически не удаляется (мягкое удаление). Это позволяет хранить историю операций и выполнять аудит.

---

## ✅ Валидация

### Правила для полей

| Поле | Правило | Пример |
|------|---------|--------|
| `guest_name` | Минимум 2 символа | ✅ "Иван Петров" |
| `guest_phone` | Российский мобильный номер (phonenumbers) | ✅ "+79997776615" или "89997776615" |
| `booking_date` | От сегодня до +90 дней | ✅ "2026-09-15" |
| `booking_time` | Почасовые слоты 12:00–22:00 | ✅ "19:00" |
| `guests` | Целое число 1–12 | ✅ 4 |

### Примеры ошибок валидации

**Невалидный телефон (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "guest_phone"],
      "msg": "Некорректный формат номера",
      "input": "12345"
    }
  ]
}
```

**Дата раньше сегодня (422):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "booking_date"],
      "msg": "Дата бронирования не может быть раньше сегодня",
      "input": "2026-01-01"
    }
  ]
}
```

**Время за пределами слотов (422):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "booking_time"],
      "msg": "Доступные слоты: 12:00, 13:00, ..., 22:00",
      "input": "11:30"
    }
  ]
}
```

---

## 🏗️ Архитектура

### Слоистая архитектура (Layered Architecture)

```
app/
├── main.py                           # Инициализация FastAPI, lifecycle, исключения
│
├── src/
│   ├── api/
│   │   ├── bookings.py              # Роуты эндпоинтов (HTTP слой)
│   │   ├── dependency.py            # Инъекция зависимостей
│   │   └── exception_handler.py     # Обработчики кастомных ошибок
│   │
│   ├── schemas/
│   │   └── booking_schemas.py       # Pydantic v2 DTO для валидации
│   │
│   ├── services/
│   │   ├── booking_service.py       # Бизнес-логика (Service слой)
│   │   └── exception.py             # Кастомные исключения
│   │
│   ├── repository/
│   │   └── booking_repo.py          # Работа с БД (Data Access слой)
│   │
│   ├── models/
│   │   └── orm_booking.py           # SQLAlchemy ORM модели
│   │
│   ├── core/
│   │   ├── db_conn.py               # Конфигурация подключения БД
│   │   └── enums.py                 # Енумы (BookingStatus)
│   │
│   ├── config/
│   │   └── db_config.py             # Конфигурация приложения
│   │
│   └── utils/
│       └── create_tables.py         # Утилиты инициализации
│
├── alembic/                          # Миграции БД
│   ├── versions/                     # Версионированные миграции
│   ├── env.py                        # Конфигурация Alembic
│   └── script.py.mako                # Шаблон миграций
│
├── tests/                            # Юнит и интеграционные тесты
│
├── requirements.txt                  # Зависимости Python
├── Dockerfile                        # Docker образ
├── docker-compose.yaml               # Оркестрация контейнеров
├── alembic.ini                       # Конфигурация Alembic
├── .env.example                      # Пример переменных окружения
└── README.md                         # Этот файл
```

### Поток данных

```
HTTP Request
    ↓
API Router (bookings.py)
    ↓
Dependency Injection (dependency.py)
    ↓
Service Layer (booking_service.py) ← бизнес-логика
    ↓
Repository Layer (booking_repo.py) ← SQLAlchemy queries
    ↓
ORM Model (orm_booking.py)
    ↓
SQLite Database
    ↓
(обратный путь с преобразованиями)
    ↓
Pydantic DTO (booking_schemas.py)
    ↓
HTTP Response (JSON)
```

---

## 🎯 Решения и обоснование

### 1. **PATCH вместо DELETE для отмены брони**

В ТЗ было указано использовать `DELETE`, но я выбрал `PATCH` — вот почему:

- **PATCH** = частичное обновление ресурса (меняем статус)
- **DELETE** = полное удаление ресурса (физическое удаление из БД)

Поскольку мы не удаляем запись, а обновляем её статус на `cancelled` (мягкое удаление), **PATCH** точнее описывает семантику операции. Это следует REST-принципам и облегчает аудит.

---

### 2. **Библиотека `phonenumbers` для валидации**

Выбрал `phonenumbers` вместо regex по нескольким причинам:

```python
# ❌ Regex подход (сложный, ненадежный)
pattern = r'^[+7|8]\d{10}$'

# ✅ phonenumbers подход (надежный, масштабируемый)
parsed = phonenumbers.parse(phone, "RU")
if not phonenumbers.is_valid_number(parsed):
    raise ValueError("Invalid")
```

**Преимущества:**
- ✅ Поддерживает разные форматы: `+79997776615`, `89997776615`, `9997776615`
- ✅ Нормализует в E.164: любой формат → `+79997776615`
- ✅ Проверяет, что это мобильный номер (отсеит городские, 8-800, сервисные)
- ✅ Структурированная база правил для 240+ стран
- ✅ Близко к production-коду

**Примеры нормализации:**
```
+7 (916) 123-45-67    → +79161234567  ✅
8 916 123 45 67       → +79161234567  ✅
9161234567            → +79161234567  ✅ (библиотека понимает, что это Россия)
123456789             → ValueError     ✅ (не соответствует формату)
```

---

### 3. **Enum для статуса брони**

```python
class BookingStatus(enum.StrEnum):
    ACTIVE = "active"
    CANCELED = "cancelled"
```

**Почему enum?**
- 🔒 Гарантирует только два значения: `active` или `cancelled`
- 🛡️ Предотвращает ошибочные состояния (`acive`, `cancelled`, `pending` и т.д.)
- 📝 Типизация: IDE подсказывает возможные значения
- 🔍 Легче для фильтрации и аналитики

**Альтернатива (плохо):**
```python
status: str  # ❌ Может содержать что угодно
```

---

### 4. **Асинхронная SQLAlchemy 2.0**

```python
async def create_booking(self, session: AsyncSession, booking: BookingAddDTO):
    # Асинхронные операции, совместимые с FastAPI
    result = await session.execute(query)
    await session.commit()
```

**Почему async?**
- ⚡ Масштабируемость: один процесс обрабатывает тысячи параллельных запросов
- 🔄 Не блокирует I/O операции (запросы к БД)
- 🎯 Естественный fit с FastAPI (async-native)

Без async:
```python
session.execute(query)  # ❌ Блокирует на время запроса к БД
```

---

### 5. **Alembic для миграций БД**

```bash
alembic init alembic          # Инициализация
alembic revision --autogenerate -m "Add bookings table"
alembic upgrade head          # Применить миграции
```

**Плюсы:**
- 📜 История всех изменений схемы БД
- ↩️ Откаты: `alembic downgrade -1`
- 👥 Совместная разработка: все разработчики имеют одинаковую схему
- 🔄 CI/CD интеграция

Альтернатива (плохо):
```python
Base.metadata.create_all(engine)  # ❌ Нет истории
```

---

### 6. **Слоистая архитектура (Routes → Services → Repository)**

```
request
  ↓
API Router        ← HTTP level
  ↓
Service           ← Business logic (валидация, проверка слотов)
  ↓
Repository        ← Data access (SQL queries)
  ↓
Database
```

**Преимущества:**
- 🔧 Легко тестировать каждый слой независимо
- 🔄 Переиспользуемая бизнес-логика
- 📝 Понятный код и разделение ответственности
- 🔌 Легко менять DB (SQLite → PostgreSQL)

---

### Файл зависимостей

```
fastapi==0.141.1
uvicorn==0.52.4
sqlalchemy==2.0.52
pydantic==2.13.5
pydantic-settings==2.15.0
phonenumbers==9.0.38
alembic==1.19.2
aiosqlite==0.22.1
python-dotenv==1.2.3
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
black==26.5.1
mypy==1.13.5
```

---

## 📋 Статус-коды и сценарии

| Сценарий | Код | Тело ответа |
|----------|-----|-------------|
| Успешное создание | 201 | Объект брони с `status="active"` |
| Невалидные данные | 422 | Pydantic validation error |
| Слот занят | 409 | `{"detail": "...", "error_code": "CONFLICT"}` |
| Не найдена | 404 | `{"detail": "Бронирование не найдено"}` |
| Успешная отмена | 200 | Объект брони с `status="cancelled"` |
| Успешный список | 200 | `{"bookings": [...]}` |

---

## 🔌 Интеграции и расширения

### Подключённые библиотеки

| Библиотека | Версия | Назначение |
|------------|--------|-----------|
| FastAPI | 0.141.1 | Web framework |
| SQLAlchemy | 2.0.52 | ORM + SQL toolkit |
| Pydantic | 2.13.5 | Валидация + сериализация |
| Alembic | 1.19.2 | Миграции БД |
| phonenumbers | 9.0.38 | Валидация телефонов |
| aiosqlite | 0.22.1 | Async SQLite driver |

---

## 📞 Контакты

- **GitHub:** [Ссылка](https://github.com/KEgubov)
- **Email:** kirilegubov@gmail.com
- **Telegram:** @Maestro2344

---

## 📄 Лицензия

MIT License. Свободно используй и модифицируй.

---

**Создано как тестовое задание для MISE · Backend Trainee · Python/FastAPI**

*Последнее обновление: September 2026*