import asyncio
from pathlib import Path

import pywizlight as wl  # type: ignore[import-untyped]
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from wizaut.config import WizautConfig
from wizaut.wiz import WizManager


def create_app(config: WizautConfig) -> FastAPI:
    templates = Jinja2Templates(directory=Path(__file__).parent / 'templates')
    static = StaticFiles(directory=Path(__file__).parent / 'static')

    app = FastAPI()
    app.mount('/static', static, name='static')
    wiz = WizManager(
        devices=config.get_devices(),
        broadcast=config.broadcast,
        timeout=config.timeout,
    )

    @app.get('/', response_class=HTMLResponse)
    async def index(request: Request) -> Response:
        data = {'page': 'Home page'}
        return templates.TemplateResponse('index.j2', {'request': request, 'data': data})

    @app.get('/lights', response_class=HTMLResponse)
    async def get_lights(request: Request) -> Response:
        res = []

        lights = await wiz.get_lights(update=True)
        for light in lights:
            if light.ip in (None, 'None'):
                continue
            print('updating', light)
            await light.updateState()
            for device in wiz._devices:
                if light.mac == device.mac:
                    name = device.name
                    break
            else:
                name = light.mac

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
        wiz._lights = []
        return Response()

    @app.get('/lights/off', response_class=HTMLResponse)
    async def lights_off(request: Request) -> Response:
        tasks = [light.turn_off() for light in await wiz.get_lights()]
        await asyncio.wait(tasks, timeout=config.timeout)
        return await get_lights(request)

    @app.get('/lights/on', response_class=HTMLResponse)
    async def lights_on(request: Request) -> Response:
        tasks = [light.turn_on() for light in await wiz.get_lights()]
        await asyncio.wait(tasks, timeout=config.timeout)
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

        if value:
            await asyncio.wait_for(light.turn_on(wl.PilotBuilder(brightness=int(value))), config.timeout)
        else:
            await asyncio.wait_for(light.turn_off(), config.timeout)

    @app.post('/lights/{name}/warmth', response_class=HTMLResponse)
    async def light_warmth(request: Request) -> None:
        name = request.path_params['name']
        value = (await request.form())['value']

        light = wl.wizlight(name)
        await light.updateState()
        timeout = config.timeout
        await asyncio.wait_for(light.turn_on(wl.PilotBuilder(colortemp=int(value))), timeout)  # type: ignore[arg-type]

    return app
