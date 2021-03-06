import sys
import os
import argparse
import json
import struct
"""
0x80    Bones offset
0x84    Number of bones
"""
ENDIANNESS = 'big'

OFFSETS = {
    'gmd': (0x80, 0x84),
    'gmt': (0x4C, 0x48)
}

def get_all_bones(folder):
    files = os.listdir(folder)
    all_bones = {}
    for f in files:
        if not f.endswith('gmd') and not f.endswith('gmt'):
            continue
        print(f"Dumping {f}")
        c_bones = get_bones(os.path.join(folder, f))
        all_bones.update(c_bones)
    return all_bones

def get_bones(filename):
    b_o, n_o = OFFSETS[filename[-3:]]
    bones = {}
    with open(filename, 'rb') as binary_file:
        binary_data = binary_file.read()

    c_endianness = ENDIANNESS
    endian_check = int.from_bytes(binary_data[0x04:0x06], ENDIANNESS)
    # We just assume that if the endiannes check is 0, just use little
    # 'cause that's the case for Kenzan
    if endian_check == 0:
        c_endianness = 'little'
    bones_offset = int.from_bytes(binary_data[b_o:b_o+4], c_endianness)
    n_bones = int.from_bytes(binary_data[n_o:n_o+4], c_endianness)
    print(hex(bones_offset))
    for i in range(0, n_bones):
        bone = binary_data[bones_offset+2:bones_offset+0x20].decode().strip('\x00')
        _id = binary_data[bones_offset:bones_offset+2]
        bones[bone] = int.from_bytes(_id, c_endianness)
        bones_offset += 0x20
    return bones


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A bone extractor tool")
    parser.add_argument('File', metavar='path', type=str, help='GMD file/path')
    parser.add_argument('-d', '--dir', action='store_true', help='The file is a folder')
    parser.add_argument('-bo', '--byteorder', action='store', help='Byte order (endianness)')
    parser.add_argument('-n', '--name', action='store', required=False, help='Output name')
    args = parser.parse_args()

    if args.byteorder is not None:
        ENDIANNESS = args.byteorder
    if not args.dir:
        bones = get_bones(args.File)
    else:
        bones = get_all_bones(args.File)
    name = args.name
    if not name:
        name = 'output.txt'
    with open(name, 'w') as f:
        f.write(json.dumps(bones, indent=4, sort_keys=True))

