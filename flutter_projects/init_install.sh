#!/bin/bash

set -e

# Flutter 安裝路徑
FLUTTER_DIR="$HOME/development/flutter"
FLUTTER_ZIP="flutter_linux_3.22.1-stable.tar.xz"
FLUTTER_URL="https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/$FLUTTER_ZIP"

echo "🔍 檢查是否已安裝 Flutter..."
if [ -d "$FLUTTER_DIR" ]; then
    echo "✅ Flutter 已安裝在 $FLUTTER_DIR"
else
    echo "📥 開始下載 Flutter SDK..."
    mkdir -p ~/development
    cd ~/development
    curl -O "$FLUTTER_URL"
    echo "📦 解壓縮 Flutter SDK..."
    tar xf "$FLUTTER_ZIP"
    rm "$FLUTTER_ZIP"
    echo "✅ Flutter 安裝完成！"
fi

# 設定 PATH
export PATH="$PATH:$FLUTTER_DIR/bin"

echo "🔧 執行 flutter doctor..."
flutter doctor

# 安裝 Web 所需的 Chrome
echo "🌐 安裝 Google Chrome..."
sudo apt update
sudo apt install -y wget gnupg2
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# 安裝 Linux 桌面開發所需套件（選擇性）
echo "🛠️ 安裝 Linux 桌面開發工具（選擇性）..."
sudo apt install -y ninja-build libgtk-3-dev

# 啟用 Web 支援
flutter config --enable-web

# 建立 Hello World 專案
PROJECT_DIR="$HOME/flutter_web_hello"
if [ -d "$PROJECT_DIR" ]; then
    echo "📁 專案已存在：$PROJECT_DIR"
else
    echo "🚀 建立 Flutter Web 專案..."
    flutter create flutter_web_hello
    cd flutter_web_hello
    flutter build web
fi

echo "🎉 完成！你可以用 VS Code 開啟 $PROJECT_DIR 並預覽 build/web 資料夾內容。"
