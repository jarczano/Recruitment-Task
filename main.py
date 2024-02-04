from fastapi import FastAPI
import asyncio  # Imports asyncio for asynchronous programming

from module_c import ModuleC
from utils import write_frame, read_frame

app = FastAPI()  # Creates instances of FastAPI applications

module = ModuleC()  # Create an instance of C module
module.start()  # Start of calculation by C module


async def tcp_client(port, device, host='127.0.0.1'):
    """
    The function receives information from devices connected to CAN-TCP gateways.
    :param port: Gate port number
    :param device: The name of the device that is connected to the gateway. value = 'a' or 'b'
    :param host: Gateway host number
    """

    #  Establishes an asynchronous TCP connection to the server.
    while True:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            break
        except Exception as e:
            print(f"Error while trying to connect: {e}")
            await asyncio.sleep(1)  # Delay before the next trial

    print("Connected to the server!")

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
                break  # Termination of the loop, if there is no more data

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        writer.close()  # Closes the sending connection
        await writer.wait_closed()  # Waiting for the connection to close


async def watchdog(port, can_id, host='127.0.0.1'):
    """
    Function sends watchdog reset message every 400 ms
    :param port: Gate port number
    :param can_id: device ID CAN
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
    try:
        while True:
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
        await writer.wait_closed()


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
    asyncio.create_task(tcp_client(port=12345, device='a'))  # Listen to the device A
    asyncio.create_task(tcp_client(port=12346, device='b'))  # Listen to the device B
    asyncio.create_task(watchdog(port=12346, can_id=[0x12, 0x34, 0x56, 0x78]))
    asyncio.create_task(monitor_c_result())


@app.on_event("shutdown")
async def shutdown_event():
    module.stop()


@app.get("/")
async def read_root():
    return {"message": "FastAPI application listens for data from TCP servers."}

