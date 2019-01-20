#!/usr/bin/env python3

import sys
import json
import asyncio
import websockets

from switchio import get_connection

msisdn = None

sockets = []

def filter(input):
    output = {}
    for key in ['Event-Name','Job-Command','Job-UUID','Unique-ID','Caller-Logical-Direction','Caller-Caller-ID-Number','Caller-Destination-Number','Hangup-Cause']:
            if key in input:
                output[key] = input[key]
    return output

async def request(data):
    global connection    
    print('REQUEST  : '+data)
    response = await connection.bgapi(data)
    print('RESPONSE : '+json.dumps(filter(response)))

async def commands(websocket, path):
    global msisdn
    sockets.append(websocket)
    while(loop.is_running()):
        message = await websocket.recv()
        print('COMMAND  : '+message)
        command = json.loads(message)
        if (command['action'] == 'call' and command['destination']):
            await request('originate {origination_caller_id_number='+msisdn+'}sofia/gateway/mss/'+command['destination']+' &park()')

async def events(host, loop):
    global connection    
    while(loop.is_running()):
        event = filter(await connection.recv_event())
        print('EVENT    : '+json.dumps(event))
        global sockets
        for socket in sockets:
            await socket.send(json.dumps(event))
        job = None
        if event['Event-Name'] == 'CHANNEL_PARK':
            await request('uuid_answer '+event['Unique-ID'])
        elif event['Event-Name'] == 'CHANNEL_ANSWER':
            await request('uuid_broadcast '+event['Unique-ID']+' playback::/opt/media/welcome.wav')
        elif event['Event-Name'] == 'PLAYBACK_STOP':
            await request('uuid_kill  '+event['Unique-ID']+' playback::/opt/media/welcome.wav')

if len(sys.argv) == 2:
    msisdn = sys.argv[1]
    loop = asyncio.get_event_loop()    
    connection = get_connection('sipbox', loop=loop)
    connection.connect()
    connection.subscribe(['BACKGROUND_JOB','CHANNEL_PARK','CHANNEL_ANSWER','PLAYBACK_START','PLAYBACK_STOP','CHANNEL_HANGUP'])    
    loop.run_until_complete(websockets.serve(commands, 'localhost', 8765))
    loop.run_until_complete(events('sipbox',loop))
