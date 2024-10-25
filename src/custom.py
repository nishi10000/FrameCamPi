# src/custom.py

import tkinter as tk
from tkinter import ttk
import logging

class CustomFrame(tk.Frame):
    def __init__(self, parent, camera_handler, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.camera_handler = camera_handler

        # シンプルなラベルを追加
        label = ttk.Label(self, text="これはカスタムモードです。", font=("Arial", 16))
        label.pack(padx=20, pady=20)

        # 追加のウィジェットや機能をここに実装
        # 例: ボタン
        close_button = ttk.Button(self, text="このウィンドウを閉じる", command=self.close_window)
        close_button.pack(pady=10)

    def close_window(self):
        self.parent.destroy()
        logging.info("カスタムモードのウィンドウを閉じました。")

    def destroy(self):
        # 必要なリソースのクリーンアップがあればここに追加
        super().destroy()
