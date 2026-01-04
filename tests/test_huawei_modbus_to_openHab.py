"""This file contains the tests for the huawei_modbus_to_openHab.py file."""

import datetime
import unittest
from unittest.mock import patch

from huawei_modbus_to_openHab import (
    OH_EXTRA_ITEM_MAP,
    USE_MAX,
    USE_MIN,
    check_max_day,
    check_max_month,
    check_min_day,
    check_min_max,
    check_min_month,
    sum_up,
    sum_up_day,
    sum_up_month,
)


class TestCheckMinMax(unittest.TestCase):
    """This class contains the tests for the check_min_max function."""

    def setUp(self):
        OH_EXTRA_ITEM_MAP.clear()

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_check_min_max_initial(self, mock_oh_item_command):
        """Test check_min_max function for initial call."""
        oh_item_name = "example_item"
        oh_state = 10.5
        time_value = 5

        check_min_max(oh_item_name, oh_state, time_value, USE_MAX)
        mock_oh_item_command.assert_called_once()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], time_value)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], oh_state)

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_check_min_max_no_reset_new_value(self, mock_oh_item_command):
        """Test check_min_max function when reset is not required."""
        oh_item_name = "example_item"
        oh_state = 10.5
        time_value = 5

        OH_EXTRA_ITEM_MAP[oh_item_name] = {"time": 3, "value": 8.5}

        check_min_max(oh_item_name, oh_state, time_value, USE_MAX)
        mock_oh_item_command.assert_not_called()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], time_value)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], oh_state)

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_check_min_max_no_reset_no_new_value(self, mock_oh_item_command):
        """Test check_min_max function when reset is not required."""
        oh_item_name = "example_item"
        oh_old = 8.5
        oh_state = 3.5
        time_value = 5

        OH_EXTRA_ITEM_MAP[oh_item_name] = {"time": 3, "value": oh_old}

        check_min_max(oh_item_name, oh_state, time_value, USE_MAX)
        mock_oh_item_command.assert_not_called()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], time_value)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], oh_old)

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_check_min_max_use_min(self, mock_oh_item_command):
        """Test check_min_max function with USE_MIN."""
        oh_item_name = "example_item"
        old_value = 8.5
        oh_state = 10.5
        time_value = 5

        OH_EXTRA_ITEM_MAP[oh_item_name] = {"time": 3, "value": old_value}

        check_min_max(oh_item_name, oh_state, time_value, USE_MIN)
        mock_oh_item_command.assert_not_called()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], 5)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], old_value)

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_check_min_max_reset_max_data(self, mock_oh_item_command):
        """Test check_min_max function with USE_MIN."""
        oh_item_name = "example_item"
        old_value = 8.5
        oh_state = 1.5
        time_value = 1

        OH_EXTRA_ITEM_MAP[oh_item_name] = {"time": 3, "value": old_value}

        check_min_max(oh_item_name, oh_state, time_value, USE_MAX)
        mock_oh_item_command.assert_called_once()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], time_value)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], oh_state)

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_check_min_max_reset_min_data(self, mock_oh_item_command):
        """Test check_min_max function with USE_MIN."""
        oh_item_name = "example_item"
        old_value = 8.5
        oh_state = 10.5
        time_value = 1

        OH_EXTRA_ITEM_MAP[oh_item_name] = {"time": 3, "value": old_value}

        check_min_max(oh_item_name, oh_state, time_value, USE_MIN)
        mock_oh_item_command.assert_called_once()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], time_value)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], oh_state)


class TestCheckMinMonth(unittest.TestCase):
    """This class contains the tests for the check_min_month function."""

    @patch("huawei_modbus_to_openHab.check_min_max")
    def test_check_min_month(self, mock_check_min_max):
        """This function tests the check_min_month function."""
        oh_item_name = "example_item"
        oh_state = "10.5"
        day = datetime.datetime.now().day

        check_min_month(oh_item_name, oh_state)

        mock_check_min_max.assert_called_with("example_item_Min_Month", 10.5, day, USE_MIN)


class TestCheckMaxMonth(unittest.TestCase):
    """This class contains the tests for the check_max_month function."""

    @patch("huawei_modbus_to_openHab.check_min_max")
    def test_check_max_month(self, mock_check_min_max):
        """This function tests the check_max_month function."""
        oh_item_name = "example_item"
        oh_state = "10.5"

        check_max_month(oh_item_name, oh_state)

        day = datetime.datetime.now().day
        mock_check_min_max.assert_called_with("example_item_Max_Month", 10.5, day, USE_MAX)


