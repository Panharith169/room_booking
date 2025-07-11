# 📱 Local Network Access Guide for RUPP Room Booking System

## 🎯 Quick Setup for Phone Access

### Step 1: Start the Local Network Server

**Option A: Use the automated script (Recommended)**
```bash
# Double-click this file in Windows Explorer
start_local_network.bat
```

**Option B: Python script**
```bash
python start_local_network.py
```

**Option C: Manual command**
```bash
python manage.py runserver 0.0.0.0:8000
```

### Step 2: Find Your IP Address

**Windows (Command Prompt):**
```cmd
ipconfig | findstr IPv4
```

**The script will automatically show your IP address like:**
- `192.168.1.100` (most common)
- `192.168.0.100` 
- `10.0.0.100`

### Step 3: Connect from Phone

1. **Make sure your phone and computer are on the same WiFi network**
2. **Open browser on your phone**
3. **Type the URL:** `http://YOUR_IP_ADDRESS:8000`

**Example URLs:**
- `http://192.168.1.100:8000`
- `http://192.168.0.100:8000`
- `http://10.0.0.100:8000`

## 🔧 Troubleshooting

### Problem: Can't access from phone

**Solution 1: Check Windows Firewall**
```cmd
# Run as Administrator
netsh advfirewall firewall add rule name="Django Dev Server" dir=in action=allow protocol=TCP localport=8000
```

**Solution 2: Disable Windows Firewall temporarily**
1. Go to Windows Security
2. Firewall & network protection
3. Turn off Windows Defender Firewall (temporarily)

**Solution 3: Check WiFi network**
- Make sure both devices are on the same WiFi
- Some public WiFi networks block device-to-device communication

### Problem: Server not starting

**Check if port is in use:**
```cmd
netstat -ano | findstr :8000
```

**Kill process using port 8000:**
```cmd
taskkill /PID [PID_NUMBER] /F
```

## 📱 Mobile Browser Compatibility

### Recommended Mobile Browsers:
- ✅ Chrome (Android/iOS)
- ✅ Safari (iOS)
- ✅ Firefox (Android/iOS)
- ✅ Samsung Internet (Android)

### Mobile-Friendly Features:
- Responsive design works on all screen sizes
- Touch-friendly buttons and forms
- Mobile-optimized navigation

## 🌐 Access URLs

Once server is running, you can access from:

**Computer (Local):**
- `http://localhost:8000`
- `http://127.0.0.1:8000`

**Phone/Other Devices (Network):**
- `http://[YOUR_IP]:8000`

**Admin Panel:**
- `http://[YOUR_IP]:8000/admin/`

**User Dashboard:**
- `http://[YOUR_IP]:8000/accounts/dashboard/`

## 🔒 Security Notes

### For Local Development:
- ✅ Safe to use `ALLOWED_HOSTS = ['*']`
- ✅ Safe to use `0.0.0.0:8000` binding
- ✅ Keep `DEBUG = True`

### Important:
- 🚫 **NEVER** use these settings in production
- 🚫 **NEVER** expose to the internet
- ✅ **ONLY** for local network testing

## 📊 Testing Checklist

- [ ] Computer can access `http://localhost:8000`
- [ ] Phone can access `http://[YOUR_IP]:8000`
- [ ] Both devices are on same WiFi
- [ ] Windows Firewall allows Django server
- [ ] Admin panel works from phone
- [ ] User registration works from phone
- [ ] Room booking works from phone

## 🚀 Quick Commands

**Start server for network access:**
```bash
python manage.py runserver 0.0.0.0:8000
```

**Check Django is working:**
```bash
python manage.py check
```

**Create admin user:**
```bash
python manage.py createsuperuser
```

**Run migrations:**
```bash
python manage.py migrate
```

## 💡 Pro Tips

1. **Bookmark the IP on your phone** for easy access
2. **Use QR code generator** to share the URL
3. **Test with multiple phones** to ensure it works
4. **Check responsive design** on different screen sizes
5. **Test all features** from mobile browsers

## 🔧 Alternative Methods

### Method 1: Using ngrok (Internet tunnel)
```bash
# Install ngrok
ngrok http 8000
# Use the generated URL
```

### Method 2: Using VS Code Live Share
1. Install Live Share extension
2. Share your session
3. Collaborators can access via browser

### Method 3: Using Windows hotspot
1. Create mobile hotspot on Windows
2. Connect phone to hotspot
3. Access via computer's hotspot IP
