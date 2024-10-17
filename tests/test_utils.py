# tests/test_util.py
import sys
import os
import unittest
from unittest import mock
from datetime import datetime
import re
from unittest.mock import MagicMock, mock_open
import logging
import importlib

# srcディレクトリをインポートパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from utils import get_timestamp, get_screen_sizes, setup_logging

class TestGetTimestamp(unittest.TestCase):
    def test_format(self):
        """
        戻り値が 'YYYYMMDD_HHMMSS' の形式になっているか確認する。
        """
        timestamp = get_timestamp()
        pattern = r'^\d{8}_\d{6}$'  # 正規表現パターン: 8桁_6桁
        self.assertRegex(timestamp, pattern, f"Timestamp '{timestamp}' does not match the format 'YYYYMMDD_HHMMSS'")

    @mock.patch('utils.datetime')
    def test_correctness(self, mock_datetime):
        """
        関数が実行された時点の正確な日時を返しているか確認する。
        """
        fixed_datetime = datetime(2024, 4, 27, 15, 30, 45)
        mock_datetime.datetime.now.return_value = fixed_datetime
        mock_datetime.datetime.strftime = datetime.strftime  # 実際のstrftimeメソッドを使用

        timestamp = get_timestamp()
        expected = "20240427_153045"
        self.assertEqual(timestamp, expected, f"Expected '{expected}', got '{timestamp}'")

    @mock.patch('utils.datetime')
    def test_uniqueness(self, mock_datetime):
        """
        短時間に複数回実行した場合でも、異なるタイムスタンプが生成されることを確認する。
        """
        fixed_datetime1 = datetime(2024, 4, 27, 15, 30, 45)
        fixed_datetime2 = datetime(2024, 4, 27, 15, 30, 46)
        mock_datetime.datetime.now.side_effect = [fixed_datetime1, fixed_datetime2]

        timestamp1 = get_timestamp()
        timestamp2 = get_timestamp()

        self.assertNotEqual(timestamp1, timestamp2, "Timestamps should be unique on consecutive calls")

    @mock.patch('utils.datetime')
    def test_mocked_time_specific(self, mock_datetime):
        """
        モックを使用して、特定の日時での動作を確認する。
        """
        fixed_datetime = datetime(2024, 12, 31, 23, 59, 59)
        mock_datetime.datetime.now.return_value = fixed_datetime
        mock_datetime.datetime.strftime = datetime.strftime  # 実際のstrftimeメソッドを使用

        timestamp = get_timestamp()
        expected = "20241231_235959"
        self.assertEqual(timestamp, expected, f"Expected '{expected}', got '{timestamp}'")

