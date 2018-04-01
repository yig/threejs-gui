#!/usr/bin/env python3

import websockets
import asyncio
import json
import os

port2pid = {}

DEFAULT_PORT = 9876

def send_data( data, port = None ):
    if port is None: port = DEFAULT_PORT
    port = int(port)
    
    setup_relay_server_if_needed( port )
    
    ## Send a message to the relay server. Wait until it is sent to return.
    async def send_one():
        async with websockets.connect('ws://localhost:%d' % port) as websocket:
            await websocket.send( json.dumps(data) )
    
    asyncio.get_event_loop().run_until_complete(send_one())

def setup_relay_server_if_needed( port ):
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

def setup_relay_server( port ):
    port = int(port)
    
    connected = set()
    
    async def relay_server( websocket, path ):
        ## Remember this new websocket
        print( "New client:", websocket )
        connected.add( websocket )
        
        try:
            async for msg in websocket:
                ## Broadcast any message to all other clients.
                other_clients = set(connected)
                other_clients.remove( websocket )
                print( "Broadcasting message from", websocket, "to", len( other_clients ), "other clients." )
                if len( other_clients ) > 0:
                    await asyncio.wait([ client.send( msg ) for client in other_clients ])
        finally:
            print( "Client disconnected:", websocket )
            connected.remove( websocket )
    
    print( "Starting a relay server listening on port", port )
    start_server = websockets.serve( relay_server, 'localhost', port )
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

def main():
    import argparse
    parser = argparse.ArgumentParser( description = "Echo messages to all connected WebSocket clients." )
    parser.add_argument( "--port", type = int, default = DEFAULT_PORT, help="The port to listen on." )
    args = parser.parse_args()
    
    setup_relay_server( args.port )

if __name__ == '__main__':
    main()
