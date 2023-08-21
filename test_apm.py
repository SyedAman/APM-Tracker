import unittest
from unittest.mock import MagicMock
from apm_tracker import ApmTracker

class TestApmTracker(unittest.TestCase):

    def setUp(self):
        self.apm_tracker = ApmTracker()

    def test_single_keypress(self):
        # Mock a single keyboard press
        self.apm_tracker.on_keyboard_press(None)  # Passing `None` because the key isn't checked in the method

        # Simulate the update_display method without drawing the GUI
        current_APM = self.apm_tracker.keystrokes + self.apm_tracker.mouse_clicks
        current_EAPM = self.apm_tracker.effective_actions

        # Assert that both APM and EAPM are 1 for a single keypress
        self.assertEqual(current_APM, 1)
        self.assertEqual(current_EAPM, 1)


if __name__ == "__main__":
    unittest.main()
