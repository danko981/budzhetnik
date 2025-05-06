# Упрощенная версия API для Budgetnik

Данная версия API представляет собой облегченную реализацию системы аутентификации для приложения Budgetnik. Она была создана для решения проблем с тайм-аутами при регистрации и авторизации пользователей.

## Основные файлы

- `simple_app.py` - Основное Flask-приложение
- `simple_wsgi.py` - WSGI-точка входа для развертывания
- `views/auth_simple.py` - Реализация API аутентификации
- `data/users.json` - Файл для хранения пользовательских данных
- `static/api_test.html` - Веб-интерфейс для тестирования API

## Установка и запуск

1. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

2. Запустите приложение:
   ```
   python simple_app.py
   ```

3. Приложение будет доступно по адресу: `http://localhost:8000`

4. Для тестирования API через веб-интерфейс откройте в браузере:
   ```
   http://localhost:8000/api_test.html
   ```

## Доступные API-эндпоинты

### Проверка статуса API
```
GET /api/status
```

### Регистрация пользователя
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "имя_пользователя",
  "password": "пароль",
  "email": "email@example.com"
}
```

### Авторизация и получение токена
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "имя_пользователя",
  "password": "пароль"
}
```

### Получение данных текущего пользователя
```
GET /api/v1/auth/me
Authorization: Bearer <токен>
```

### Обновление данных пользователя
```
PUT /api/v1/auth/update
Authorization: Bearer <токен>
Content-Type: application/json

{
  "email": "новый_email@example.com",
  "password": "новый_пароль"
}
```

## Примеры использования с curl

### Авторизация
```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "demo", "password": "demo123"}' http://localhost:8000/api/v1/auth/login
```

### Регистрация
```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "newuser", "password": "newpass123", "email": "new@example.com"}' http://localhost:8000/api/v1/auth/register
```

### Получение данных пользователя
```bash
curl -X GET -H "Authorization: Bearer <полученный_токен>" http://localhost:8000/api/v1/auth/me
```

### Обновление данных пользователя
```bash
curl -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer <полученный_токен>" -d '{"email": "updated@example.com"}' http://localhost:8000/api/v1/auth/update
```

## Примечания по безопасности

- В этой простой реализации пароли хранятся в открытом виде. В продакшн-версии необходимо использовать хеширование паролей.
- Токены JWT имеют срок действия 24 часа.
- В качестве секретного ключа используется значение из переменной окружения SECRET_KEY или значение по умолчанию 'dev-secret-key'.

## Интеграция с фронтендом

Для интеграции фронтенда с этим API установите правильные URL в файле `static/environment.js`:

```javascript
window.apiConfig = {
    apiUrl: 'http://localhost:8000/api/v1',
    authEndpoint: 'http://localhost:8000/api/v1/auth',
    timeout: 30000, // 30 секунд
    retryAttempts: 3
};
``` 