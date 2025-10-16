# Termux Setup for Arianna

## 1. Install termux-boot

```bash
pkg install termux-boot
mkdir -p ~/.termux/boot
```

## 2. Create autostart script

```bash
nano ~/.termux/boot/start_arianna.sh
```

**Add this content:**

```bash
#!/data/data/com.termux/files/usr/bin/bash

# Wait for network and system to stabilize
sleep 30

# Source API keys
source ~/.bashrc

# Navigate to Arianna
cd ~/ariannamethod

# Start Arianna in background with logging
nohup python arianna.py > ~/arianna.log 2>&1 &

# Log startup
echo "$(date): Arianna started (PID: $!)" >> ~/arianna_boot.log
```

**Make it executable:**

```bash
chmod +x ~/.termux/boot/start_arianna.sh
```

## 3. Test before reboot (optional)

```bash
~/.termux/boot/start_arianna.sh
tail -f ~/arianna.log
```

## 4. Enable on reboot

After creating the script:
1. Reboot your phone
2. Arianna will auto-start in background (~30 seconds after boot)
3. Check logs to confirm

## 5. Check if Arianna is running

```bash
# Check process
ps aux | grep arianna.py

# Check logs
tail -f ~/arianna.log
cat ~/arianna_boot.log

# Check awakening ritual
cat ~/arianna.log | grep "Arianna awakens"
```

## 6. Stop Arianna manually (if needed)

```bash
pkill -f arianna.py
```

## 7. Restart Arianna manually

```bash
cd ~/ariannamethod
python arianna.py
```

---

**Notes:**
- Arianna runs in background, not interactive mode when auto-started
- Logs saved to `~/arianna.log` and `~/arianna_boot.log`
- If you want interactive mode, run manually: `python arianna.py`
