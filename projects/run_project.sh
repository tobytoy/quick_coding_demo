#!/bin/bash

# 1. 尋找所有專案資料夾（排除 demo）
echo "📁 可用的專案資料夾："
PROJECTS=()
i=1
for dir in */ ; do
    if [[ "$dir" != "demo/" ]]; then
        PROJECTS+=("${dir%/}")
        echo "$i) ${dir%/}"
        ((i++))
    fi
done

# 2. 使用者選擇專案
read -p "請輸入要執行的專案編號: " choice
PROJECT_NAME="${PROJECTS[$((choice-1))]}"

if [ -z "$PROJECT_NAME" ]; then
    echo "❌ 無效的選擇"
    exit 1
fi

echo "✅ 選擇的專案是：$PROJECT_NAME"

# 3. 建立 demo 環境
echo "🔧 建立 demo 環境..."
bash setup_demo_env.sh

# 4. 進入專案資料夾
cd "$PROJECT_NAME" || exit

# 5. 安裝 requirements.txt
echo "📦 安裝必要套件..."
../demo/bin/pip install -r requirements.txt

# 6. 執行 Streamlit 應用
echo "🚀 啟動 Streamlit..."
../demo/bin/streamlit run app.py
