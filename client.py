#!/usr/bin/env python3

import sys
import json
import asyncio
import websockets

async def handler(loop):
    async with websockets.connect('ws://localhost:8765') as websocket:
        if len(sys.argv) == 2:
            await websocket.send(json.dumps({ 'action' : 'call', 'destination' : sys.argv[1] }))
        while(loop.is_running()):
            response = await websocket.recv()
            print(response)

loop = asyncio.get_event_loop()
loop.run_until_complete(handler(loop))
