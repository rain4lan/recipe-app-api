"""
Test custom Django management commands.
"""

from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# Mock, adds a new parameter to the test methods
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for db if db is ready."""
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    # Path sleep method only for this test method
    # Argument order! Last patch first, from the inside out!
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for db when getting OperationalError"""
        # Found out by trial-and-error which errors
        # Calls  1-2: raise Psycop2Error - simulate PostgreSQL not yet up
        #   - OperationError->Psycopg2Error from Postgres
        # Calls 3-5: Raise 3 OperationalError - simulate PostgreSQL up,
        #   but test db not yet created -> OperationionalError from Django
        # Call 6: True: Simulate db up and running, ok
        patched_check.side_effect = \
            [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
