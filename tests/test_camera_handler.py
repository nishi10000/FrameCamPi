# tests/test_camera_handler.py

import sys
import os
import unittest
import shutil
from unittest import mock
import cv2
import numpy as np  # NumPyをインポート
import threading  # threading.Event を使用

# srcディレクトリをPythonのパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from photo_capture import CameraHandler  # photo_capture.py からインポート
from utils import load_config, setup_logging

class TestCameraHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # テスト用のディレクトリを作成
        cls.test_photo_dir = os.path.join(parent_dir, 'test_photos')
        os.makedirs(cls.test_photo_dir, exist_ok=True)
        
        # ログ設定のモック
        setup_logging(cls.test_photo_dir, log_file='test_debug.log')

    @classmethod
    def tearDownClass(cls):
        # テスト後にディレクトリを削除
        shutil.rmtree(cls.test_photo_dir)

    @mock.patch('cv2.VideoCapture')
    def test_initialize_camera_success(self, mock_video_capture):
        # カメラが正常に初期化される場合のテスト
        mock_cap = mock.Mock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        camera = CameraHandler(photo_directory=self.test_photo_dir)
        result = camera.initialize_camera()
        self.assertTrue(result)
        mock_video_capture.assert_called_with(camera.camera_index, cv2.CAP_V4L2)

    @mock.patch('cv2.VideoCapture')
    def test_initialize_camera_failure(self, mock_video_capture):
        # カメラが初期化に失敗する場合のテスト
        mock_cap = mock.Mock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap

        camera = CameraHandler(photo_directory=self.test_photo_dir)
        result = camera.initialize_camera()
        self.assertFalse(result)

    @mock.patch('cv2.imwrite')
    @mock.patch('cv2.VideoCapture')
    @mock.patch.object(CameraHandler, 'countdown_timer')  # countdown_timer をモック
    def test_capture_image_with_resized_window(self, mock_countdown_timer, mock_video_capture, mock_imwrite):
        # カウントダウンイベントを即時にセット
        def immediate_set(*args, **kwargs):
            if len(args) > 0 and isinstance(args[0], threading.Event):
                args[0].set()
        
        mock_countdown_timer.side_effect = immediate_set

        # 画像キャプチャと保存のテスト
        mock_cap = mock.Mock()
        mock_cap.isOpened.return_value = True
        # フレーム読み込みを模擬（黒い画像を使用）
        mock_frame = np.zeros((768, 1024, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, mock_frame)
        mock_video_capture.return_value = mock_cap

        camera = CameraHandler(photo_directory=self.test_photo_dir, countdown_time=1, preview_time=1)
        save_path = os.path.join(self.test_photo_dir, 'test_image.jpg')

        # キャプチャ関数を実行（実際のGUI表示はスキップ）
        with mock.patch('cv2.imshow'), mock.patch('cv2.waitKey', return_value=ord('q')):
            camera.capture_image_with_resized_window(save_path)

        # 画像が保存されたか確認
        mock_imwrite.assert_called_with(save_path, mock_frame)
        self.assertTrue(os.path.exists(save_path))

    def test_directory_creation(self):
        # 写真保存ディレクトリの作成確認
        camera = CameraHandler(photo_directory=self.test_photo_dir)
        camera.initialize_camera()
        self.assertTrue(os.path.exists(self.test_photo_dir))

if __name__ == '__main__':
    unittest.main()
