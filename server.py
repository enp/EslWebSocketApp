#!/usr/bin/env python3

import sys
import json
import asyncio
import websockets

from switchio import get_connection

msisdn = None

sockets = []

async def commands(websocket, path):
    global msisdn
    sockets.append(websocket)
    while(loop.is_running()):
        message = await websocket.recv()
        command = json.loads(message)
        print(command)
        if (command['action'] == 'call' and command['destination']):
            connection.api('originate {origination_caller_id_number='+msisdn+'}sofia/gateway/mss/'+command['destination']+' &park()')

async def events(host, loop):
    global connection    
    while(loop.is_running()):
        event = await connection.recv_event()
        name = event['Event-Name']
        uuid = event['Unique-ID']
        caller = event['Caller-Caller-ID-Number']
        called = event['Caller-Destination-Number']
        event = caller+' => '+called+' : '+name
        print(event)
        global sockets
        for socket in sockets:
            await socket.send(event)
        if name == 'CHANNEL_PARK':
            connection.api('uuid_answer '+uuid)
        elif name == 'CHANNEL_ANSWER':
            connection.api('uuid_broadcast '+uuid+' playback::/opt/media/welcome.wav')
        elif name == 'PLAYBACK_STOP':
            connection.api('uuid_kill  '+uuid+' playback::/opt/media/welcome.wav')

if len(sys.argv) == 2:
    msisdn = sys.argv[1]
    loop = asyncio.get_event_loop()    
    connection = get_connection('sipbox', loop=loop)
    connection.connect()
    connection.subscribe(['CHANNEL_PARK','CHANNEL_ANSWER','PLAYBACK_START','PLAYBACK_STOP','CHANNEL_HANGUP'])    
    loop.run_until_complete(websockets.serve(commands, 'localhost', 8765))
    loop.run_until_complete(events('sipbox',loop))
