from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML


@dataclass(kw_only=True)
class Device:
    name: str | None = None
    ip: str | None = None
    mac: str | None = None


@dataclass(kw_only=True)
class WizautConfig:
    host: str = '127.0.0.1'
    port: int = 8001
    broadcast: str = '255.255.255.255'
    timeout: int = 10
    devices: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> 'WizautConfig':
        config_dict = YAML().load(path.read_text())
        return cls(**config_dict)

    @classmethod
    def discover(cls) -> 'WizautConfig':
        for path in (
            Path.home() / '.config' / 'wizaut.yaml',
            Path('/etc') / 'wizaut.yaml',
        ):
            if path.exists():
                return cls.load(path)
        return cls()

    def get_devices(self) -> list[Device]:
        return [Device(**device) for device in self.devices]
