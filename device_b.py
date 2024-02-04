from device_class import Device

if __name__ == "__main__":
    # Running a server pretending to be device B connected to the CAN-TCP gateway
    device_b = Device(name='device B', port=12346, id_can=[0x12, 0x34, 0x56, 0x79], receive=True)
    device_b.start_server()

