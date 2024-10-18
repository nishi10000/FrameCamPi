# main_test.py

import os
from utils import load_config, setup_logging, get_screen_sizes,get_timestamp
from photoframe_tkinter import PhotoFrame
import logging
import photo_capture

def main():
    """
    PhotoFrame クラスをテストするエントリーポイント。
    """
    # スクリプトのディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ログ設定を初期化（テスト用ログファイルを指定）
    setup_logging(script_dir, log_file='test_debug.log')

    # config.yaml のパスを指定
    config_path = os.path.join(script_dir, 'config.yaml')
    
    # 設定の読み込み
    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"設定ファイルの読み込みに失敗しました: {e}")
        return

    photo_directory = config.get('slideshow', {}).get('photos_directory', '')
    interval = config.get('slideshow', {}).get('interval', 5000)  # デフォルト値を設定

    if not photo_directory:
        print("設定ファイルに 'photos_directory' が指定されていません。")
        logging.error("設定ファイルに 'photos_directory' が指定されていません。")
        return
    
    # CameraHandler クラスのインスタンスを作成
    camera = photo_capture.CameraHandler(camera_index=0, countdown_time=5, preview_time=5, photo_directory=photo_directory)
    timestamp = get_timestamp()
    # タイムスタンプ付きのファイル名を作成
    filename = f"{timestamp}.jpg"
    file_path = os.path.join(photo_directory, filename)
    # 画像をキャプチャして保存
    camera.capture_image_with_resized_window(file_path)

    # 画面サイズを取得
    get_screen_sizes()

    # PhotoFrame の初期化と起動
    app = PhotoFrame(photo_directory, interval)
    app.mainloop()

if __name__ == "__main__":

    main()
