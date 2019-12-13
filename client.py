#!/usr/bin/env python3

import sys
import json
import asyncio
import websockets

async def handler(loop):
    try:
        async with websockets.connect('ws://localhost:8765') as websocket:
            if len(sys.argv) == 2:
                await websocket.send(json.dumps({ 'action' : 'call', 'destination' : sys.argv[1] }))
            while(loop.is_running()):
                message = await websocket.recv()
                event = json.loads(message)
                print('EVENT    : '+json.dumps(event))
                if event['Event-Name'] == 'CHANNEL_PARK':
                    await websocket.send(json.dumps({ 'action' : 'answer', 'uuid' : event['Unique-ID'] }))
                elif event['Event-Name'] == 'CHANNEL_ANSWER':
                    await websocket.send(json.dumps({ 'action' : 'play', 'uuid' : event['Unique-ID'], 'file' : 'welcome.wav' }))
                elif event['Event-Name'] == 'PLAYBACK_STOP':
                    await websocket.send(json.dumps({ 'action' : 'hangup', 'uuid' : event['Unique-ID'] }))
                elif event['Event-Name'] == 'CHANNEL_HANGUP':
                    await websocket.close()
    except BaseException as e:
        print("ERROR    : {} : {}".format(type(e).__name__, e))

loop = asyncio.get_event_loop()
loop.run_until_complete(handler(loop))
