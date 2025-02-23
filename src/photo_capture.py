import cv2
import time
import threading
import os
import sys
import logging
from utils import get_screen_sizes, load_config, setup_logging, get_timestamp  # utils.pyからインポート

class CameraHandler:
    def __init__(self, camera_index=0, countdown_time=3, preview_time=3, photo_directory='photos'):
        """
        カメラハンドラーの初期化。
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
        try:
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_V4L2)
            if not self.cap.isOpened():
                logging.error("カメラを開くことができませんでした。")
                return False
            logging.info("カメラが正常に初期化されました。")
            return True
        except Exception as e:
            logging.error(f"カメラの初期化中にエラーが発生しました: {e}")
            return False

    def release_camera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            logging.info("カメラをリリースしました。")

    def start_countdown(self, start_time):
        """カウントダウンの残り時間を計算します。"""
        return int(start_time + self.countdown_time - time.time())

    def show_camera_preview(self, window_name, overlay_text=None):
        """カメラからのフレームを取得して表示します。"""
        ret, frame = self.cap.read()
        if not ret:
            logging.error("フレームを取得できませんでした。")
            return None
        if overlay_text is not None:
            cv2.putText(
                frame,
                overlay_text,
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (255, 0, 0),
                3,
                cv2.LINE_AA
            )
        cv2.imshow(window_name, frame)
        return frame

    def capture_image(self, save_path):
        """カメラから画像をキャプチャして保存します。"""
        ret, frame = self.cap.read()
        if ret:
            cv2.imwrite(save_path, frame)
            logging.info(f"画像が保存されました: {save_path}")
            return frame
        else:
            logging.error("画像のキャプチャに失敗しました。")
            return None

    def capture_image_with_resized_window(self, save_path):
        """
        カウントダウンを表示しながらカメラのプレビューを行い、カウントダウン終了後に写真を撮影し、
        撮影された画像をプレビュー表示します。
        """
        if not self.initialize_camera():
            return

        window_name = 'カメラプレビュー - カウントダウン'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.screen_width, self.screen_height)

        start_time = time.time()

        try:
            while True:
                remaining_time = self.start_countdown(start_time)
                if remaining_time > 0:
                    frame = self.show_camera_preview(window_name, str(remaining_time))
                else:
                    self.captured_frame = self.capture_image(save_path)
                    break

                if frame is None:
                    break

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logging.info("ユーザーによってキャプチャが中断されました。")
                    break
        finally:
            self.release_camera()
            cv2.destroyAllWindows()

        # 撮影された画像のプレビュー表示
        if self.captured_frame is not None:
            self.preview_image(self.captured_frame)

    def preview_image(self, frame):
        """
        撮影された画像をプレビュー表示します。
        """
        window_name = '撮影画像プレビュー'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.screen_width, self.screen_height)

        start_time = time.time()
        try:
            while time.time() - start_time < self.preview_time:
                cv2.imshow(window_name, frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logging.info("ユーザーによってプレビューが中断されました。")
                    break
            logging.info(f"プレビューが終了しました ({self.preview_time} 秒後)。")
        finally:
            cv2.destroyWindow(window_name)

    def start_camera_preview(self):
        """カメラからのリアルタイム映像をプレビュー表示します。"""
        if not self.initialize_camera():
            return

        window_name = 'カメラプレビュー'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.screen_width, self.screen_height)

        logging.info("カメラプレビューを開始します。'q' キーで終了します。")
        try:
            while True:
                frame = self.show_camera_preview(window_name)
                if frame is None:
                    break

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logging.info("ユーザーによってプレビューが終了されました。")
                    break
        finally:
            self.release_camera()
            cv2.destroyAllWindows()

def main():
    # スクリプトのディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ロギングの設定を初期化
    setup_logging(script_dir, log_file='debug.log')

    # config.yaml のパスを構築
    config_path = os.path.join(script_dir, 'config.yaml')

    if not os.path.exists(config_path):
        logging.error(f"設定ファイルが見つかりません: {config_path}")
        sys.exit(1)

    # 設定ファイルをロード
    try:
        config = load_config(config_filename=config_path, env_filename='.env')
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

if __name__ == "__main__":
    main()