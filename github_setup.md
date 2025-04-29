# Настройка соединения с GitHub

1. **Замените YOUR_USERNAME в следующей команде на ваше реальное имя пользователя GitHub**:
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/budgetnik.git
git branch -M main
git push -u origin main
```

2. **Для безопасного доступа через SSH** (опционально):
```bash
# Генерация SSH ключа
ssh-keygen -t ed25519 -C "your_email@example.com"

# Запуск SSH-агента
eval "$(ssh-agent -s)"

# Добавление ключа в SSH-агент
ssh-add ~/.ssh/id_ed25519

# Просмотр публичного ключа (добавьте его в настройки GitHub)
cat ~/.ssh/id_ed25519.pub

# Настройка удаленного репозитория через SSH
git remote set-url origin git@github.com:YOUR_USERNAME/budgetnik.git
```

3. **После настройки соединения с GitHub, интегрируйте его с Cursor AI**:
- Откройте Cursor AI
- Перейдите в Settings → GitHub & Source Control
- Нажмите "Connect to GitHub"
- Авторизуйтесь и предоставьте доступ

После выполнения этих шагов вы сможете использовать функции GitHub в Cursor AI и команду `@Git` для работы с репозиторием. 