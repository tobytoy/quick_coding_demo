#!/bin/bash

# 更新套件列表
sudo apt update

# 安裝必要工具
sudo apt install -y wget gnupg2

# 下載 Google Chrome 安裝檔
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# 安裝
sudo apt install -y ./google-chrome-stable_current_amd64.deb
