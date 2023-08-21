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

        peak_APM = max(self.apm_tracker.APM_list + [current_APM])  # Use max to safely handle empty lists
        peak_EAPM = max(self.apm_tracker.EAPM_list + [current_EAPM])

        average_APM = (self.apm_tracker.cumulative_actions + current_APM) / (
                    self.apm_tracker.intervals_since_start + 1) if self.apm_tracker.intervals_since_start != -1 else current_APM
        average_EAPM = (self.apm_tracker.cumulative_effective_actions + current_EAPM) / (
                    self.apm_tracker.intervals_since_start + 1) if self.apm_tracker.intervals_since_start != -1 else current_EAPM

        # Assert that both APM and EAPM are 1 for a single keypress
        self.assertEqual(current_APM, 1)
        self.assertEqual(current_EAPM, 1)

        # Assert peak values
        self.assertEqual(peak_APM, 1)
        self.assertEqual(peak_EAPM, 1)

        # Assert average values
        self.assertEqual(average_APM, 1)
        self.assertEqual(average_EAPM, 1)


if __name__ == "__main__":
    unittest.main()
