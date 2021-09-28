import wifi_qrcode_generator
import re, os

def generate_code(SSID, Password):
    qrco = wifi_qrcode_generator.wifi_qrcode(
    SSID, False, 'WPA', Password
    )
    file = re.sub(r"[^A-Za-z]+", '', SSID) + ".png"
    fullfile = os.path.join('website', 'static', 'qrcode',file).lower()
    full = os.path.join('static', 'qrcode',file).lower()

    print(fullfile)

    qrco.save(fullfile, format='PNG')
    return full