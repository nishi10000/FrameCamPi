# tests/test_utils1.py
import sys
import os
import unittest
from unittest import mock
import logging
import tempfile
import importlib

# srcディレクトリをインポートパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from utils import setup_logging  # setup_logging をインポート

class TestSetupLogging(unittest.TestCase):
    def setUp(self):
        # 一時ディレクトリの作成
        self.temp_dir = tempfile.TemporaryDirectory()
        self.script_dir = self.temp_dir.name
        self.log_file = 'test_debug.log'

    def tearDown(self):
        # 一時ディレクトリのクリーンアップ
        self.temp_dir.cleanup()
        logging.shutdown()
        importlib.reload(sys.modules['utils'])  # utils モジュールを再読み込みして設定をリセット

    @mock.patch('utils.logging.basicConfig')
    @mock.patch('utils.os.makedirs')
    @mock.patch('utils.os.path.exists')
    def test_logs_directory_creation_when_not_exists(self, mock_exists, mock_makedirs, mock_basicConfig):
        """
        logs フォルダが存在しない場合、自動的に作成されることを確認する。
        """
        # logs フォルダが存在しないと仮定
        mock_exists.return_value = False

        setup_logging(self.script_dir, self.log_file)

        # os.makedirs が正しく呼び出されたことを確認（exist_ok=True を含む）
        expected_logs_dir = os.path.join(self.script_dir, 'logs')
        mock_makedirs.assert_called_once_with(expected_logs_dir, exist_ok=True)

        # logging.basicConfig が正しく呼び出されたことを確認
        expected_log_path = os.path.join(expected_logs_dir, self.log_file)
        mock_basicConfig.assert_called_once_with(
            filename=expected_log_path,
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )

    @mock.patch('utils.logging.basicConfig')
    @mock.patch('utils.os.makedirs')
    @mock.patch('utils.os.path.exists')
    def test_logs_directory_creation_when_exists(self, mock_exists, mock_makedirs, mock_basicConfig):
        """
        logs フォルダが既に存在する場合でも、os.makedirs が正しく呼び出されることを確認する。
        """
        # logs フォルダが存在すると仮定
        mock_exists.return_value = True

        setup_logging(self.script_dir, self.log_file)

        # os.makedirs が正しく呼び出されたことを確認（exist_ok=True を含む）
        expected_logs_dir = os.path.join(self.script_dir, 'logs')
        mock_makedirs.assert_called_once_with(expected_logs_dir, exist_ok=True)

        # logging.basicConfig が正しく呼び出されたことを確認
        expected_log_path = os.path.join(expected_logs_dir, self.log_file)
        mock_basicConfig.assert_called_once_with(
            filename=expected_log_path,
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )

    @mock.patch('utils.logging.basicConfig')
    @mock.patch('utils.os.makedirs')
    @mock.patch('utils.os.path.exists')
    def test_log_file_creation(self, mock_exists, mock_makedirs, mock_basicConfig):
        """
        指定された log_file 名でログファイルが正しく作成されることを確認する。
        """
        # logs フォルダが存在しないと仮定
        mock_exists.return_value = False

        setup_logging(self.script_dir, self.log_file)

        # logging.basicConfig が正しく呼び出されたことを確認
        expected_log_path = os.path.join(self.script_dir, 'logs', self.log_file)
        mock_basicConfig.assert_called_once_with(
            filename=expected_log_path,
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )

    @mock.patch('utils.logging.basicConfig')
    @mock.patch('utils.os.makedirs')
    @mock.patch('utils.os.path.exists')
    def test_logging_level_set_to_debug(self, mock_exists, mock_makedirs, mock_basicConfig):
        """
        ログレベルが DEBUG に設定されていることを確認する。
        """
        # logs フォルダが存在しないと仮定
        mock_exists.return_value = False

        with self.assertLogs(level='DEBUG') as log:
            setup_logging(self.script_dir, self.log_file)
            logging.debug('This is a debug message.')

        # logging.basicConfig が正しく呼び出されたことを確認
        expected_log_path = os.path.join(self.script_dir, 'logs', self.log_file)
        mock_basicConfig.assert_called_once_with(
            filename=expected_log_path,
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )

        # ログレベルが DEBUG であることを確認
        self.assertIn('DEBUG:root:This is a debug message.', log.output)

    @mock.patch('utils.logging.basicConfig')
    @mock.patch('utils.os.makedirs')
    @mock.patch('utils.os.path.exists')
    def test_logging_format(self, mock_exists, mock_makedirs, mock_basicConfig):
        """
        ログメッセージが指定されたフォーマット ('%(asctime)s %(levelname)s:%(message)s') で記録されることを確認する。
        """
        # logs フォルダが存在しないと仮定
        mock_exists.return_value = False

        setup_logging(self.script_dir, self.log_file)

        # logging.basicConfig が正しく呼び出されたことを確認
        expected_log_path = os.path.join(self.script_dir, 'logs', self.log_file)
        mock_basicConfig.assert_called_once_with(
            filename=expected_log_path,
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )

    @mock.patch('utils.logging.basicConfig', side_effect=OSError("Cannot create directory"))
    @mock.patch('utils.os.makedirs')
    @mock.patch('utils.os.path.exists')
    def test_invalid_script_dir_handling(self, mock_exists, mock_makedirs, mock_basicConfig):
        """
        存在しないディレクトリパスが渡された場合の挙動を確認する。
        """
        # logs フォルダが存在しないと仮定し、logging.basicConfig が例外を投げる
        mock_exists.return_value = False

        with self.assertRaises(OSError) as context:
            setup_logging(self.script_dir, self.log_file)

        self.assertIn("Cannot create directory", str(context.exception), "Should raise OSError when directory creation fails.")

    @mock.patch('utils.logging.basicConfig')
    @mock.patch('utils.os.makedirs')
    @mock.patch('utils.os.path.exists')
    def test_default_log_file(self, mock_exists, mock_makedirs, mock_basicConfig):
        """
        log_file 引数を指定しなかった場合、デフォルトの 'debug.log' が使用されることを確認する。
        """
        mock_exists.return_value = False

        setup_logging(self.script_dir)  # log_file を指定しない

        # logging.basicConfig が 'debug.log' で呼び出されたことを確認
        expected_log_path = os.path.join(self.script_dir, 'logs', 'debug.log')
        mock_basicConfig.assert_called_once_with(
            filename=expected_log_path,
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )

    @mock.patch('utils.logging.basicConfig')
    @mock.patch('utils.os.makedirs')
    @mock.patch('utils.os.path.exists')
    def test_multiple_calls_setup_logging(self, mock_exists, mock_makedirs, mock_basicConfig):
        """
        setup_logging を複数回呼び出した場合でも、ログ設定が正しく更新されることを確認する。
        """
        mock_exists.return_value = False

        # 初回の呼び出し
        setup_logging(self.script_dir, 'first.log')
        expected_log_path1 = os.path.join(self.script_dir, 'logs', 'first.log')
        mock_basicConfig.assert_called_with(
            filename=expected_log_path1,
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )

        # ハンドラのリセット
        mock_basicConfig.reset_mock()

        # 二回目の呼び出し
        setup_logging(self.script_dir, 'second.log')
        expected_log_path2 = os.path.join(self.script_dir, 'logs', 'second.log')
        mock_basicConfig.assert_called_with(
            filename=expected_log_path2,
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )

if __name__ == '__main__':
    unittest.main()
