import sys
import os
import argparse
import csv
import io
"""
0x80    Bones offset
0x84    Number of bones

Offset Differences:
y3:
    0x8:    00 03 00 0B

y0: 0x8:    00 02 00 08
"""

"""
origin & dest can be `y0` or `y5`
"""

# For the future
GAME_DESCRIPTIONS = {
    'y5': { 'endianness': 'big', 'csv_index': 1 },
    'y0': { 'endianness': 'big', 'csv_index': 0 },
    'yk1': { 'endianness': 'little', 'csv_index': 0 },
    'yk2': { 'endianness': 'little', 'csv_index': 0 },
}

# offset for the initial bone reading
# (offset_bones, n_bones)
OFFSETS = {
    'gmd': (0x80, 0x84),
    'gmt': (0x4C, 0x48)
}

def load_data_table(origin, dest):

    data_table = {}
    i_orig, i_dest = origin['csv_index'], dest['csv_index']

    with open('data.csv') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        csvreader.__next__()
        for row in csvreader:
            v_orig = row[i_orig]
            v_dest = row[i_dest]
            data_table[v_dest] = v_orig

    return data_table

def load_byte_table(origin_file, endianness):
    extension = origin_file[-3:]
    o_bone_dir, o_n_bones = OFFSETS[extension]

    with open(origin_file, 'rb') as binary_file:
        binary_data = binary_file.read()

    data_table = {}
    offset_bones = int.from_bytes(binary_data[o_bone_dir:o_bone_dir+0x04], endianness)
    n_bones = int.from_bytes(binary_data[o_n_bones:o_n_bones+4], endianness)
    print(f"Offset: {hex(offset_bones)}, n_bones: {hex(n_bones)}")
    for i in range(0, n_bones):
        name_bone = binary_data[offset_bones+0x2:offset_bones+0x20].decode().strip('\x00')
        data_bone = binary_data[offset_bones:offset_bones+0x20]
        data_table[name_bone] = data_bone
        offset_bones += 0x20
    data_table[''] = b'\x00'*0x20
    return data_table

def write_bytes(origin, data_table, byte_table, endianness):
    extension = origin[-3:]
    o_bone_dir, o_n_bones = OFFSETS[extension]

    with open(origin, 'rb') as binary_file:
        binary_data = bytearray(binary_file.read())

    offset_bones = int.from_bytes(binary_data[o_bone_dir:o_bone_dir+0x04], endianness)
    n_bones = int.from_bytes(binary_data[o_n_bones:o_n_bones+4], endianness)
    print(offset_bones, n_bones)

    for i in range(0, n_bones):
        name_bone = binary_data[offset_bones+0x2:offset_bones+0x20].decode().strip('\x00')

        if name_bone not in data_table:
            print(f"WARNING: {name_bone} not in data.csv")
            offset_bones += 0x20
            continue

        equivalent_bone = data_table[name_bone]
        print(name_bone, "->", equivalent_bone)

        if equivalent_bone not in byte_table:
            d_equivalent_bone = b'\x00'*0x20
        else:
            d_equivalent_bone = byte_table[equivalent_bone]

        binary_data[offset_bones:offset_bones+0x20] = d_equivalent_bone

        offset_bones += 0x20


    with open(f"{origin}_modified", 'wb') as binary_file:
        binary_file.write(binary_data)

if __name__ == "__main__":
    description="""
A tool to overwrite bones
Currently supported Games
    - Yakuza 0: y0
    - Yakuza Kiwami: yk1
    - Yakuza Kiwami 2: yk2
    - Yakuza 5: y5
"""

    epilog = """
EXAMPLE

Replace Yakuza 0 bones into Yakuza 5 bones (useful when porting a model
from Yakuza 5 to Yakuza 0)
    write_bones.exe -og y0 -dg y5 -i bones_from_y0.gmd -o bones_from_y5.gmd
"""

    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-ig', '--inputgame', required=True, action='store', help='Game origin')
    parser.add_argument('-og', '--outputgame', required=True, action='store', help='Game destination')
    parser.add_argument('-i', '--inputfile', required=True, action='store', help='GMD input file')
    parser.add_argument('-o', '--outputfile', required=True, action='store', help='GMD output name')

    args = parser.parse_args()
    if args.inputgame not in GAME_DESCRIPTIONS:
        raise Exception("The game {args.origin} is not supported")
    if args.outputgame not in GAME_DESCRIPTIONS:
        raise Exception("The game {args.dest} is not supported")

    origin_game = GAME_DESCRIPTIONS[args.inputgame]
    dest_game = GAME_DESCRIPTIONS[args.outputgame]

    byte_table = load_byte_table(args.inputfile, origin_game['endianness'])
    data_table = load_data_table(origin_game, dest_game)
    write_bytes(args.outputfile, data_table, byte_table, dest_game['endianness'])
