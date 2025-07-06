#!/bin/bash

ENV_NAME="demo"

# 找出所有可能的 python 執行檔（包含 python、python3、python3.x）
PYTHON_CANDIDATES=$(compgen -c python | grep -E '^python([0-9\\.]+)?$' | sort -u)

HIGHEST_PYTHON=""
HIGHEST_VERSION="0"

# 比較版本號
version_gt() {
    [ "$(printf '%s\n' "$@" | sort -V | tail -n 1)" == "$1" ]
}

# 找出最高版本的 Python
for cmd in $PYTHON_CANDIDATES; do
    if command -v "$cmd" &> /dev/null; then
        VERSION=$("$cmd" -V 2>&1 | awk '{print $2}')
        if version_gt "$VERSION" "$HIGHEST_VERSION"; then
            HIGHEST_VERSION="$VERSION"
            HIGHEST_PYTHON="$cmd"
        fi
    fi
done
if [ -z "$HIGHEST_PYTHON" ]; then
    echo "❌ 找不到可用的 Python 版本。"
    exit 1
fi

echo "✅ 使用最高版本的 Python：$HIGHEST_PYTHON ($HIGHEST_VERSION)"

# 刪除舊環境
if [ -d "$ENV_NAME" ]; then
    echo "🔄 已存在 $ENV_NAME 環境，正在清除..."
    rm -rf "$ENV_NAME"
fi
# 建立新環境
echo "🚀 建立新的虛擬環境：$ENV_NAME"
"$HIGHEST_PYTHON" -m venv "$ENV_NAME"

# 啟用虛擬環境並更新 pip
echo "📦 啟用環境並升級 pip..."
source "$ENV_NAME/bin/activate"
python -m pip install --upgrade pip

echo "✅ 環境建立完成！請使用以下指令啟動："
echo "source $ENV_NAME/bin/activate"
