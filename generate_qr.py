import qrcode
import socket
import sys
from io import BytesIO
import base64

def get_local_ip():
    """Get the local IP address"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "127.0.0.1"

def generate_qr_code(url):
    """Generate QR code for the URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code
    img.save("room_booking_qr.png")
    print(f"📱 QR Code saved as 'room_booking_qr.png'")
    print(f"   Scan with your phone camera to access: {url}")

def main():
    local_ip = get_local_ip()
    port = 8000
    url = f"http://{local_ip}:{port}"
    
    print("🎯 Room Booking System - Phone Access Helper")
    print("=" * 50)
    print(f"🌐 Local IP: {local_ip}")
    print(f"🔗 URL: {url}")
    print()
    
    try:
        generate_qr_code(url)
        print("\n📋 Instructions for phone access:")
        print("1. Make sure your phone is on the same WiFi")
        print("2. Scan the QR code OR")
        print(f"3. Open browser and go to: {url}")
        print("\n🚀 Now run: python manage.py runserver 0.0.0.0:8000")
    except ImportError:
        print("📦 To generate QR codes, install qrcode:")
        print("   pip install qrcode[pil]")
        print(f"\n📱 Manual access: {url}")

if __name__ == "__main__":
    main()
