# tests/test_utils2.py
import sys
import os
import unittest
from unittest.mock import patch
import tempfile
import importlib
import yaml
from dotenv import load_dotenv
from contextlib import contextmanager

# srcディレクトリをインポートパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from utils import load_config  # load_config をインポート


class TestLoadConfig(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None  # 差分を全て表示する

        # 一時ディレクトリの作成
        self.temp_dir = tempfile.TemporaryDirectory()
        self.script_dir = self.temp_dir.name  # 一時ディレクトリを script_dir とする
        self.project_root = os.path.abspath(os.path.join(self.script_dir, os.pardir))  # 一時ディレクトリの親を project_root とする
        self.config_filename = 'config.yaml'
        self.env_filename = '.env'
        self.config_path = os.path.join(self.script_dir, self.config_filename)
        self.env_path = os.path.join(self.project_root, self.env_filename)

        # デフォルトの config.yaml と .env ファイルを作成
        self.default_config_yaml = """# config.yaml: プロジェクト全体で使用される設定値を管理する設定ファイル
database:
  host: ${DB_HOST}
  port: ${DB_PORT}
"""
        self.default_env = "DB_HOST=localhost\nDB_PORT=5432\n"

        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write(self.default_config_yaml)

        with open(self.env_path, 'w', encoding='utf-8') as f:
            f.write(self.default_env)

    def tearDown(self):
        # 一時ディレクトリのクリーンアップ
        self.temp_dir.cleanup()

        # 'utils' モジュールを再読み込みしてパッチの影響をリセット
        if 'utils' in sys.modules:
            importlib.reload(sys.modules['utils'])

    @contextmanager
    def mock_paths(self):
        """
        Apply patches for os.path.abspath, os.path.dirname, and load_dotenv.
        This method is a context manager.
        """
        patcher_abspath = patch('utils.os.path.abspath')
        patcher_dirname = patch('utils.os.path.dirname')
        patcher_load_dotenv = patch('utils.load_dotenv')

        mock_abspath = patcher_abspath.start()
        mock_dirname = patcher_dirname.start()
        mock_load_dotenv = patcher_load_dotenv.start()

        try:
            def fake_abspath_side_effect(path):
                if path.endswith('utils.py'):
                    return os.path.join(self.script_dir, 'utils.py')
                elif path == os.path.join(self.script_dir, os.pardir):
                    return self.project_root
                elif path == self.env_path:
                    return self.env_path
                elif path == self.config_path:
                    return self.config_path
                else:
                    return os.path.abspath(path)

            def fake_dirname_side_effect(path):
                if path == os.path.join(self.script_dir, 'utils.py'):
                    return self.script_dir
                elif path == self.project_root:
                    return self.project_root
                else:
                    return os.path.dirname(path)

            mock_abspath.side_effect = fake_abspath_side_effect
            mock_dirname.side_effect = fake_dirname_side_effect

            # Allow actual load_dotenv to be called
            mock_load_dotenv.side_effect = lambda path, override: load_dotenv(path, override=override)

            yield
        finally:
            patcher_abspath.stop()
            patcher_dirname.stop()
            patcher_load_dotenv.stop()

    def test_basic_load_config_with_env_variables(self):
        with self.mock_paths():
            # 'utils' モジュールが既にインポートされている場合は削除
            if 'utils' in sys.modules:
                del sys.modules['utils']

            # 関数の呼び出し
            config = load_config(config_filename=self.config_filename, env_filename=self.env_filename)

            # 期待される結果（'port' を整数に修正）
            expected_config = {
                'database': {
                    'host': 'localhost',
                    'port': 5432  # 整数に修正
                }
            }

            # 結果の検証
            self.assertEqual(config, expected_config)

    def test_missing_env_file(self):
        with self.mock_paths():
            # 'utils' モジュールが既にインポートされている場合は削除
            if 'utils' in sys.modules:
                del sys.modules['utils']

            # .env ファイルを削除して、存在しない状態をシミュレート
            os.remove(self.env_path)

            # 関数の呼び出しと例外の検証
            with self.assertRaises(FileNotFoundError) as context:
                load_config(config_filename=self.config_filename, env_filename=self.env_filename)

            self.assertIn('.env', str(context.exception))

    def test_invalid_yaml(self):
        with self.mock_paths():
            # 'utils' モジュールが既にインポートされている場合は削除
            if 'utils' in sys.modules:
                del sys.modules['utils']

            # 無効な YAML を含む config.yaml を作成
            invalid_yaml = "database:\n  host: ${DB_HOST}\n  port: [INVALID YAML\n"  # 閉じ括弧が欠けているリスト
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(invalid_yaml)

            # yaml.YAMLError が発生することを確認
            with self.assertRaises(yaml.YAMLError):
                load_config(config_filename=self.config_filename, env_filename=self.env_filename)

    def test_missing_config_file(self):
        with self.mock_paths():
            # 'utils' モジュールが既にインポートされている場合は削除
            if 'utils' in sys.modules:
                del sys.modules['utils']

            # config.yaml ファイルを削除して、存在しない状態をシミュレート
            os.remove(self.config_path)

            # 関数の呼び出しと例外の検証
            with self.assertRaises(FileNotFoundError) as context:
                load_config(config_filename=self.config_filename, env_filename=self.env_filename)

            self.assertIn('config.yaml', str(context.exception))

    def test_missing_env_variables(self):
        with self.mock_paths():
            # 'utils' モジュールが既にインポートされている場合は削除
            if 'utils' in sys.modules:
                del sys.modules['utils']

            # 完全な config.yaml を作成（インデントを修正）
            complete_config_yaml = """# config.yaml: プロジェクト全体で使用される設定値を管理する設定ファイル
slideshow:
  interval: ${SLIDESHOW_INTERVAL}  # 表示間隔（ミリ秒）
  timeout: ${SLIDESHOW_TIMEOUT}    # 無操作時間（秒）
  photos_directory: ${SLIDESHOW_PHOTOS_DIRECTORY}  # フォトディレクトリのパス

camera:
  resolution: ${CAMERA_RESOLUTION}

samba:
  user: ${SAMBA_USER}
  password: ${SAMBA_PASSWORD}

flask:
  host: ${FLASK_HOST}
  port: ${FLASK_PORT}
  debug: ${FLASK_DEBUG}

environment: ${ENVIRONMENT}
"""
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(complete_config_yaml)

            # .env ファイルから一部の環境変数を削除（例: SLIDESHOW_INTERVAL、SAMBA_USER、FLASK_DEBUG などを削除）
            partial_env = """DB_HOST=localhost
DB_PORT=5432
"""
            with open(self.env_path, 'w', encoding='utf-8') as f:
                f.write(partial_env)  # 必要な変数だけ残す

            # 関数の呼び出し
            config = load_config(config_filename=self.config_filename, env_filename=self.env_filename)

            # 実際の config を出力して確認（デバッグ用）
            print("Actual config:", config)

            # 期待される結果（環境変数が設定されていない場合はプレースホルダが残る）
            expected_config = {
                'slideshow': {
                    'interval': '${SLIDESHOW_INTERVAL}',      # 環境変数が設定されていない場合はそのまま
                    'timeout': '${SLIDESHOW_TIMEOUT}',
                    'photos_directory': '${SLIDESHOW_PHOTOS_DIRECTORY}'
                },
                'camera': {
                    'resolution': '${CAMERA_RESOLUTION}'      # 環境変数が設定されていない場合はそのまま
                },
                'samba': {
                    'user': '${SAMBA_USER}',                  # 環境変数が設定されていない場合はそのまま
                    'password': '${SAMBA_PASSWORD}'
                },
                'flask': {
                    'host': '${FLASK_HOST}',
                    'port': '${FLASK_PORT}',
                    'debug': '${FLASK_DEBUG}'                 # プレースホルダがそのまま残る
                },
                'environment': '${ENVIRONMENT}'                # 環境変数が設定されていない場合はそのまま
            }

            # 結果の検証
            self.assertEqual(config, expected_config)


# テストの実行
if __name__ == '__main__':
    unittest.main()
