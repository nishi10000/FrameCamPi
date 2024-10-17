#utils.py #
import os
import yaml
from dotenv import load_dotenv
import re
from screeninfo import get_monitors
import logging
import datetime

def get_timestamp():
    """現在の日時を取得して、ファイル名に使用できる形式にフォーマットします。"""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def get_screen_sizes():
    """
    画面サイズを取得し、ログに記録します。
    DISPLAY 環境変数が設定されていない場合はデフォルト値を設定します。
    """
    if os.environ.get('DISPLAY', '') == '':
        logging.debug('no display found. Using :0.0')
        os.environ['DISPLAY'] = ':0.0'
        os.environ['XAUTHORITY'] = '/home/sini/.Xauthority'
        logging.debug("DISPLAY環境変数を ':0.0' に設定しました。")
    
    monitors = get_monitors()
    for monitor in monitors:
        logging.debug(f"ディスプレイ {monitor.name}: 幅={monitor.width}, 高さ={monitor.height}")
        print(f"ディスプレイ {monitor.name}: 幅={monitor.width}, 高さ={monitor.height}")
        return monitor.width, monitor.height
    
def setup_logging(script_dir, log_file='debug.log'):
    """
    ログ設定を初期化します。
    ログファイルはスクリプトのディレクトリ内の logs フォルダに保存されます。
    
    Args:
        script_dir (str): スクリプトのディレクトリパス。
        log_file (str, optional): ログファイル名。デフォルトは 'debug.log'。
    """
    try:
        log_directory = os.path.join(script_dir, 'logs')
        os.makedirs(log_directory, exist_ok=True)
    except OSError as e:
        print(f"Failed to create log directory: {e}")
        raise
    
    logging.basicConfig(
        filename=os.path.join(log_directory, log_file),
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(message)s'
    )

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
    load_dotenv(env_path, override=True)

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
    config = load_config('config.yaml')
    print(config)
