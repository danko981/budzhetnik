from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import date, datetime
from decimal import Decimal

# ---- Пользовательские поля и валидаторы ----


class DecimalField(fields.Decimal):
    """Поле для Decimal с валидацией на положительные значения для денежных сумм."""

    def __init__(self, positive=True, *args, **kwargs):
        self.positive = positive
        super().__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            decimal_value = super()._deserialize(value, attr, data, **kwargs)
            if self.positive and decimal_value <= 0:
                raise ValidationError("Value must be positive.")
            return decimal_value
        except ValidationError as e:
            if isinstance(e.messages, str) and "not a valid decimal" in e.messages:
                raise ValidationError("Invalid number format.")
            raise e

# ---- Базовые схемы ----


class UserSchema(Schema):
    """Схема валидации пользователя."""
    id = fields.Integer(dump_only=True)
    username = fields.String(
        required=True, validate=validate.Length(min=3, max=64))
    email = fields.Email(required=True)
    password = fields.String(
        required=True, load_only=True, validate=validate.Length(min=8))
    created_at = fields.DateTime(dump_only=True)

    @validates('username')
    def validate_username(self, value):
        # Дополнительная валидация имени пользователя если необходимо
        if value.strip() != value:
            raise ValidationError(
                "Username cannot contain leading or trailing whitespace.")

    @validates('email')
    def validate_email(self, value):
        # Дополнительная валидация email если необходимо
        if value.strip() != value:
            raise ValidationError(
                "Email cannot contain leading or trailing whitespace.")


class CategorySchema(Schema):
    """Схема валидации категории."""
    id = fields.Integer(dump_only=True)
    name = fields.String(
        required=True, validate=validate.Length(min=1, max=100))
    type = fields.String(required=True, validate=validate.OneOf(
        ['income', 'expense'], error="Type must be 'income' or 'expense'"))
    user_id = fields.Integer(dump_only=True)

    @validates('name')
    def validate_name(self, value):
        if value.strip() != value:
            raise ValidationError(
                "Category name cannot contain leading or trailing whitespace.")


class BudgetSchema(Schema):
    """Схема валидации бюджета."""
    id = fields.Integer(dump_only=True)
    name = fields.String(
        required=True, validate=validate.Length(min=1, max=100))
    period = fields.String(
        required=True,
        validate=validate.OneOf(
            ['weekly', 'monthly', 'quarterly', 'semiannual', 'annual'])
    )
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    target_amount = DecimalField(places=2, as_string=True, allow_none=True)
    user_id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    @validates('end_date')
    def validate_end_date(self, value, **kwargs):
        start_date = self.context.get(
            'start_date', kwargs.get('data', {}).get('start_date'))
        if start_date and value < start_date:
            raise ValidationError(
                "End date cannot be earlier than start date.")

    @validates('start_date')
    def validate_start_date(self, value):
        if value < date.today():
            raise ValidationError("Start date cannot be in the past.")


class TransactionSchema(Schema):
    """Схема валидации транзакции."""
    id = fields.Integer(dump_only=True)
    description = fields.String(
        allow_none=True, validate=validate.Length(max=255))
    amount = DecimalField(places=2, as_string=True, required=True)
    date = fields.Date(required=True)
    type = fields.String(required=True, validate=validate.OneOf(
        ['income', 'expense'], error="Type must be 'income' or 'expense'"))
    category_id = fields.Integer(required=True)
    user_id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    # Дополнительное поле для отображения с именем категории
    category_name = fields.String(dump_only=True)

    @validates('date')
    def validate_date(self, value):
        # Можно добавить дополнительную валидацию даты, например, не в будущем
        if value > date.today():
            raise ValidationError("Transaction date cannot be in the future.")

# ---- Схемы для использования в API ----

# Схема для регистрации пользователя


class UserRegisterSchema(UserSchema):
    password_confirm = fields.String(required=True, load_only=True)

    @validates('password_confirm')
    def validate_password_match(self, value, **kwargs):
        password = self.context.get(
            'password', kwargs.get('data', {}).get('password'))
        if password and value != password:
            raise ValidationError("Passwords must match.")

# Схема для входа пользователя


class UserLoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)

# Схема для калькулятора сбережений


class SavingsCalculatorSchema(Schema):
    target_amount = DecimalField(places=2, as_string=True, required=True)
    target_date = fields.Date(required=True)
    current_savings = DecimalField(places=2, as_string=True, default="0.00")

    @validates('target_date')
    def validate_future_date(self, value):
        if value <= date.today():
            raise ValidationError("Target date must be in the future.")

# Схемы для отчетов


class DateRangeSchema(Schema):
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    @validates('end_date')
    def validate_end_date(self, value, **kwargs):
        start_date = self.context.get(
            'start_date', kwargs.get('data', {}).get('start_date'))
        if start_date and value < start_date:
            raise ValidationError(
                "End date cannot be earlier than start date.")
