#!/bin/bash

# Скрипт для настройки интеграции Cursor AI с GitHub

# Цвета для сообщений
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Настройка интеграции Cursor AI с GitHub ===${NC}\n"

# Проверка Git конфигурации
echo -e "${GREEN}Шаг 1: Проверка Git конфигурации${NC}"
USER_NAME=$(git config --global user.name)
USER_EMAIL=$(git config --global user.email)

if [ -z "$USER_NAME" ] || [ -z "$USER_EMAIL" ]; then
    echo -e "${RED}Ошибка: Не настроено имя пользователя или email в Git.${NC}"
    echo -e "Выполните команды:"
    echo -e "git config --global user.name \"Ваше Имя\""
    echo -e "git config --global user.email \"ваш.email@example.com\""
    exit 1
else
    echo -e "Git настроен для пользователя: ${YELLOW}$USER_NAME ($USER_EMAIL)${NC}"
fi

# Проверка удаленного репозитория
echo -e "\n${GREEN}Шаг 2: Проверка удаленного репозитория${NC}"
REMOTE_URL=$(git remote get-url origin 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "${RED}Удаленный репозиторий не настроен.${NC}"
    read -p "Хотите настроить репозиторий сейчас? (y/n): " SETUP_REMOTE
    
    if [ "$SETUP_REMOTE" = "y" ]; then
        read -p "Введите ваше имя пользователя GitHub: " GITHUB_USER
        read -p "Введите имя репозитория: " REPO_NAME
        
        echo "Настройка удаленного репозитория..."
        git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
        git branch -M main
        
        echo -e "${YELLOW}Репозиторий настроен: https://github.com/$GITHUB_USER/$REPO_NAME.git${NC}"
    else
        echo -e "${YELLOW}Пропускаем настройку удаленного репозитория.${NC}"
    fi
else
    echo -e "Удаленный репозиторий настроен: ${YELLOW}$REMOTE_URL${NC}"
fi

# Инструкции по настройке Cursor AI
echo -e "\n${GREEN}Шаг 3: Инструкции по настройке Cursor AI${NC}"
echo -e "Для интеграции Cursor AI с GitHub, выполните следующие действия в интерфейсе Cursor:"
echo -e "1. Откройте настройки Cursor AI (${YELLOW}Command + ,${NC} на Mac или ${YELLOW}Ctrl + ,${NC} на Windows/Linux)"
echo -e "2. Перейдите в раздел ${YELLOW}GitHub & Source Control${NC}"
echo -e "3. Нажмите на кнопку ${YELLOW}Connect to GitHub${NC}"
echo -e "4. Авторизуйтесь в GitHub и предоставьте необходимые разрешения"

echo -e "\n${GREEN}Шаг 4: Проверка интеграции${NC}"
echo -e "После настройки используйте команду ${YELLOW}@Git${NC} в чате Cursor для работы с репозиторием."

echo -e "\n${GREEN}=== Настройка завершена ===${NC}"
echo -e "Дополнительную информацию можно найти в файле ${YELLOW}cursor_github_integration.md${NC}" 