# Kattenoog – Linker Pi

Deze Raspberry Pi bestuurt het **linkeroog** van de kat.

## Functie
- Visualiseert het linkeroog op een display
- Ontvangt UDP-data (poort 5005) met 4 waarden: look_x, look_y, pupil, lid
- Reageert realtime op PLC-signalen (Siemens S7-1215)

## Scripts
Alle code staat in /home/cat/kattenoog/ en in deze repo:
- kattenoog_plc_udp_oneeye.py → aansturing linkeroog
- eyes_send.py → test/diagnose script
- jaw_udp_dynamixel.py en jaw_send.py zijn aanwezig, maar niet actief op deze Pi

## Systemd services
Geïnstalleerd in /etc/systemd/system/ en ook in de map services/ van deze repo:
- eye-left.service → hoofdservice voor linkeroog
- eye.service → symlink naar eye-left.service
- jaw.service → aanwezig, maar standaard niet actief

### Voorbeelden
Status bekijken:
  systemctl status eye-left.service

Service herstarten:
  sudo systemctl restart eye-left.service

Autostart checken:
  systemctl is-enabled eye-left.service

## Deployment
  cd /home/cat/kattenoog
  git pull
  sudo systemctl restart eye-left.service

## Troubleshooting
Logs volgen:
  journalctl -u eye-left.service -f

Controleren of UDP draait:
  sudo netstat -anu | grep 5005
