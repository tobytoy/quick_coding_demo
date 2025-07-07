# 建立 Hello World 專案
PROJECT_DIR="$PWD/flutter_web_hello"
if [ -d "$PROJECT_DIR" ]; then
    echo "📁 專案已存在：$PROJECT_DIR"
else
    echo "🚀 建立 Flutter Web 專案..."
    flutter create flutter_web_hello
    cd flutter_web_hello
    flutter run -d chrome
fi

echo "🎉 完成！你可以用 VS Code 開啟 $PROJECT_DIR 來開發 Flutter Web App。"
