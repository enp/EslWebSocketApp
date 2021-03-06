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
    try:
        while(loop.is_running()):
            message = await websocket.recv()
            print('COMMAND  : '+message)
            command = json.loads(message)
            if (command['action'] == 'call' and command['destination']):
                await request('originate {origination_caller_id_number='+msisdn+'}sofia/gateway/mss/'+command['destination']+' &park()')
            elif (command['action'] == 'answer' and command['uuid']):
                await request('uuid_answer '+command['uuid'])
            elif (command['action'] == 'play' and command['uuid'] and command['file']):
                await request('uuid_broadcast '+ command['uuid']+' playback::/home/app/EslWebSocketApp/'+command['file'])
            elif (command['action'] == 'hangup' and command['uuid']):
                await request('uuid_kill  '+command['uuid']+' CALL_REJECTED')
    except BaseException as e:
        print("ERROR    : {} : {}".format(type(e).__name__, e))
    finally:
        sockets.remove(websocket)

async def events(host, loop):
    global connection    
    while(loop.is_running()):
        event = filter(await connection.recv_event())
        print('EVENT    : '+json.dumps(event))
        global sockets
        for socket in sockets:
            await socket.send(json.dumps(event))

if len(sys.argv) == 2:
    try:
        msisdn = sys.argv[1]
        loop = asyncio.get_event_loop()    
        connection = get_connection('sipbox', loop=loop)
        connection.connect()
        connection.subscribe(['BACKGROUND_JOB','CHANNEL_PARK','CHANNEL_ANSWER','PLAYBACK_START','PLAYBACK_STOP','CHANNEL_HANGUP'])    
        loop.run_until_complete(websockets.serve(commands, 'localhost', 8765))
        loop.run_until_complete(events('sipbox',loop))
    except BaseException as e:
        print("ERROR    : {} : {}".format(type(e).__name__, e))