class TestCheckMinDay(unittest.TestCase):
    """This class contains the tests for the check_min_day function."""

    @patch("huawei_modbus_to_openHab.check_min_max")
    def test_check_min_day(self, mock_check_min_max):
        """This function tests the check_min_day function."""
        oh_item_name = "example_item"
        oh_state = "10.5"

        check_min_day(oh_item_name, oh_state)

        hour = datetime.datetime.now().hour
        mock_check_min_max.assert_called_with("example_item_Min_Day", 10.5, hour, USE_MIN)


class TestCheckMaxDay(unittest.TestCase):
    """This class contains the tests for the check_max_day function."""

    @patch("huawei_modbus_to_openHab.check_min_max")
    def test_check_max_day(self, mock_check_min_max):
        """This function tests the check_max_day function."""
        oh_item_name = "example_item"
        oh_state = "10.5"

        check_max_day(oh_item_name, oh_state)

        hour = datetime.datetime.now().hour
        mock_check_min_max.assert_called_with("example_item_Max_Day", 10.5, hour, USE_MAX)


if __name__ == "__main__":
    unittest.main()

""" This file contains the tests for the huawei_modbus_to_openHab.py file. """
import unittest
from unittest.mock import patch


class TestCheckMinMax(unittest.TestCase):
    """This class contains the tests for the check_min_max function."""

    def setUp(self):
        OH_EXTRA_ITEM_MAP.clear()

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_check_min_max_initial(self, mock_oh_item_command):
        """Test check_min_max function for initial call."""
        oh_item_name = "example_item"
        oh_state = 10.5
        time_value = 5

        check_min_max(oh_item_name, oh_state, time_value, USE_MAX)
        mock_oh_item_command.assert_called_once()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], time_value)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], oh_state)

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_check_min_max_no_reset_new_value(self, mock_oh_item_command):
        """Test check_min_max function when reset is not required."""
        oh_item_name = "example_item"
        oh_state = 10.5
        time_value = 5

        OH_EXTRA_ITEM_MAP[oh_item_name] = {"time": 3, "value": 8.5}

        check_min_max(oh_item_name, oh_state, time_value, USE_MAX)
        mock_oh_item_command.assert_not_called()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], time_value)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], oh_state)

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_check_min_max_no_reset_no_new_value(self, mock_oh_item_command):
        """Test check_min_max function when reset is not required."""
        oh_item_name = "example_item"
        oh_old = 8.5
        oh_state = 3.5
        time_value = 5

        OH_EXTRA_ITEM_MAP[oh_item_name] = {"time": 3, "value": oh_old}

        check_min_max(oh_item_name, oh_state, time_value, USE_MAX)
        mock_oh_item_command.assert_not_called()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], time_value)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], oh_old)

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_check_min_max_use_min(self, mock_oh_item_command):
        """Test check_min_max function with USE_MIN."""
        oh_item_name = "example_item"
        old_value = 8.5
        oh_state = 10.5
        time_value = 5

        OH_EXTRA_ITEM_MAP[oh_item_name] = {"time": 3, "value": old_value}

        check_min_max(oh_item_name, oh_state, time_value, USE_MIN)
        mock_oh_item_command.assert_not_called()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], 5)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], old_value)

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_check_min_max_reset_max_data(self, mock_oh_item_command):
        """Test check_min_max function with USE_MIN."""
        oh_item_name = "example_item"
        old_value = 8.5
        oh_state = 1.5
        time_value = 1

        OH_EXTRA_ITEM_MAP[oh_item_name] = {"time": 3, "value": old_value}

        check_min_max(oh_item_name, oh_state, time_value, USE_MAX)
        mock_oh_item_command.assert_called_once()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], time_value)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], oh_state)

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_check_min_max_reset_min_data(self, mock_oh_item_command):
        """Test check_min_max function with USE_MIN."""
        oh_item_name = "example_item"
        old_value = 8.5
        oh_state = 10.5
        time_value = 1

        OH_EXTRA_ITEM_MAP[oh_item_name] = {"time": 3, "value": old_value}

        check_min_max(oh_item_name, oh_state, time_value, USE_MIN)
        mock_oh_item_command.assert_called_once()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], time_value)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], oh_state)


class TestCheckMinMonth(unittest.TestCase):
    """This class contains the tests for the check_min_month function."""

    @patch("huawei_modbus_to_openHab.check_min_max")
    def test_check_min_month(self, mock_check_min_max):
        """This function tests the check_min_month function."""
        oh_item_name = "example_item"
        oh_state = "10.5"
        day = datetime.datetime.now().day

        check_min_month(oh_item_name, oh_state)

        mock_check_min_max.assert_called_with("example_item_Min_Month", 10.5, day, USE_MIN)


