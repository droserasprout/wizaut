# Wizaut

Lightweight Web UI to manage WiZ lights. Made with Python, htmx, and some CSS.

![Wizaut interface screenshot](screenshot.png)

## Usage

Run `wizaut` command and open `http://localhost:8001` in your browser. You can also create a config file at `/etc/wizaut.yaml` or `~/.config/wizaut.yaml` with the following content:

```yaml
host: 0.0.0.0
port: 8001
broadcast: 255.255.255.255
timeout: 10
devices:
  - name: Couch
    mac: d8:a0:11:bc:75:c7
  - name: Table
    mac: d8:a0:11:b8:7d:79
    ip: 192.168.0.141
  - name: Floor Lamp
    mac: d8:a0:11:b7:6c:7d
    ip: 192.168.0.107
  - name: Bedroom
    mac: d8:a0:11:be:54:ab 
    ip: 192.168.0.162
```
