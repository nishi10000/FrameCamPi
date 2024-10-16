import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
from PIL import Image

# srcディレクトリをPythonのパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

import photoframe_tkinter as pf  # テスト対象のモジュールをインポート

# テスト用の画像を作成
def create_test_image(path, width=100, height=100):
    img = Image.new('RGB', (width, height), color='red')
    img.save(path)

class TestPhotoFrame(unittest.TestCase):

    def setUp(self):
        # Tkinterのmainloopをモック化して無限ループを防ぐ
        self.patcher_mainloop = patch('tkinter.Tk.mainloop', return_value=None)
        self.mock_mainloop = self.patcher_mainloop.start()

        # テスト用の画像ディレクトリを作成
        self.test_dir = 'test_photos'
        os.makedirs(self.test_dir, exist_ok=True)
        create_test_image(os.path.join(self.test_dir, 'test1.jpg'))
        create_test_image(os.path.join(self.test_dir, 'test2.png'))

        # utils モジュールをモックに置き換える
        self.mock_utils = MagicMock()
        self.mock_utils.get_screen_sizes.return_value = (1920, 1080)
        self.mock_utils.load_config.return_value = {'slideshow': {'photos_directory': self.test_dir, 'interval': 100}}
        pf.utils = self.mock_utils

    def tearDown(self):
        # テスト用の画像ディレクトリを削除
        for f in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, f))
        os.rmdir(self.test_dir)

        # モックを解除
        self.patcher_mainloop.stop()
        delattr(pf, 'utils')

    def test_load_photos(self):
        app = pf.PhotoFrame()
        self.assertEqual(len(app.photos), 2)  # 2つのテスト画像が読み込まれることを確認

    def test_load_photos_no_directory(self):
        self.mock_utils.load_config.return_value = {'slideshow': {'photos_directory': 'nonexistent_dir', 'interval': 100}}
        with self.assertRaises(FileNotFoundError):  # ディレクトリが存在しない場合、FileNotFoundErrorが発生することを確認
            pf.PhotoFrame()

    def test_show_photo(self):
        app = pf.PhotoFrame()

        # show_photo が画像を読み込み、リサイズ、表示できることを確認
        with patch.object(app.canvas, 'create_image') as mock_create_image, \
             patch.object(app.canvas, "delete") as mock_delete:
            app.show_photo()
            mock_create_image.assert_called()  # 画像が描画されたことを確認
            mock_delete.assert_called_with("all")  # 既存画像が削除されたことを確認

    def test_no_photos(self):
        # 画像のないディレクトリを指定した場合のテスト
        empty_dir = 'empty_dir'
        os.makedirs(empty_dir, exist_ok=True)
        self.mock_utils.load_config.return_value = {'slideshow': {'photos_directory': empty_dir, 'interval': 100}}

        with self.assertRaises(ValueError):  # 写真がない場合、ValueErrorが発生することを確認
            pf.PhotoFrame()
        os.rmdir(empty_dir)

    def test_invalid_image(self):
        # 無効な画像ファイルがある場合のテスト
        with open(os.path.join(self.test_dir, 'invalid.jpg'), 'w') as f:
            f.write("This is not an image")

        app = pf.PhotoFrame()

        with patch.object(app.canvas, 'create_image') as mock_create_image:  # Canvasへの描画をモック化
            app.show_photo()
            # show_photo()がエラーで停止せず、次の画像の表示に進むことを確認
            self.assertEqual(app.current, 1 % len(app.photos))

if __name__ == '__main__':
    unittest.main()