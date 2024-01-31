import pywizlight as wl  # type: ignore[import-untyped]


class WizManager:
    def __init__(
        self,
        broadcast: str = '255.255.255.255',
        timeout: int = 10,
        aliases: dict[str, str] | None = None,
    ):
        self._broadcast: str = broadcast
        self._timeout: int = timeout
        self._aliases: dict[str, str] = aliases or {}
        self._lights: list[wl.wizlight] = []

    def __getitem__(self, name: str) -> wl.wizlight:
        name = (self._aliases.get(name) or name).replace(':', '').lower()
        for light in self._lights:
            if name in (light.mac, light.ip):
                return light
        raise KeyError(f'No light with name {name}')

    async def discover(self) -> None:
        self._lights = await wl.discovery.discover_lights(
            broadcast_space=self._broadcast,
            wait_time=self._timeout,
        )

    async def refresh(self) -> None:
        for _light in self._lights:
            await _light.updateState()

    async def get_lights(self) -> list[wl.wizlight]:
        if not self._lights:
            await self.discover()
        await self.refresh()
        return self._lights
