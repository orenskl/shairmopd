import asyncio
import json
import logging
from tornado.websocket import websocket_connect
from dbus_next.aio import MessageBus
from dbus_next.constants import MessageType
from dbus_next.constants import BusType
from dbus_next import Message
from dbus_next.message import MessageType

MOPIDY_WS_URL = "ws://localhost:6680/mopidy/ws/"

log = logging.getLogger(__name__)

# ----- Mopidy WebSocket Listener -----
async def listen_to_mopidy():
    try:
        ws = await websocket_connect(MOPIDY_WS_URL)
        log.info("Connected to Mopidy WebSocket")
        while True:
            msg = await ws.read_message()
            if msg is None:
                log.info("Mopidy WebSocket closed")
                break
            data = json.loads(msg)
            if "event" in data:
                if data['event'] == "playback_state_changed":
                    if data['old_state'] == "stopped" and data['new_state'] == "playing":
                        log.info("Mopidy playback started")
                        bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
                        # Create the method call message
                        msg = Message(
                            destination='org.gnome.ShairportSync',
                            path='/org/gnome/ShairportSync',
                            interface='org.gnome.ShairportSync',
                            member='DropSession',
                            signature='',
                            body=[],
                            message_type=MessageType.METHOD_CALL,
                        )
                        reply = await bus.call(msg)
                        log.info(reply.body)
    except Exception as e:
        log.info(f"Mopidy connection failed: {e}")

# ----- D-Bus System Event Listener -----
async def listen_to_dbus():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    def handle_signal(msg):
        if msg.message_type != MessageType.SIGNAL:
            return
        log.info(f"D-Bus Signal: {msg.interface}.{msg.member}")
        if msg.body:
            log.info(f"Body: {msg.body}")

    bus.add_message_handler(handle_signal)

    await bus.introspect('org.gnome.ShairportSync', '/org/gnome/ShairportSync')
    await bus.request_name('org.freedesktop.shairmopd')

    log.info("Listening for D-Bus system signals...")

# ----- Main -----
async def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    log.info('shairmopd version ' + __version__)
    await asyncio.gather(
        listen_to_mopidy(),
        listen_to_dbus()
    )

if __name__ == "__main__":
    asyncio.run(main())
