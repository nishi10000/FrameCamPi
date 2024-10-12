# src/utils.py

import os
import yaml
from dotenv import load_dotenv
import re

def load_config(config_filename='config.yaml', env_filename='.env'):
    """
    config.yaml ファイルを読み込み、環境変数を展開して設定を返す。

    Args:
        config_filename (str): 設定ファイル名。デフォルトは 'config.yaml'。
        env_filename (str): .env ファイル名。デフォルトは '.env'。

    Returns:
        dict: 設定内容を含む辞書。
    """
    # 現在のスクリプトのディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # プロジェクトルートディレクトリを取得（.env がここにある）
    project_root = os.path.abspath(os.path.join(script_dir, os.pardir))

    # .env ファイルのパスを構築して読み込む
    env_path = os.path.join(project_root, env_filename)
    load_dotenv(env_path)

    # config.yaml ファイルのパスを構築
    config_path = os.path.join(script_dir, config_filename)

    # config.yaml が存在するか確認
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"No such file or directory: '{config_path}'")

    # YAMLファイルの読み込み
    with open(config_path, 'r', encoding='utf-8') as file:
        config_text = file.read()

    # 環境変数のプレースホルダ (${VARIABLE_NAME}) を置換
    pattern = re.compile(r'\$\{(\w+)\}')  # ${VARIABLE_NAME} を検出する正規表現パターン

    def replace_env_variables(match):
        var_name = match.group(1)  # 環境変数名を取得
        return os.getenv(var_name, match.group(0))  # 環境変数を取得、見つからなければそのまま

    # プレースホルダを環境変数で置換
    config_text = pattern.sub(replace_env_variables, config_text)

    # YAMLとしてパース
    config = yaml.safe_load(config_text)

    return config

# テスト用の実行例
if __name__ == "__main__":
    config = load_config('src/config.yaml')
    print(config)
