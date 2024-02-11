# CAN-TCP Monitor Project

## Introduction
The CAN-TCP Monitor project involves emulating two devices, A and B, which communicate with a FastAPI application through CAN-TCP gateways. Devices A and B report their operational status by transmitting random numbers to the application for monitoring purposes and perform operations on the data. The system also allows sending commands to device B.  

![image_CANTCP](https://github.com/jarczano/Recruitment-Task/assets/107764304/229380ec-e24d-4dbb-b169-41bd9792144f)  
Overview drawing of CAN-TCP network with one gateway  

### Key Features
- **Data Monitoring:** The application enables tracking of data transmitted from devices A and B, as well as the values of operations performed by block C.
- **Sending Commands:** Capability to send messages to device B.
- **Web Interface:** Accessible web page providing a user interface for monitoring parameters and sending data to device B.

![screen](https://github.com/jarczano/Recruitment-Task/assets/107764304/81237ae0-5f22-430e-9580-d2aa6b9236bc)

## Project File Structure

- **device_class:** Class emulating a device connected to the CAN-TCP gateway.
- **device_a:** Launches a server emitting device A with a gateway.
- **device_b:** Launches a server emitting device B with a gateway.
- **utils:** Contains functions for saving and reading data from CAN frames.
- **module_c:** Class emulating block C.
- **main:** FastAPI application allowing:
  - Monitoring data received from devices using the `tcp_client()` function.
  - Sending data to device B using the `send_message()` function.
  - `watchdog()` function for continuously sending watchdog-resetting messages.

## Instructions

1. Install the necessary dependencies using `pip install -r requirements.txt`.
2. Run the emulation of device A: `python device_a.py`.
3. Run the emulation of device B: `python device_b.py`.
4. Start the application: `uvicorn main:app`.
5. The application will be running at `http://localhost:8000`. Upon accessing this URL, a page showcasing the functionality of the application will be displayed.

**Note:** This project requires Python version 3.10


