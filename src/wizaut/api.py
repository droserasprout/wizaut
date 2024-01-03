import asyncio
from pathlib import Path

import pywizlight as wl  # type: ignore[import-untyped]
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from ruamel.yaml import YAML

config_path = Path(__file__).parent.parent.parent / 'wizaut.yaml'
config = YAML().load(config_path.read_text())


KNOWN_BULBS = {k.replace(':', ''): v for k, v in config['devices'].items()}

_discovered_lights: list[wl.wizlight] = []


async def _get_lights() -> list[wl.wizlight]:
    global _discovered_lights
    if not _discovered_lights:
        _discovered_lights = await wl.discovery.discover_lights(
            broadcast_space=config['broadcast'],
            wait_time=int(config['timeout']),
        )
    for _light in _discovered_lights:
        await _light.updateState()
    return _discovered_lights


templates = Jinja2Templates(directory=Path(__file__).parent.joinpath('templates'))
app = FastAPI()
app.mount('/static', StaticFiles(directory=Path(__file__).parent.joinpath('static')), name='static')


@app.get('/', response_class=HTMLResponse)
async def index(request: Request) -> Response:
    data = {'page': 'Home page'}
    return templates.TemplateResponse('index.j2', {'request': request, 'data': data})


class System(BaseModel):
    system_name: str


@app.get('/lights', response_class=HTMLResponse)
async def get_lights(request: Request) -> Response:
    res = []

    lights = await _get_lights()
    for light in lights:
        await light.updateState()
        name = KNOWN_BULBS.get(light.mac) or light.mac
        state = light.state.get_state()
        res.append(
            {
                'name': name,
                'ip': light.ip,
                'mac': light.mac,
                'status': state,
                'brightness': light.state.get_brightness() if state else 0,
                'colortemp': light.state.get_colortemp(),
            }
        )

    return templates.TemplateResponse('lights.j2', {'request': request, 'lights': res})


@app.get('/lights/reset', response_class=HTMLResponse)
async def reset_lights(request: Request) -> Response:
    global _discovered_lights
    _discovered_lights = []
    return Response()


@app.get('/lights/off', response_class=HTMLResponse)
async def lights_off(request: Request) -> Response:
    for light in await _get_lights():
        await light.turn_off()
    return await get_lights(request)


@app.get('/lights/on', response_class=HTMLResponse)
async def lights_on(request: Request) -> Response:
    for light in await _get_lights():
        await light.turn_on()
    return await get_lights(request)


@app.get('/lights/{name}/flip', response_class=HTMLResponse)
async def light_flip(request: Request) -> Response:
    import pywizlight as wl

    name = request.path_params['name']

    light = wl.wizlight(name)
    await light.lightSwitch()
    await light.updateState()
    return Response('ON') if light.state.get_state() else Response('OFF')


@app.post('/lights/{name}/brightness', response_class=HTMLResponse)
async def light_brightness(request: Request) -> None:
    name = request.path_params['name']
    value = int((await request.form())['value'])  # type: ignore[arg-type]

    light = wl.wizlight(name)
    await light.updateState()
    timeout = config['timeout']

    if value:
        await asyncio.wait_for(light.turn_on(wl.PilotBuilder(brightness=int(value))), timeout)
    else:
        await asyncio.wait_for(light.turn_off(), timeout)


@app.post('/lights/{name}/warmth', response_class=HTMLResponse)
async def light_warmth(request: Request) -> None:
    name = request.path_params['name']
    value = (await request.form())['value']

    light = wl.wizlight(name)
    await light.updateState()
    timeout = config['timeout']
    await asyncio.wait_for(light.turn_on(wl.PilotBuilder(colortemp=int(value))), timeout)  # type: ignore[arg-type]
