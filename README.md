# FrameCamPi Project Overview

# デジタルフォトフレーム with Raspberry Pi

このプロジェクトは、Raspberry Pi を使用してデジタルフォトフレームを作成する方法を説明します。カメラ、マイク、ディスプレイを接続し、スライドショー表示、写真撮影、音声コマンド操作などの機能を実装します。

## 1. ハードウェアの準備

### Raspberry Pi 4 の準備

Raspberry Pi 4 を使用します。

### 周辺機器の接続

* **カメラモジュール:** Raspberry Pi Camera Module V2 を CSI ポートに接続します。
* **ディスプレイ:** HDMI ケーブルでディスプレイを接続します。
* **マイク:** USB マイクを Raspberry Pi の USB ポートに接続します。
* **電源供給:** 安定した電源（例：5V 3A の USB-C アダプタ）を接続します。


## 2. ソフトウェアのセットアップ

### 2.1 推奨OSのインストール

* **OS:** Raspberry Pi OS (Bullseye)

最新の Raspberry Pi OS (現時点では Bullseye 版) を使用してください。公式サイトから Raspberry Pi Imager をダウンロードし、SD カードにインストールします。インストール後、SD カードを Raspberry Pi に挿入し、電源を接続して起動します。

### 2.2 初期設定

Raspberry Pi を起動し、画面の指示に従って言語、タイムゾーン、パスワード変更などの初期設定を行います。

ターミナルを開き、`raspi-config` を実行して以下を有効化します：

```bash
sudo raspi-config
```

* インターフェースオプションでカメラを有効化します。
* 必要に応じて SSH を有効化します (リモート操作を行う場合)。

### 2.3 システムの更新

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2.4 必要なパッケージのインストール

**requirements.txt ファイルがある場合:**

```bash
pip3 install -r requirements.txt
```

**requirements.txt ファイルがない場合、もしくは追加で必要なパッケージがある場合:**

```bash
sudo apt-get install -y python3-pip python3-picamera python3-opencv python3-flask samba samba-common-bin
```

そして、`requirements.txt` に記載されているパッケージをインストールします。例:

```bash
pip3 install pygame SpeechRecognition Flask-HTTPAuth Pillow python-dotenv PyYAML
```


### 2.5 プロジェクトディレクトリの作成

```bash
mkdir -p ~/photo_frame/src ~/photo_frame/photos ~/photo_frame/templates ~/photo_frame/docs
cd ~/photo_frame
```

### 2.6 設定ファイルの作成

#### .env ファイル (~/photo_frame/.env)

```bash
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

SLIDESHOW_INTERVAL=5000  # ミリ秒
SLIDESHOW_TIMEOUT=60      # 秒
PHOTOS_DIRECTORY="/home/pi/photo_frame/photos"

CAMERA_RESOLUTION="1920x1080"

SAMBA_USER="pi"
SAMBA_PASSWORD="your_strong_password"  # 強力なパスワードに変更してください

ENVIRONMENT="production"
```

#### config.yaml ファイル (~/photo_frame/src/config.yaml)

```yaml
slideshow:
  interval: ${SLIDESHOW_INTERVAL}
  timeout: ${SLIDESHOW_TIMEOUT}
  photos_directory: ${PHOTOS_DIRECTORY}

camera:
  resolution: ${CAMERA_RESOLUTION}

samba:
  user: ${SAMBA_USER}
  password: ${SAMBA_PASSWORD}

flask:
  host: ${FLASK_HOST}
  port: ${FLASK_PORT}
  debug: ${FLASK_DEBUG}

environment: ${ENVIRONMENT}
```

**重要:** `SAMBA_PASSWORD` は必ず強力なパスワードに変更してください。

このREADMEは提供された情報に基づいて作成されています。 今後の開発に応じて、適宜更新していく必要があります。 特に、アプリケーションの起動方法、Sambaの設定方法、音声コマンドの使い方など、詳細な手順を追記するとより分かりやすくなります。  また、`requirements.txt` の内容を具体的に示すと、ユーザーにとってより親切なドキュメントになります。
