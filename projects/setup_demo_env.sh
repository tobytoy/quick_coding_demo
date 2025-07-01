#!/bin/bash

ENV_NAME="demo"

# 找出所有 python3.x 可執行檔
PYTHON_BIN=$(compgen -c python3 | grep -E '^python3\\.[0-9]+$' | sort -V | tail -n 1)

# 檢查是否找到 Python 版本
if ! command -v "$PYTHON_BIN" &> /dev/null; then
    echo "❌ 找不到可用的 Python 3.x 版本，請先安裝 Python。"
    exit 1
fi

echo "✅ 使用最高版本的 Python：$PYTHON_BIN"

# 如果 demo 資料夾已存在，刪除它
if [ -d "$ENV_NAME" ]; then
    echo "🔄 已存在 $ENV_NAME 環境，正在清除..."
    rm -rf "$ENV_NAME"
fi

# 建立新的虛擬環境
echo "🚀 建立新的虛擬環境：$ENV_NAME"
"$PYTHON_BIN" -m venv "$ENV_NAME"

echo "✅ 環境建立完成！請使用以下指令啟動："
echo "source $ENV_NAME/bin/activate"



