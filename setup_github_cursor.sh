#!/bin/bash

# Скрипт для настройки GitHub и интеграции с Cursor AI

# Цвета для сообщений
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}    Настройка GitHub и интеграции с Cursor AI         ${NC}"
echo -e "${BLUE}=====================================================${NC}\n"

# Шаг 1: Настройка Git
echo -e "${GREEN}Шаг 1: Настройка Git${NC}"

setup_git() {
    read -p "Введите ваше имя для Git: " GIT_NAME
    read -p "Введите ваш email для Git: " GIT_EMAIL
    
    git config --global user.name "$GIT_NAME"
    git config --global user.email "$GIT_EMAIL"
    
    echo -e "${GREEN}Git настроен для пользователя: ${YELLOW}$GIT_NAME ($GIT_EMAIL)${NC}"
}

if [ -z "$(git config --global user.name)" ] || [ -z "$(git config --global user.email)" ]; then
    echo -e "${YELLOW}Git не настроен. Давайте настроим.${NC}"
    setup_git
else
    echo -e "Git уже настроен для пользователя: ${YELLOW}$(git config --global user.name) ($(git config --global user.email))${NC}"
    read -p "Хотите изменить настройки Git? (y/n): " CHANGE_GIT
    if [ "$CHANGE_GIT" = "y" ]; then
        setup_git
    fi
fi

# Шаг 2: Настройка GitHub репозитория
echo -e "\n${GREEN}Шаг 2: Настройка GitHub репозитория${NC}"

setup_github_repo() {
    read -p "Введите ваше имя пользователя GitHub: " GITHUB_USER
    read -p "Введите имя репозитория (по умолчанию: budgetnik): " REPO_NAME
    REPO_NAME=${REPO_NAME:-budgetnik}
    
    echo -e "${YELLOW}Для создания репозитория на GitHub:${NC}"
    echo -e "1. Перейдите на сайт ${BLUE}https://github.com/new${NC}"
    echo -e "2. Введите имя репозитория: ${YELLOW}$REPO_NAME${NC}"
    echo -e "3. НЕ инициализируйте репозиторий с README, .gitignore или лицензией"
    echo -e "4. Нажмите 'Create repository'"
    
    read -p "Вы создали репозиторий на GitHub? (y/n): " REPO_CREATED
    
    if [ "$REPO_CREATED" = "y" ]; then
        echo -e "${GREEN}Настройка удаленного репозитория...${NC}"
        git remote remove origin 2>/dev/null
        git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
        git branch -M main
        
        echo -e "${GREEN}Репозиторий настроен:${NC} ${YELLOW}https://github.com/$GITHUB_USER/$REPO_NAME.git${NC}"
        
        echo -e "\n${YELLOW}Для отправки кода в GitHub:${NC}"
        echo -e "1. Создайте токен доступа на GitHub (если у вас его нет):"
        echo -e "   - Перейдите в ${BLUE}https://github.com/settings/tokens${NC}"
        echo -e "   - Нажмите 'Generate new token' → 'Generate new token (classic)'"
        echo -e "   - Добавьте примечание (например, 'Cursor AI Integration')"
        echo -e "   - Выберите области: 'repo' и 'workflow'"
        echo -e "   - Нажмите 'Generate token' и скопируйте его"
        
        read -p "У вас есть токен GitHub? (y/n): " HAS_TOKEN
        
        if [ "$HAS_TOKEN" = "y" ]; then
            read -p "Введите ваш токен GitHub (токен не будет отображаться): " -s GITHUB_TOKEN
            echo ""
            
            git remote set-url origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git"
            
            echo -e "${GREEN}Отправка кода в GitHub...${NC}"
            git push -u origin main
            
            # Возвращаем обычный URL без токена
            git remote set-url origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
            
            echo -e "${GREEN}Код успешно отправлен в GitHub!${NC}"
        else
            echo -e "${YELLOW}Для отправки кода в GitHub, вам потребуется токен.${NC}"
            echo -e "Следуйте инструкциям в файле ${BLUE}github_token_instructions.md${NC}"
        fi
    else
        echo -e "${RED}Репозиторий не был создан. Выполните это позже вручную.${NC}"
        echo -e "Следуйте инструкциям в файле ${BLUE}github_token_instructions.md${NC}"
    fi
}

if git remote get-url origin 2>/dev/null | grep -q "YOUR_USERNAME"; then
    echo -e "${YELLOW}Удаленный репозиторий не настроен корректно.${NC}"
    setup_github_repo
elif git remote -v 2>/dev/null | grep -q "origin"; then
    echo -e "Удаленный репозиторий настроен: ${YELLOW}$(git remote get-url origin)${NC}"
    read -p "Хотите изменить настройки удаленного репозитория? (y/n): " CHANGE_REMOTE
    if [ "$CHANGE_REMOTE" = "y" ]; then
        setup_github_repo
    fi
else
    echo -e "${YELLOW}Удаленный репозиторий не настроен.${NC}"
    setup_github_repo
fi

# Шаг 3: Инструкции по интеграции с Cursor AI
echo -e "\n${GREEN}Шаг 3: Инструкции по интеграции Cursor AI с GitHub${NC}"
echo -e "Для интеграции Cursor AI с GitHub, выполните следующие действия:"
echo -e "1. Откройте настройки Cursor AI (${YELLOW}Command + ,${NC} на Mac или ${YELLOW}Ctrl + ,${NC} на Windows/Linux)"
echo -e "2. Перейдите в раздел ${YELLOW}GitHub & Source Control${NC}"
echo -e "3. Нажмите на кнопку ${YELLOW}Connect to GitHub${NC}"
echo -e "4. Авторизуйтесь в GitHub и предоставьте необходимые разрешения"

echo -e "\n${GREEN}Шаг 4: Проверка интеграции${NC}"
echo -e "После настройки используйте команду ${YELLOW}@Git${NC} в чате Cursor для работы с репозиторием."

echo -e "\n${BLUE}=====================================================${NC}"
echo -e "${BLUE}                Настройка завершена                    ${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo -e "\nПодробные инструкции доступны в файлах:"
echo -e "- ${YELLOW}cursor_github_integration.md${NC}"
echo -e "- ${YELLOW}github_token_instructions.md${NC}" 