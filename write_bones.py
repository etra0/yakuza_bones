import sys
import os
import argparse
import csv
import io
import json

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
    'y0': { 'endianness': 'big', 'csv_index': 0 },
    'yk1': { 'endianness': 'little', 'csv_index': 1 },
    'yk2': { 'endianness': 'little', 'csv_index': 2 },
    'y4': { 'endianness': 'big', 'csv_index': 4 },
    'y5': { 'endianness': 'big', 'csv_index': 5 },
    'yds': { 'endianness': 'big', 'csv_index': 6},
    'yish': { 'endianness': 'big', 'csv_index': 7}
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
    json_path = os.path.join('ids', origin_file + '.json')
    with open(json_path, 'r') as f:
        data = json.loads(f.read())

    for key in data:
        c_data = data[key].to_bytes(2, endianness)
        new_value = bytearray(b'\x00'*0x20)
        new_value[0:2] = c_data
        new_value[2:len(key)+2] = key.encode()
        data[key] = bytes(new_value)

    data[''] = b'\x00'*0x20
    return data

def write_bytes(origin, data_table, byte_table, endianness, path=''):
    extension = origin[-3:]
    o_bone_dir, o_n_bones = OFFSETS[extension]

    if path != '':
        destination = os.path.join(path, origin)
    else:
        destination = origin

    with open(destination, 'rb') as binary_file:
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


    if path != '':
        print(path)
        path = path.strip('\\')
        new_path = f'{path}_modified'
        try:
            os.mkdir(new_path)
        except:
            pass
        print(os.path.join(new_path, destination))
        with open(f"{os.path.join(new_path, origin)}", 'wb') as binary_file:
            binary_file.write(binary_data)
    else:
        with open(f"{origin}_modified", 'wb') as binary_file:
            binary_file.write(binary_data)

if __name__ == "__main__":
    description="""
A tool to overwrite bones
Currently supported Games
    - Yakuza 0: y0
    - Yakuza Kiwami: yk1
    - Yakuza Kiwami 2: yk2
    - Yakuza 4: y4
    - Yakuza 5: y5
    - Yakuza Dead Souls: yds
    - Yakuza Ishin: yish
"""

    epilog = """
EXAMPLE

Replace Yakuza 0 bones into Yakuza 5 bones (useful when porting a model
from Yakuza 5 to Yakuza 0)
    write_bones.exe -ig y0 -og y5 -o bones_from_y5.gmd

If you want to replace an entire folder with GMT/GMD, add the -d flag:
    write_bones.exe -ig y0 -og y5 -d -o bones_from_y5.gmd
"""

    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-ig', '--inputgame', required=True, action='store', help='Game origin')
    parser.add_argument('-og', '--outputgame', required=True, action='store', help='Game destination')
    parser.add_argument('-o', '--outputfile', required=True, action='store', help='GMD output name')
    parser.add_argument('-d', '--dir', action='store_true', help='GMD output name')

    args = parser.parse_args()
    if args.inputgame not in GAME_DESCRIPTIONS:
        raise Exception("The game {args.origin} is not supported")
    if args.outputgame not in GAME_DESCRIPTIONS:
        raise Exception("The game {args.dest} is not supported")

    origin_game = GAME_DESCRIPTIONS[args.inputgame]
    dest_game = GAME_DESCRIPTIONS[args.outputgame]

    data_table = load_data_table(origin_game, dest_game)
    byte_table = load_byte_table(args.inputgame, origin_game['endianness'])

    if args.dir:
        files = os.listdir(args.outputfile)
        for f in files:
            if not f.endswith('gmt') and not f.endswith('gmd'):
                continue
            write_bytes(f, data_table, byte_table,
                        dest_game['endianness'], args.outputfile)
    else:
        write_bytes(args.outputfile, data_table, byte_table,
                    dest_game['endianness'])
