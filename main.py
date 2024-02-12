import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
import asyncio  # Imports asyncio for asynchronous programming
from fastapi.staticfiles import StaticFiles
from module_c import ModuleC
from utils import write_frame, read_frame
import websockets


class StatusTracker:
    # class to track which device the application is connected to
    def __init__(self):
        self.device_a_connect = False
        self.device_b_connect = False


app = FastAPI()  # Creates instances of FastAPI applications
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

module = ModuleC()  # Create an instance of C module
module.start()  # Start of calculation by C module

status_tracker = StatusTracker()


async def tcp_client(port, device, host='127.0.0.1'):
    """
    The function receives information from devices connected to CAN-TCP gateways.
    :param port: Gate port number
    :param device: The name of the device that is connected to the gateway. value = 'a' or 'b'
    :param host: Gateway host number
    """
    while True:  # Start endless loop to connect and receive data
        #  Establishes an asynchronous TCP connection to the server.
        while True:
            try:
                reader, writer = await asyncio.open_connection(host, port)
                break
            except Exception as e:
                print(f"Error while trying to connect: {e}")
                await asyncio.sleep(1)  # Delay before the next trial

        print(f"Connected to the server device {device} on {host}:{port}")

        status_tracker.device_a_connect = True if device == 'a' else status_tracker.device_a_connect
        status_tracker.device_b_connect = True if device == 'b' else status_tracker.device_b_connect

        try:
            while True:  # Starts an endless loop to continuously receive data
                data = await reader.read(1000)  # Asynchronously reads data from a TCP connection
                if data:  # Checks whether data has been received

                    message = eval(data.decode())  # Decodes data into text format and into lists

                    can_id, data = read_frame(message)

                    print(f"Device {device} with CAN ID: {can_id} sent data: {data}")

                    if device == 'a':
                        module.parameter_a = data[0]
                    elif device == 'b':
                        module.parameter_b = data[0]
                else:
                    print('BREAK')
                    break  # Termination of the loop, if there is no more data

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            status_tracker.device_a_connect = False if device == 'a' else status_tracker.device_a_connect
            status_tracker.device_b_connect = False if device == 'b' else status_tracker.device_b_connect
            writer.close()  # Closes the sending connection


async def watchdog(port, can_id, host='127.0.0.1'):
    """
    Function sends watchdog reset message every 400 ms
    :param port: Gate port number
    :param can_id: device ID CAN
    :param host: Gateway host number
    :return:
    """
    while True:  # Start endless loop to connect and receive data
        while True:  # Start  endless loop to connect
            try:
                reader, writer = await asyncio.open_connection(host, port)
                break
            except Exception as e:
                print(f"Error while trying to connect: {e}")
                await asyncio.sleep(1)
        try:
            while True:  # Start receive data
                # for example, let the watchdog message look like this
                watchdog_tag = 1
                frame = str(write_frame(1, 0, can_id, [watchdog_tag]))  # extended and data frame
                writer.write(frame.encode())
                await writer.drain()
                await asyncio.sleep(1)  # Here it should be about <0.5
        except Exception as e:
            print(f"Error: {e}")
        finally:
            writer.close()


async def send_message(port, data_message, can_id, host='127.0.0.1'):
    """
    Function sends a message to the gateway
    :param can_id: Device ID CAN
    :param port: Gate port number
    :param data_message:  data list, each element from 0 to 255, maximum length 8
    :param host: Gateway host number
    :return:
    """
    while True:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            break
        except Exception as e:
            print(f"Error while trying to connect: {e}")
            await asyncio.sleep(1)

    frame = str(write_frame(1, 0, can_id, data_message))  # create a proper frame
    writer.write(frame.encode())
    await writer.drain()


async def monitor_c_result():
    while True:
        print("Module C result: ", module.result)
        await asyncio.sleep(1)


@app.on_event("startup")
async def startup_event():  # Runs tcp_client, watchdog as a background task
    asyncio.create_task(first_websocket())
    asyncio.create_task(tcp_client(port=12345, device='a'))  # Listen to the device A
    asyncio.create_task(tcp_client(port=12346, device='b'))  # Listen to the device B
    asyncio.create_task(watchdog(port=12346, can_id=[0x12, 0x34, 0x56, 0x78]))
    asyncio.create_task(monitor_c_result())


@app.on_event("shutdown")
async def shutdown_event():
    module.stop()


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


async def data_stream_to_user(websocket: WebSocket):
    # Function send data from app to web user
    while True:

        message_a = module.parameter_a if status_tracker.device_a_connect else 'trying to connect'
        await websocket.send_text(json.dumps({'type': 'attribute_a', 'message': message_a}))

        message_b = module.parameter_b if status_tracker.device_b_connect else 'trying to connect'
        await websocket.send_text(json.dumps({'type': 'attribute_b', 'message': message_b}))

        await websocket.send_text(json.dumps({'type': 'attribute_c', 'message': module.result}))

        await asyncio.sleep(0.5)  # this is the time how often the data on the html page will be refreshed


async def receive_message(websocket: WebSocket):
    # Function listens for messages from the web client and then sends them to the CAN-TCP gateway
    while True:
        # Waiting for a message from the web client
        data = await websocket.receive_text()

        print(f"Received from web client: {data}")

        # Send data from app to gate with device B
        await send_message(port=12346, data_message=[data], can_id=[0x12, 0x34, 0x56, 0x78])


async def first_websocket():
    async with websockets.connect("ws://localhost:8000/ws"):
        pass


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()
    # Running two asynchronous functions simultaneously
    try:
        await asyncio.gather(
            data_stream_to_user(websocket),
            receive_message(websocket)
        )
    except WebSocketDisconnect:
        print("User disconnected")
