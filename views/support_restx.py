from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from marshmallow import ValidationError
from ..utils.error_handlers import handle_validation_error, handle_exception, log_operation

# Создаем Namespace
ns = Namespace('support', description='Поддержка и справочная информация')

# --- Модели данных ---
faq_item_model = ns.model('FAQItem', {
    'id': fields.Integer(description='ID вопроса'),
    'question': fields.String(description='Вопрос'),
    'answer': fields.String(description='Ответ')
})

contact_input_model = ns.model('ContactInput', {
    'name': fields.String(required=True, description='Имя пользователя', example='Иван Иванов'),
    'email': fields.String(required=True, description='Email для ответа', example='user@example.com'),
    'subject': fields.String(required=True, description='Тема обращения', example='Вопрос о категориях'),
    'message': fields.String(required=True, description='Текст сообщения', example='Как добавить собственную категорию?')
})

contact_output_model = ns.model('ContactOutput', {
    'success': fields.Boolean(description='Успех отправки сообщения'),
    'message': fields.String(description='Информационное сообщение')
})

# --- Данные FAQ ---
FAQ_DATA = [
    {
        "id": 1,
        "question": "Как добавить новую транзакцию (доход или расход)?",
        "answer": "Перейдите в раздел 'Транзакции' и нажмите кнопку 'Добавить'. Выберите тип (доход/расход), категорию, введите сумму, дату и необязательное описание. Нажмите 'Сохранить'."
    },
    {
        "id": 2,
        "question": "Как создать новую категорию?",
        "answer": "В разделе 'Категории' нажмите 'Создать'. Введите название категории, выберите тип (доход или расход) и нажмите 'Сохранить'. Убедитесь, что имя уникально для выбранного типа."
    },
    {
        "id": 3,
        "question": "Как настроить бюджет на месяц?",
        "answer": "В разделе 'Бюджеты' нажмите 'Создать'. Выберите период 'Месячный', установите даты начала и конца месяца, и при желании укажите целевую сумму. Теперь вы можете отслеживать расходы по этому бюджету."
    },
    {
        "id": 4,
        "question": "Как рассчитать сколько нужно откладывать для достижения финансовой цели?",
        "answer": "Перейдите в раздел 'Калькуляторы' и выберите 'Калькулятор сбережений'. Введите целевую сумму, дату достижения и текущие накопления. Система рассчитает необходимую ежемесячную сумму."
    },
    {
        "id": 5,
        "question": "Как посмотреть статистику расходов по категориям?",
        "answer": "В разделе 'Отчеты' выберите 'Расходы по категориям', установите интересующий вас период времени и нажмите 'Сформировать'. Вы получите детальную разбивку расходов по категориям с процентным соотношением."
    }
]

# --- Ресурсы ---


@ns.route('/faq')
class FAQList(Resource):
    """Часто задаваемые вопросы."""

    @ns.doc('get_faq')
    @ns.response(200, 'Список FAQ', model=[faq_item_model])
    def get(self):
        """Получить список FAQ"""
        try:
            log_operation(operation_type="read", resource_type="faq")
            return FAQ_DATA
        except Exception as e:
            handle_exception(e, "get FAQ")
            return None


@ns.route('/faq/<int:id>')
@ns.param('id', 'ID вопроса')
class FAQItem(Resource):
    """Конкретный вопрос из FAQ."""

    @ns.doc('get_faq_item')
    @ns.response(200, 'FAQ элемент', model=faq_item_model)
    @ns.response(404, 'Вопрос не найден')
    def get(self, id):
        """Получить конкретный вопрос из FAQ по ID"""
        try:
            # Поиск вопроса по ID
            faq_item = next(
                (item for item in FAQ_DATA if item["id"] == id), None)

            if not faq_item:
                ns.abort(404, message=f"FAQ item with ID {id} not found")

            log_operation(operation_type="read",
                          resource_type="faq", resource_id=id)
            return faq_item
        except Exception as e:
            handle_exception(e, "get FAQ item")
            return None


@ns.route('/contact')
class ContactSupport(Resource):
    """Отправка сообщения в поддержку."""

    @ns.doc('send_contact_form')
    @ns.expect(contact_input_model, validate=True)
    @ns.response(200, 'Сообщение отправлено', model=contact_output_model)
    @ns.response(400, 'Ошибка валидации')
    def post(self):
        """Отправить сообщение в поддержку"""
        try:
            # В реальном приложении здесь будет отправка email или сохранение в БД
            data = request.json

            # Простая валидация
            if not data.get('email') or '@' not in data.get('email', ''):
                return {'success': False, 'message': 'Некорректный email адрес'}, 400

            if not data.get('message') or len(data.get('message', '').strip()) < 10:
                return {'success': False, 'message': 'Сообщение должно содержать минимум 10 символов'}, 400

            # Логируем обращение
            log_operation(
                operation_type="create",
                resource_type="support_request",
                details={"email": data.get(
                    'email'), "subject": data.get('subject')}
            )

            # Имитация отправки сообщения
            return {
                'success': True,
                'message': 'Ваше сообщение успешно отправлено. Мы ответим на указанный email.'
            }

        except Exception as e:
            handle_exception(e, "contact support")
            return None
