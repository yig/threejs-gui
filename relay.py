import websockets
import asyncio
import json
import os

port2pid = {}

def send_data( data, port = None ):
    if port is None: port = 9876
    port = int(port)
    
    ## Create a relay server if needed.
    if port not in port2pid:
        pid = os.fork()
        ## If we are the forked process, setup a relay server.
        if pid == 0:
            setup_relay_server( port )
            return
        else:
            ## Otherwise, just remember that we have this relay server running.
            port2pid[port] = pid
    
    ## Send one message to the relay server.
    async def send_one():
        async with websockets.connect('ws://localhost:%d' % port) as websocket:
            await websocket.send( json.dumps(data) )
    
    asyncio.get_event_loop().run_until_complete(send_one())

def setup_relay_server( port ):
    port = int(port)
    
    connected = set()
    
    async def relay_server( websocket, path ):
        ## Remember this new websocket
        connected.add( websocket )
        
        try:
            async for msg in websocket:
                ## Broadcast any message to all other clients.
                for client in connected:
                    await asyncio.wait([
                        client.send( msg )
                        for client in connected
                        if client is not websocket
                        ])
        finally:
            connected.remove( websocket )
    
    start_server = websockets.serve( relay_server, 'localhost', port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
