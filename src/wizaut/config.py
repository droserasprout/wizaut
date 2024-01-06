from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from ruamel.yaml import YAML


@dataclass(kw_only=True)
class WizautConfig:
    host: str = '127.0.0.1'
    port: int = 8001
    broadcast: str = '255.255.255.255'
    timeout: int = 10
    devices: dict[str, str] = field(default_factory=dict)

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