class TestCheckMaxMonth(unittest.TestCase):
    """This class contains the tests for the check_max_month function."""

    @patch("huawei_modbus_to_openHab.check_min_max")
    def test_check_max_month(self, mock_check_min_max):
        """This function tests the check_max_month function."""
        oh_item_name = "example_item"
        oh_state = "10.5"

        check_max_month(oh_item_name, oh_state)

        day = datetime.datetime.now().day
        mock_check_min_max.assert_called_with("example_item_Max_Month", 10.5, day, USE_MAX)


class TestCheckMinDay(unittest.TestCase):
    """This class contains the tests for the check_min_day function."""

    @patch("huawei_modbus_to_openHab.check_min_max")
    def test_check_min_day(self, mock_check_min_max):
        """This function tests the check_min_day function."""
        oh_item_name = "example_item"
        oh_state = "10.5"

        check_min_day(oh_item_name, oh_state)

        hour = datetime.datetime.now().hour
        mock_check_min_max.assert_called_with("example_item_Min_Day", 10.5, hour, USE_MIN)


class TestCheckMaxDay(unittest.TestCase):
    """This class contains the tests for the check_max_day function."""

    @patch("huawei_modbus_to_openHab.check_min_max")
    def test_check_max_day(self, mock_check_min_max):
        """This function tests the check_max_day function."""
        oh_item_name = "example_item"
        oh_state = "10.5"

        check_max_day(oh_item_name, oh_state)

        hour = datetime.datetime.now().hour
        mock_check_min_max.assert_called_with("example_item_Max_Day", 10.5, hour, USE_MAX)


class TestSumUpMonth(unittest.TestCase):
    """This class contains the tests for the sum_up_month function."""

    @patch("huawei_modbus_to_openHab.sum_up")
    def test_sum_up_month(self, mock_sum_up):
        """This function tests the sum_up_month function."""
        oh_item_name = "example_item"
        oh_state = "10.5"
        day = datetime.datetime.now().day

        sum_up_month(oh_item_name, oh_state)

        mock_sum_up.assert_called_with("example_item_Sum_Month", 10.5, day)


class TestSumUpDay(unittest.TestCase):
    """This class contains the tests for the sum_up_day function."""

    @patch("huawei_modbus_to_openHab.sum_up")
    def test_sum_up_day(self, mock_sum_up):
        """Test sum_up_day function."""
        oh_item_name = "example_item"
        oh_state = "10.5"

        hour = datetime.datetime.now().hour
        oh_item_sum_day_name = oh_item_name + "_Sum_Day"

        sum_up_day(oh_item_name, oh_state)

        mock_sum_up.assert_called_with(oh_item_sum_day_name, 10.5, hour)


class TestSumUp(unittest.TestCase):
    """This class contains the tests for the sum_up function."""

    def setUp(self):
        OH_EXTRA_ITEM_MAP.clear()

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_sum_up_initial(self, mock_oh_item_command):
        """Test sum_up function for initial call."""
        oh_item_name = "example_item"
        oh_state = 10.5
        time_value = 5

        sum_up(oh_item_name, oh_state, time_value)
        mock_oh_item_command.assert_called_once()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], time_value)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], oh_state)

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_sum_up_no_reset(self, mock_oh_item_command):
        """Test sum_up function when reset is not required."""
        oh_item_name = "example_item"
        oh_state = 10.5
        time_value = 5

        OH_EXTRA_ITEM_MAP[oh_item_name] = {"time": 3, "value": 8.5}

        sum_up(oh_item_name, oh_state, time_value)
        mock_oh_item_command.assert_not_called()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], time_value)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], 19.0)

    @patch("huawei_modbus_to_openHab.oh_item_command", return_value=0)
    def test_sum_up_reset(self, mock_oh_item_command):
        """Test sum_up function with reset."""
        oh_item_name = "example_item"
        oh_state = 10.5
        time_value = 1

        OH_EXTRA_ITEM_MAP[oh_item_name] = {"time": 3, "value": 8.5}

        sum_up(oh_item_name, oh_state, time_value)
        mock_oh_item_command.assert_called_once()

        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["time"], time_value)
        self.assertEqual(OH_EXTRA_ITEM_MAP[oh_item_name]["value"], oh_state)


if __name__ == "__main__":
    unittest.main()
