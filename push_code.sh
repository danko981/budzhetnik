#!/bin/bash

# Скрипт для отправки кода в GitHub репозиторий

# Цвета для сообщений
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}         Отправка кода в GitHub репозиторий           ${NC}"
echo -e "${BLUE}=====================================================${NC}\n"

# Проверяем текущие настройки удаленного репозитория
echo -e "${GREEN}Текущие настройки репозитория:${NC}"
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
echo -e "Удаленный репозиторий: ${YELLOW}$REMOTE_URL${NC}"

# Настраиваем GitHub-токен
echo -e "\n${GREEN}Настройка токена GitHub:${NC}"
echo -e "Для отправки кода вам нужен токен GitHub с доступом к репозиторию."
echo -e "Если у вас еще нет токена, создайте его на странице ${BLUE}https://github.com/settings/tokens${NC}"
echo -e "- Выберите 'Generate new token' → 'Generate new token (classic)'"
echo -e "- Добавьте примечание (например, 'Budgetnik repo')"
echo -e "- Выберите области: 'repo' (полный доступ к репозиториям)"
echo -e "- Нажмите 'Generate token' и скопируйте его\n"

read -p "Введите имя пользователя GitHub: " GITHUB_USER
read -p "Введите имя репозитория (по умолчанию: budgetnik): " REPO_NAME
REPO_NAME=${REPO_NAME:-budgetnik}
read -p "Введите ваш токен GitHub (токен не будет отображаться): " -s GITHUB_TOKEN
echo ""

# Создаем временный URL с токеном
TEMP_URL="https://$GITHUB_TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git"

# Устанавливаем удаленный репозиторий с токеном
echo -e "\n${GREEN}Настройка удаленного репозитория...${NC}"
git remote remove origin 2>/dev/null
git remote add origin "$TEMP_URL"

# Отправляем код
echo -e "\n${GREEN}Отправка кода в GitHub...${NC}"
git push -u origin main

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Код успешно отправлен в GitHub!${NC}"
    # Возвращаем URL без токена для безопасности
    git remote set-url origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
    echo -e "Ваш репозиторий доступен по адресу: ${BLUE}https://github.com/$GITHUB_USER/$REPO_NAME${NC}"
    
    echo -e "\n${GREEN}Настройка Cursor AI:${NC}"
    echo -e "Теперь вы можете настроить интеграцию Cursor AI с GitHub:"
    echo -e "1. Откройте настройки Cursor AI (${YELLOW}Command + ,${NC})"
    echo -e "2. Перейдите в раздел ${YELLOW}GitHub & Source Control${NC}"
    echo -e "3. Нажмите на кнопку ${YELLOW}Connect to GitHub${NC}"
    echo -e "4. Авторизуйтесь в GitHub и предоставьте необходимые разрешения"
else
    echo -e "\n${RED}Ошибка при отправке кода в GitHub.${NC}"
    echo -e "Возможные причины:"
    echo -e "- Репозиторий не существует на GitHub"
    echo -e "- Неверный токен GitHub"
    echo -e "- Нет доступа к репозиторию"
    
    echo -e "\n${YELLOW}Рекомендации:${NC}"
    echo -e "1. Проверьте, создан ли репозиторий на GitHub: https://github.com/$GITHUB_USER/$REPO_NAME"
    echo -e "2. Если репозиторий не существует, создайте его на GitHub"
    echo -e "3. Проверьте правильность токена и повторите попытку"
fi

echo -e "\n${BLUE}=====================================================${NC}"
echo -e "${BLUE}                  Операция завершена                  ${NC}"
echo -e "${BLUE}=====================================================${NC}" 