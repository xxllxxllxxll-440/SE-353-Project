"""Small offline unit tests; no database connection or API credits needed.
Run after installing requirements: python -m unittest test_database_logic.py
"""
import unittest
from unittest.mock import patch
from decimal import Decimal
import database


class FakeCursor:
    def __init__(self, fail_at_purchase=False):
        self.fail_at_purchase = fail_at_purchase
        self.calls = []
        self.lastrowid = 40
        self.rowcount = 1

    def execute(self, statement, params=()):
        self.calls.append((statement, params))
        if self.fail_at_purchase and 'INSERT INTO purchases' in statement:
            raise RuntimeError('duplicate invoice')
        if 'INSERT INTO purchases' in statement:
            self.lastrowid = 45
        elif 'INSERT INTO purchase_items' in statement:
            self.lastrowid = 46

    def fetchone(self):
        return {'item_id': 1}

    def close(self):
        pass


class FakeConnection:
    def __init__(self, fail=False):
        self.cur = FakeCursor(fail)
        self.committed = False
        self.rolled_back = False
        self.closed = False
        self.started = False

    def cursor(self, dictionary=False):
        return self.cur

    def start_transaction(self):
        self.started = True

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


class DatabaseLogicTests(unittest.TestCase):
    def test_money(self):
        self.assertEqual(database.money('3.505'), Decimal('3.51'))
        with self.assertRaises(ValueError): database.money('-2')
        with self.assertRaises(ValueError): database.money('nan')

    def test_bad_lines_do_not_connect(self):
        with patch.object(database, 'get_connection') as c:
            with self.assertRaises(ValueError):
                database.record_purchase(1, 'ABC', '2026-10-12', [])
            with self.assertRaises(ValueError):
                database.record_purchase(1, 'ABC', '2026-10-12', [
                    {'item_id': 1, 'quantity': '1', 'unit_cost': 2},
                    {'item_id': 1, 'quantity': '2', 'unit_cost': 2}])
            c.assert_not_called()

    def test_success_commits_purchase_stock_and_expense(self):
        fake = FakeConnection()
        with patch.object(database, 'get_connection', return_value=fake):
            result = database.record_purchase(1, 'INV-123', '2026-10-12', [
                {'item_id': 1, 'quantity': '5', 'unit_cost': '3.50'}])
        self.assertTrue(fake.started)
        self.assertTrue(fake.committed)
        self.assertFalse(fake.rolled_back)
        self.assertTrue(fake.closed)
        self.assertEqual(result['total_amount'], '17.50')
        sql = '\n'.join(x[0] for x in fake.cur.calls)
        self.assertIn('INSERT INTO purchases', sql)
        self.assertIn('INSERT INTO purchase_items', sql)
        self.assertIn('UPDATE inventory_items', sql)
        self.assertIn('INSERT INTO inventory_transactions', sql)
        self.assertIn('INSERT INTO expenses', sql)

    def test_failed_purchase_rolls_back(self):
        fake = FakeConnection(fail=True)
        with patch.object(database, 'get_connection', return_value=fake):
            with self.assertRaises(RuntimeError):
                database.record_purchase(1, 'DUPLICATE', '2026-10-12', [
                    {'item_id': 1, 'quantity': '5', 'unit_cost': '3.50'}])
        self.assertTrue(fake.rolled_back)
        self.assertFalse(fake.committed)
        self.assertTrue(fake.closed)


if __name__ == '__main__':
    unittest.main()
