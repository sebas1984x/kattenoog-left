
---

## README voor **linker Pi** (`kattenoog-left`)

```markdown
# Kattenoog – Linker Pi

Deze Raspberry Pi bestuurt:
- Het **linker oog** (UDP 5005 → `eye-left.service`)
- Een **jaw.service** is aanwezig, maar wordt standaard niet gebruikt/gestart.

## Scripts
Alle code staat in `/home/cat/kattenoog/` en in deze repo.

- `kattenoog_plc_udp_oneeye.py` → visualisatie van het linkeroog
- `jaw_udp_dynamixel.py` → aanwezig maar op linker Pi meestal niet actief
- Extra helper-scripts (`eyes_send.py`, `jaw_send.py`)

## Systemd services
Geïnstalleerd in `/etc/systemd/system/` en ook in `services/` map van deze repo.

- `eye-left.service` → de daadwerkelijke service voor het linkeroog
- `eye.service` → symlink naar `eye-left.service`
- `jaw.service` → aanwezig, maar doorgaans niet actief

Status bekijken:
```bash
systemctl status eye-left.service
