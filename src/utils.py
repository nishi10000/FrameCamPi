# utils.py - Utility functions used across the FrameCamPi project
# src/utils.py

import os
import yaml
from dotenv import load_dotenv
import re

def load_config(config_path):
    """
    config.yaml ファイルを読み込み、環境変数を展開して設定を返す。
    
    Args:
        config_path (str): 設定ファイルへのパス。
    
    Returns:
        dict: 設定内容を含む辞書。
    """
    # .env ファイルの読み込み
    load_dotenv()

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
