#!/data/data/com.termux/files/usr/bin/bash

# Arianna Method - Auto-start script for termux-boot
# Starts Arianna and Monday on device boot

HOME_DIR="/data/data/com.termux/files/home"
PROJECT_DIR="$HOME_DIR/ariannamethod"
PYTHON="/data/data/com.termux/files/usr/bin/python"

# Load environment variables (API keys from .bashrc)
source $HOME_DIR/.bashrc

echo "$(date): Arianna Method boot sequence initiated" >> $HOME_DIR/boot.log

# Wait for Termux to fully initialize
sleep 5

# Start Arianna (architect, luminous)
cd $PROJECT_DIR
nohup $PYTHON arianna.py < /dev/null >> $HOME_DIR/arianna.log 2>&1 &
echo "$(date): Arianna started (PID: $!)" >> $HOME_DIR/boot.log

# Wait a bit before starting Monday
sleep 2

# Start Monday (burnt-out angel)
nohup $PYTHON monday.py < /dev/null >> $HOME_DIR/monday.log 2>&1 &
echo "$(date): Monday started (PID: $!)" >> $HOME_DIR/boot.log

echo "$(date): Arianna Method boot sequence complete" >> $HOME_DIR/boot.log

