import unittest
from datetime import date, timedelta
from decimal import Decimal
from services.calculator_service import calculate_required_savings


class TestCalculatorService(unittest.TestCase):
    """Тесты для сервиса расчета финансовых целей."""

    def test_valid_calculation(self):
        """Тестирование корректного расчета требуемых сбережений."""
        future_date = date.today() + timedelta(days=365)  # год вперед
        target_amount = Decimal('10000.00')
        current_savings = Decimal('1000.00')

        result = calculate_required_savings(
            target_amount=target_amount,
            target_date=future_date,
            current_savings=current_savings
        )

        # Проверка структуры ответа
        self.assertIn('target_amount', result)
        self.assertIn('current_savings', result)
        self.assertIn('target_date', result)
        self.assertIn('amount_to_save', result)
        self.assertIn('months_remaining', result)
        self.assertIn('required_monthly_savings', result)

        # Проверка значений
        self.assertEqual(result['target_amount'], str(target_amount))
        self.assertEqual(result['current_savings'], str(current_savings))
        self.assertEqual(result['target_date'], future_date.isoformat())
        self.assertEqual(result['amount_to_save'], str(Decimal('9000.00')))

        # Месяцы должны быть примерно 12 (может меняться из-за дней)
        self.assertTrue(11 <= result['months_remaining'] <= 13)

        # Проверка расчета ежемесячных сбережений
        expected_monthly = Decimal('9000.00') / \
            Decimal(result['months_remaining'])
        expected_monthly = expected_monthly.quantize(Decimal('0.01'))
        self.assertEqual(
            Decimal(result['required_monthly_savings']), expected_monthly)

    def test_goal_already_reached(self):
        """Тестирование случая, когда цель уже достигнута."""
        future_date = date.today() + timedelta(days=30)  # месяц вперед
        target_amount = Decimal('1000.00')
        current_savings = Decimal('1500.00')  # Больше целевой суммы

        result = calculate_required_savings(
            target_amount=target_amount,
            target_date=future_date,
            current_savings=current_savings
        )

        # Основная проверка
        self.assertEqual(result['amount_to_save'], '0.00')
        self.assertEqual(result['months_remaining'], 0)
        self.assertEqual(result['required_monthly_savings'], '0.00')
        self.assertIn('message', result)
        self.assertIn('Goal already reached', result['message'])

    def test_negative_target_amount(self):
        """Тестирование исключения при отрицательной целевой сумме."""
        future_date = date.today() + timedelta(days=30)
        target_amount = Decimal('-100.00')
        current_savings = Decimal('0.00')

        with self.assertRaises(ValueError) as context:
            calculate_required_savings(
                target_amount=target_amount,
                target_date=future_date,
                current_savings=current_savings
            )

        self.assertIn('must be positive', str(context.exception))

    def test_negative_current_savings(self):
        """Тестирование исключения при отрицательных текущих сбережениях."""
        future_date = date.today() + timedelta(days=30)
        target_amount = Decimal('1000.00')
        current_savings = Decimal('-100.00')

        with self.assertRaises(ValueError) as context:
            calculate_required_savings(
                target_amount=target_amount,
                target_date=future_date,
                current_savings=current_savings
            )

        self.assertIn('cannot be negative', str(context.exception))

    def test_past_target_date(self):
        """Тестирование исключения при дате в прошлом."""
        past_date = date.today() - timedelta(days=1)
        target_amount = Decimal('1000.00')
        current_savings = Decimal('0.00')

        with self.assertRaises(ValueError) as context:
            calculate_required_savings(
                target_amount=target_amount,
                target_date=past_date,
                current_savings=current_savings
            )

        self.assertIn('must be in the future', str(context.exception))

    def test_invalid_input_types(self):
        """Тестирование обработки некорректных типов данных."""
        future_date = date.today() + timedelta(days=30)

        # Проверка строковых значений сумм
        result = calculate_required_savings(
            target_amount="1000.00",
            target_date=future_date,
            current_savings="500.00"
        )

        self.assertEqual(result['target_amount'], '1000.00')
        self.assertEqual(result['current_savings'], '500.00')

        # Проверка строковой даты
        result = calculate_required_savings(
            target_amount=Decimal('1000.00'),
            target_date=future_date.isoformat(),
            current_savings=Decimal('500.00')
        )

        self.assertEqual(result['target_date'], future_date.isoformat())

        # Проверка некорректных значений
        with self.assertRaises(ValueError):
            calculate_required_savings(
                target_amount="not-a-number",
                target_date=future_date,
                current_savings=Decimal('500.00')
            )

        with self.assertRaises(ValueError):
            calculate_required_savings(
                target_amount=Decimal('1000.00'),
                target_date="not-a-date",
                current_savings=Decimal('500.00')
            )


if __name__ == '__main__':
    unittest.main()
