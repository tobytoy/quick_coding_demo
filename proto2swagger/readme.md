
# Method
* .proto → protoc-gen-openapiv2 → .swagger.json
* 再用 Swagger UI / Redoc 顯示

# Step2
## 1: 系統工具

```bash
sudo apt update
sudo apt install -y protobuf-compiler golang-go git curl
```

## 2 安裝 grpc-gateway 需要的插件（會放到 $GOPATH/bin，記得把它加到 PATH 裡）

```bash
sudo apt update
sudo apt install -y protobuf-compiler golang-go git curl

# check version
protoc-gen-openapiv2 --version

```