class TestGetScreenSizes(unittest.TestCase):
    @mock.patch.dict(os.environ, {'DISPLAY': ':1.0'}, clear=True)
    @mock.patch('utils.get_monitors')
    def test_display_env_set(self, mock_get_monitors):
        """
        DISPLAY 環境変数が既に設定されている場合、変更されないことを確認。
        """
        # モックされたモニター情報を設定
        mock_monitor = mock.Mock()
        mock_monitor.name = "Monitor1"
        mock_monitor.width = 1920
        mock_monitor.height = 1080
        mock_get_monitors.return_value = [mock_monitor]

        # 関数の実行
        width, height = get_screen_sizes()

        # DISPLAY 環境変数が変更されていないことを確認
        self.assertEqual(os.environ.get('DISPLAY'), ':1.0', "DISPLAY environment variable should not be changed when already set.")
        # XAUTHORITY 環境変数が設定されていないことを確認
        self.assertNotIn('XAUTHORITY', os.environ, "XAUTHORITY should not be set when DISPLAY is already set.")

        # モニターの幅と高さが正しく返されていることを確認
        self.assertEqual(width, 1920)
        self.assertEqual(height, 1080)

    @mock.patch.dict(os.environ, {}, clear=True)
    @mock.patch('utils.get_monitors')
    def test_display_env_not_set(self, mock_get_monitors):
        """
        DISPLAY が未設定の場合、:0.0 に設定されることと、XAUTHORITY が正しく設定されることを確認。
        """
        # モックされたモニター情報を設定
        mock_monitor = mock.Mock()
        mock_monitor.name = "Monitor1"
        mock_monitor.width = 1920
        mock_monitor.height = 1080
        mock_get_monitors.return_value = [mock_monitor]

        # ログ出力をキャプチャ
        with self.assertLogs(level='DEBUG') as log:
            width, height = get_screen_sizes()

            # ログに期待されるメッセージが含まれていることを確認
            self.assertIn("no display found. Using :0.0", log.output[0])
            self.assertIn("DISPLAY環境変数を ':0.0' に設定しました。", log.output[1])

        # DISPLAY 環境変数が ':0.0' に設定されていることを確認
        self.assertEqual(os.environ.get('DISPLAY'), ':0.0', "DISPLAY environment variable should be set to ':0.0' when not initially set.")
        # XAUTHORITY 環境変数が正しく設定されていることを確認
        self.assertEqual(os.environ.get('XAUTHORITY'), '/home/sini/.Xauthority', "XAUTHORITY should be set to '/home/sini/.Xauthority' when DISPLAY was not set.")

        # モニターの幅と高さが正しく返されていることを確認
        self.assertEqual(width, 1920)
        self.assertEqual(height, 1080)

    @mock.patch('utils.get_monitors')
    def test_single_monitor(self, mock_get_monitors):
        """
        単一モニターの場合、正しい幅と高さが返されることを確認する。
        """
        # モックされたモニター情報を設定
        mock_monitor = mock.Mock()
        mock_monitor.name = "Monitor1"
        mock_monitor.width = 1920
        mock_monitor.height = 1080
        mock_get_monitors.return_value = [mock_monitor]

        # 関数の実行
        width, height = get_screen_sizes()

        # モニターの幅と高さが正しく返されていることを確認
        self.assertEqual(width, 1920, "Width should be 1920 for a single monitor.")
        self.assertEqual(height, 1080, "Height should be 1080 for a single monitor.")

    @mock.patch('utils.get_monitors')
    def test_multiple_monitors(self, mock_get_monitors):
        """
        複数モニターが接続されている場合、最初のモニターの情報が返されることを確認する。
        """
        # モックされた複数のモニター情報を設定
        mock_monitor1 = mock.Mock()
        mock_monitor1.name = "Monitor1"
        mock_monitor1.width = 1920
        mock_monitor1.height = 1080

        mock_monitor2 = mock.Mock()
        mock_monitor2.name = "Monitor2"
        mock_monitor2.width = 1280
        mock_monitor2.height = 720

        mock_get_monitors.return_value = [mock_monitor1, mock_monitor2]

        # 関数の実行
        width, height = get_screen_sizes()

        # 最初のモニターの幅と高さが返されていることを確認
        self.assertEqual(width, 1920, "Width should be 1920 for the first monitor.")
        self.assertEqual(height, 1080, "Height should be 1080 for the first monitor.")

    @mock.patch.dict(os.environ, {}, clear=True)
    @mock.patch('utils.get_monitors')
    def test_log_output(self, mock_get_monitors):
        """
        各ディスプレイの情報がログに正しく記録されていることを確認する。
        """
        # モックされたモニター情報を設定
        mock_monitor = mock.Mock()
        mock_monitor.name = "Monitor1"
        mock_monitor.width = 1920
        mock_monitor.height = 1080
        mock_get_monitors.return_value = [mock_monitor]

        # ログ出力をキャプチャ
        with self.assertLogs(level='DEBUG') as log:
            get_screen_sizes()

            # ログにモニター情報が含まれていることを確認
            self.assertIn(f"ディスプレイ {mock_monitor.name}: 幅={mock_monitor.width}, 高さ={mock_monitor.height}", log.output[-1],
                          "Monitor information should be logged correctly.")

    @mock.patch('utils.get_monitors', side_effect=Exception("Monitor detection failed"))
    def test_get_monitors_exception(self, mock_get_monitors):
        """
        get_monitors() が例外を投げた場合の挙動を確認する。
        """
        with self.assertRaises(Exception) as context:
            get_screen_sizes()
        self.assertIn("Monitor detection failed", str(context.exception), "Exception message should be propagated correctly.")    


if __name__ == '__main__':
    unittest.main()
