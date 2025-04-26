#!/bin/bash

# Скрипт для ручной отправки кода в GitHub
echo "=== Подготовка к отправке кода в GitHub ==="
echo ""

# Удаляем текущую привязку
echo "1. Удаление текущей привязки к удаленному репозиторию..."
git remote remove origin
echo "   Готово"

# Добавляем новый репозиторий
echo ""
echo "2. Добавление нового удаленного репозитория..."
git remote add origin https://github.com/danko981/budzhetnik.git
echo "   Готово"

# Настраиваем основную ветку
echo ""
echo "3. Настройка основной ветки..."
git branch -M main
echo "   Готово"

echo ""
echo "=== Подготовка завершена ==="
echo ""
echo "Теперь выполните команду:"
echo "git push -u origin main"
echo ""
echo "При запросе учетных данных введите:"
echo "* Имя пользователя: danko981"
echo "* Пароль: ваш токен доступа GitHub"
echo ""
echo "После успешной отправки кода, настройте интеграцию Cursor AI с GitHub:"
echo "1. Откройте настройки Cursor AI (Command + ,)"
echo "2. Перейдите в раздел 'GitHub & Source Control'"
echo "3. Нажмите на кнопку 'Connect to GitHub'"
echo "4. Авторизуйтесь в GitHub и предоставьте необходимые разрешения" 