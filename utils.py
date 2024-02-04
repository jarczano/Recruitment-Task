

def read_frame(frame):
    """
    The function reads a CAN frame consisting of 13 bytes and returns both the id_can and the transmitted data
    :param frame: 13 bytes CAN frame
    :return: CAN id, data
    """
    extended_frame = (frame[0] >> 7) & 0x01
    remote_frame = (frame[0] >> 6) & 0x01
    length_bit = frame[0] & 0xF
    can_id = frame[1:5] if extended_frame else frame[3:5]
    data = frame[5: 5 + length_bit]
    return can_id, data


def write_frame(extended_frame, remote_frame, can_id, data):
    """
    Function creates a 13 byte CAN frame
    :param extended_frame: 1 is extended frame, 0 is standard frame
    :param remote_frame: 1 is remote frame, 0 is data frame
    :param can_id: device ID CAN
    :param data: data list, each element from 0 to 255, maximum length 8
    :return: CAN frame
    """
    length_bit = len(data)
    B = bin(length_bit)[2:].zfill(4)
    first_byte = str(extended_frame) + str(remote_frame) + '00' + str(B)
    first_byte = int(int(first_byte, 2))

    filled_data = data + [0] * (8 - length_bit)
    frame = [first_byte] + can_id + filled_data
    return frame


