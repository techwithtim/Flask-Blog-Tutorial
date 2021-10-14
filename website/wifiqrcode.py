import wifi_qrcode_generator
import re, os
from flask import url_for

def generate_code(SSID, Password):
    qrco = wifi_qrcode_generator.wifi_qrcode(
    SSID, False, 'WPA', Password
    )
    file = re.sub(r"[^A-Za-z]+", '', SSID) + ".png"
    fullfile = os.path.join('website', 'static', 'qrcode',file).lower()
    full = os.path.join('qrcode',file).lower()

    print(fullfile)

    qrco.save(fullfile, format='PNG')
    return full

def renameSSID(SSID):
    file = re.sub(r"[^A-Za-z]+", '', SSID) + ".png"
    path = url_for('static', filename = '/qrcode/'+file)
    return path
