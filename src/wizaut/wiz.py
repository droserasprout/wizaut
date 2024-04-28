import pywizlight as wl

from wizaut.config import Device  # type: ignore[import-untyped]


class WizManager:
    def __init__(
        self,
        devices: list[Device],
        broadcast: str = '255.255.255.255',
        timeout: int = 10,
    ):
        self._devices: list[Device] = devices
        self._broadcast: str = broadcast
        self._timeout: int = timeout
        self._lights: list[wl.wizlight] = []

    def add_device(self, device: Device) -> None:
        for known_device in self._devices:
            if device.mac == known_device.mac or device.ip == known_device.ip:
                return

        self._devices.append(device)

    def add_light(self, light: wl.wizlight) -> None:
        for device in self._devices:
            if light.mac == device.mac or light.ip == device.ip:
                break
        else:
            device = (Device(),)
            self._devices.append(device)

        device.name = device.name or light.mac
        device.ip = device.ip or light.ip
        device.mac = device.mac or light.mac

        for known_light in self._lights:
            if light.mac == known_light.mac:
                return

        self._lights.append(light)

    async def discover(self) -> None:
        discovered_lights = await wl.discovery.discover_lights(
            broadcast_space=self._broadcast,
            wait_time=self._timeout,
        )
        for light in discovered_lights:
            self.add_light(light)

    async def refresh(self) -> None:
        for device in self._devices:
            light = wl.wizlight(ip=device.ip, mac=device.mac)
            self.add_light(light)
        for _light in self._lights:
            if _light.ip in (None, 'None'):
                continue
            await _light.updateState()

    async def get_lights(self, update: bool = False) -> list[wl.wizlight]:
        if not self._devices:
            await self.discover()
        elif update:        
            await self.refresh()
        return self._lights
