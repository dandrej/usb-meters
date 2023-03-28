#!/usr/bin/bash
pip install  -r usb/requirements.txt
install -D --target-directory=/usr/local/bin/fnirsi/ --mode=0644 $(find usb -maxdepth 1 -not -type d)
install --mode=0644 install/90-fnirsi.rules /etc/udev/rules.d/
install --mode=0644 install/fnirsi.service /etc/systemd/system/
install --mode=644 usb-config.yml /etc/
chmod +x /usr/local/bin/fnirsi/fnirsi_meter.py
udevadm trigger
systemctl daemon-reload
