from device_class import Device

if __name__ == "__main__":
    # Running a server pretending to be device A connected to the CAN-TCP gateway
    device_a = Device(name='device A', port=12345, id_can=[0x12, 0x34, 0x56, 0x78])
    device_a.start_server()

