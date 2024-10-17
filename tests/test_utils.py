# tests/test_util.py
import sys
import os
import unittest
from unittest import mock
from datetime import datetime
import re

# srcディレクトリをインポートパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from utils import get_timestamp

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

if __name__ == '__main__':
    unittest.main()
