# main.py - Entry point of the FrameCamPi project
import threading
import time
from utils import load_config, setup_logging
from photoframe_tkinter import PhotoFrame
from voice_commands import listen_for_commands, process_command
from smile_detection import detect_smile_and_capture
from web_app import run_web_app
from photo_capture import CameraHandler  # CameraHandlerをインポート
import os
import logging



def command_listener(config):
    """音声コマンドをリスニングし、コマンドに応じた処理を実行する"""
    while True:
        command = listen_for_commands()
        if command:
            process_command(command, config)

def monitor_activity(config):
    """ユーザーのアクティビティを監視し、無操作時にフォトフレームモードに切り替える"""
    timeout = config['slideshow']['timeout']
    last_activity = time.time()

    def reset_timer():
        nonlocal last_activity
        last_activity = time.time()

    # アクティビティのリセット方法（例：キーボードやマウスのイベント）を実装する必要があります。
    # ここでは仮に音声コマンドリスナーがアクティビティの一部とします。
    while True:
        current_time = time.time()
        if current_time - last_activity > timeout:
            logging.info("無操作時間が設定値を超えたため、フォトフレームモードに切り替えます。")
            # フォトフレームモードをトリガーするロジックを実装
            # 例: イベントを発火する、フラグをセットするなど
            last_activity = current_time  # タイマーをリセット
        time.sleep(1)

def main():
    """システムのエントリーポイント。設定を読み込み、各スレッドを開始する。"""
    # スクリプトのディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ロギングの設定を初期化
    setup_logging(script_dir, log_file='debug.log')

    # config.yaml のパスを構築
    config_path = os.path.join(script_dir, 'config.yaml')  # config.yaml が src ディレクトリ内にある場合

    if not os.path.exists(config_path):
        logging.error(f"設定ファイルが見つかりません: {config_path}")
        sys.exit(1)

    # 設定ファイルをロード
    try:
        config = load_config(config_filename='config.yaml', env_filename='.env')
    except Exception as e:
        logging.error(f"設定ファイルの読み込みに失敗しました: {e}")
        sys.exit(1)

    timestamp = get_timestamp()

    # 写真保存ディレクトリを取得
    photo_directory = config.get('slideshow', {}).get('photos_directory', 'photos')

    # ディレクトリが相対パスの場合、スクリプトのディレクトリを基準にする
    photo_directory = os.path.join(script_dir, photo_directory)

    # ディレクトリが存在しない場合は作成
    try:
        os.makedirs(photo_directory, exist_ok=True)
        logging.info(f"写真保存ディレクトリ: {photo_directory}")
    except Exception as e:
        logging.error(f"写真保存ディレクトリの作成に失敗しました: {e}")
        sys.exit(1)

    # タイムスタンプ付きのファイル名を作成
    filename = f"{timestamp}.jpg"
    file_path = os.path.join(photo_directory, filename)

    # カメラハンドラーのインスタンスを作成
    camera_config = config.get('camera', {})
    camera_handler = CameraHandler(
        camera_index=camera_config.get('index', 0),
        countdown_time=camera_config.get('countdown_time', 3),
        preview_time=camera_config.get('preview_time', 3),
        photo_directory=photo_directory
    )

    # カメラキャプチャ機能を別スレッドで実行
    camera_thread = threading.Thread(
        target=camera_handler.capture_image_with_resized_window,
        args=(file_path,),
        daemon=True
    )
    camera_thread.start()

    # 音声コマンドリスニングのスレッド開始
    command_thread = threading.Thread(target=command_listener, args=(config,), daemon=True)
    command_thread.start()

    # アクティビティ監視のスレッド開始
    monitor_thread = threading.Thread(target=monitor_activity, args=(config,), daemon=True)
    monitor_thread.start()

    # 笑顔検出のスレッド開始（オプション）
    smile_detection_thread = threading.Thread(
        target=detect_smile_and_capture, 
        args=(0, config['slideshow']['photos_directory']), 
        daemon=True
    )
    smile_detection_thread.start()

    # ウェブアプリケーションのスレッド開始（オプション）
    web_app_thread = threading.Thread(target=run_web_app, args=(config,), daemon=True)
    web_app_thread.start()

    # Tkinterのメインループをメインスレッドで実行
    interval = config['slideshow']['interval']
    app = PhotoFrame(photo_directory, interval)
    app.mainloop()

if __name__ == "__main__":
    main()
