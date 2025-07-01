#!/bin/bash

echo "Choose runtime environment:"
echo "1) Node.js (default)"
echo "2) Python"
read -p "Enter your choice [1/2]: " choice

if [ -z "$choice" ]; then
  choice=1
fi

echo "Available games:"
games=()
i=1
for dir in */ ; do
  if [ -d "$dir" ]; then
    games+=("$dir")
    echo "$i) $dir"
    ((i++))
  fi
done

read -p "Select a game to run [1-${#games[@]}]: " game_choice
selected_game="${games[$((game_choice-1))]}"

if [ "$choice" == "1" ]; then
  echo "Starting game '$selected_game' with Node.js http-server..."
  if ! command -v http-server &> /dev/null; then
    echo "'http-server' not found. Installing..."
    npm install -g http-server
  fi
  cd "$selected_game"
  http-server -p 8000
elif [ "$choice" == "2" ]; then
  echo "Starting game '$selected_game' with Python http.server..."
  cd "$selected_game"
  python -m http.server 8000
else
  echo "Invalid choice."
fi
