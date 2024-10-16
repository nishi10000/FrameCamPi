import cv2
import time
import threading
from utils import get_screen_sizes, load_config, setup_logging  # utils.pyからインポート
import datetime
import sys
import os
import logging

def get_timestamp():
    """現在の日時を取得して、ファイル名に使用できる形式にフォーマットします。"""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

class CameraHandler:
    def __init__(self, camera_index=0, countdown_time=3, preview_time=3, photo_directory='photos'):
        """
        カメラハンドラーの初期化。

        Parameters:
        - camera_index (int): 使用するカメラのインデックス (デフォルト: 0)
        - countdown_time (int): カウントダウンの秒数 (デフォルト: 3)
        - preview_time (int): 撮影後のプレビュー時間（秒） (デフォルト: 3)
        - photo_directory (str): 写真の保存先ディレクトリ (デフォルト: 'photos')
        """
        self.camera_index = camera_index
        self.countdown_time = countdown_time
        self.preview_time = preview_time
        self.photo_directory = photo_directory
        self.cap = None
        self.screen_width, self.screen_height = get_screen_sizes()
        self.captured_frame = None

    def initialize_camera(self):
        """カメラデバイスを初期化します。"""
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            logging.error("カメラを開くことができませんでした。")
            return False
        logging.info("カメラが正常に初期化されました。")
        return True

    def countdown_timer(self, countdown_event):
        """カウントダウンを非同期で行い、終了時にイベントを設定します。"""
        for i in range(self.countdown_time, 0, -1):
            logging.info(f"Countdown: {i}")
            countdown_event.remaining_time = i
            time.sleep(1)
        countdown_event.set()
        logging.info("カウントダウンが終了しました。")

    def capture_image_with_resized_window(self, save_path):
        """
        カウントダウンを表示しながらカメラのプレビューを行い、カウントダウン終了後に写真を撮影し、
        撮影された画像をプレビュー表示します。

        Parameters:
        - save_path (str): 撮影した画像の保存先
        """
        if not self.initialize_camera():
            return

        countdown_event = threading.Event()
        countdown_event.remaining_time = self.countdown_time
        countdown_thread = threading.Thread(target=self.countdown_timer, args=(countdown_event,))
        countdown_thread.start()

        # プレビューウィンドウの設定
        window_name = 'Camera Preview - Countdown'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.screen_width, self.screen_height)

        while True:
            ret, frame = self.cap.read()
            if not ret:
                logging.error("フレームを取得できませんでした。")
                break

            if not countdown_event.is_set():
                remaining_time = getattr(countdown_event, 'remaining_time', self.countdown_time)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(
                    frame,
                    str(remaining_time),
                    (50, 50),
                    font,
                    2,
                    (255, 0, 0),
                    3,
                    cv2.LINE_AA
                )
            else:
                self.captured_frame = frame
                cv2.imwrite(save_path, self.captured_frame)
                logging.info(f"画像が保存されました: {save_path}")
                break

            cv2.imshow(window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("ユーザーによってキャプチャが中断されました。")
                break

        self.cap.release()

        # 撮影された画像のプレビュー表示
        if self.captured_frame is not None:
            self.preview_image(self.captured_frame)

        cv2.destroyAllWindows()

    def preview_image(self, frame):
        """
        撮影された画像をプレビュー表示します。

        Parameters:
        - frame: 撮影された画像のフレーム
        """
        window_name = 'Captured Image'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.screen_width, self.screen_height)

        start_time = time.time()
        while time.time() - start_time < self.preview_time:
            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("ユーザーによってプレビューが中断されました。")
                break
        logging.info(f"プレビューが終了しました ({self.preview_time} 秒後)。")
        cv2.destroyWindow(window_name)

    def start_camera_preview(self):
        """カメラからのリアルタイム映像をプレビュー表示します。"""
        if not self.initialize_camera():
            return

        window_name = 'Camera Preview'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.screen_width, self.screen_height)

        logging.info("カメラプレビューを開始します。'q' キーで終了します。")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                logging.error("フレームを取得できませんでした。")
                break

            cv2.imshow(window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("ユーザーによってプレビューが終了されました。")
                break

        self.cap.release()
        cv2.destroyAllWindows()

def main():
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

    # 画像をキャプチャして保存
    camera_handler.capture_image_with_resized_window(file_path)

    # 例として、リアルタイムプレビューを実行する場合
    # camera_handler.start_camera_preview()

if __name__ == "__main__":
    main()
