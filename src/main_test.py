# test_main.py

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
from utils import get_screen_sizes

class ModeSwitcherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("モードスイッチャー")
        self.geometry("400x200")
        self.resizable(False, False)

        # ラベルの作成
        label = ttk.Label(self, text="実行したいモードを選択してください。", font=("Arial", 14))
        label.pack(pady=20)

        # フレームの作成
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        # Photo Frame モードのボタン
        self.photo_frame_button = ttk.Button(button_frame, text="Photo Frame モード", command=self.launch_photo_frame)
        self.photo_frame_button.grid(row=0, column=0, padx=10, pady=10)

        # Smile Detection モードのボタン
        self.smile_detection_button = ttk.Button(button_frame, text="Smile Detection モード", command=self.launch_smile_detection)
        self.smile_detection_button.grid(row=0, column=1, padx=10, pady=10)

        # 終了ボタン
        self.exit_button = ttk.Button(self, text="終了", command=self.quit)
        self.exit_button.pack(pady=10)

        # スクリプトのパスを取得
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.photoframe_script = os.path.join(self.script_dir, 'photoframe_tkinter.py')
        self.smile_detection_script = os.path.join(self.script_dir, 'smile_detection.py')

        # スクリプトの存在確認
        if not os.path.isfile(self.photoframe_script):
            messagebox.showerror("エラー", f"'{self.photoframe_script}' が見つかりません。")
            self.photo_frame_button.config(state=tk.DISABLED)
        if not os.path.isfile(self.smile_detection_script):
            messagebox.showerror("エラー", f"'{self.smile_detection_script}' が見つかりません。")
            self.smile_detection_button.config(state=tk.DISABLED)

        # プロセス管理用リスト
        self.processes = []

        # ウィンドウ閉じる時の処理
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def launch_photo_frame(self):
        """Photo Frame モードを起動します。"""
        try:
            # Pythonインタープリタを指定してスクリプトを実行
            process = subprocess.Popen([sys.executable, self.photoframe_script],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            self.processes.append(process)
            messagebox.showinfo("実行中", "Photo Frame モードを起動しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"Photo Frame モードの起動に失敗しました。\n{e}")

    def launch_smile_detection(self):
        """Smile Detection モードを起動します。"""
        try:
            # Pythonインタープリタを指定してスクリプトを実行
            process = subprocess.Popen([sys.executable, self.smile_detection_script],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            self.processes.append(process)
            messagebox.showinfo("実行中", "Smile Detection モードを起動しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"Smile Detection モードの起動に失敗しました。\n{e}")

    def on_closing(self):
        """アプリケーション終了時の処理。起動したプロセスを終了します。"""
        if self.processes:
            if messagebox.askokcancel("終了確認", "起動中のモードがあります。終了しますか？"):
                for process in self.processes:
                    process.terminate()
                self.destroy()
        else:
            self.destroy()

if __name__ == "__main__":
    get_screen_sizes()
    app = ModeSwitcherApp()
    app.mainloop()
