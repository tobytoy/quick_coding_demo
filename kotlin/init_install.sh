#!/bin/bash
set -e

KOTLIN_VERSION="1.9.23"
ZIP_FILE="kotlin-compiler-$KOTLIN_VERSION.zip"
INSTALL_DIR="/opt/kotlinc"

# 🔍 檢查是否已安裝 Kotlin
if command -v kotlin &> /dev/null; then
    echo "✅ 已安裝 Kotlin（版本：$(kotlin -version 2>&1)）"
    exit 0
fi

echo "📦 尚未安裝 Kotlin，開始安裝..."

# 📥 安裝 Java（必要）
sudo apt update
sudo apt install -y default-jdk curl unzip

# 📦 下載 Kotlin 編譯器
curl -LO "https://github.com/JetBrains/kotlin/releases/download/v$KOTLIN_VERSION/$ZIP_FILE"

# 📂 解壓並移動到 /opt
unzip "$ZIP_FILE"
sudo mv kotlinc "$INSTALL_DIR"

# 🔗 建立指令捷徑
sudo ln -s "$INSTALL_DIR/bin/kotlinc" /usr/local/bin/kotlinc
sudo ln -s "$INSTALL_DIR/bin/kotlin" /usr/local/bin/kotlin

# 🧹 刪除 zip 檔
rm "$ZIP_FILE"

# ✅ 驗證安裝
echo "🎉 Kotlin 安裝完成！版本如下："
kotlin -version

