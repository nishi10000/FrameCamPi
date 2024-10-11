# main.py - Entry point of the FrameCamPi project
# main.py
import threading
import time
from utils import load_config
from photoframe_tkinter import PhotoFrame
from voice_commands import listen_for_commands, process_command
from smile_detection import detect_smile_and_capture
from web_app import run_web_app

def start_slideshow(config):
    """フォトフレームモードを開始し、スライドショーを実行する"""
    photo_directory = config['slideshow']['photos_directory']
    interval = config['slideshow']['interval']
    slideshow = PhotoFrame(photo_directory, interval)
    slideshow.mainloop()

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
            print("無操作時間が設定値を超えたため、フォトフレームモードに切り替えます。")
            start_slideshow(config)
            last_activity = current_time  # スライドショー開始後、タイマーをリセット
        time.sleep(1)

def main():
    """システムのエントリーポイント。設定を読み込み、各スレッドを開始する。"""
    config = load_config('src/config.yaml')

    # スライドショーのスレッド開始
    slideshow_thread = threading.Thread(target=start_slideshow, args=(config,), daemon=True)
    slideshow_thread.start()

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

    # メインスレッドは終了しないように待機
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("プログラムを終了します。")

if __name__ == "__main__":
    main()
