import sys
import os
import argparse
import csv
import io
"""
0x80    Bones offset
0x84    Number of bones
"""

"""
origin & dest can be `y0` or `y5`
"""
def load_data_table(origin, dest):
    order = ['y0', 'y5']

    data_table = {}
    i_orig = order.index(origin)
    i_dest = order.index(dest)

    with open('data.csv') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        csvreader.__next__()
        for row in csvreader:
            v_orig = row[i_orig]
            v_dest = row[i_dest]
            data_table[v_dest] = v_orig

    return data_table

def load_byte_table(origin_file):
    with open(origin_file, 'rb') as binary_file:
        binary_data = binary_file.read()

    data_table = {}
    offset_bones = int.from_bytes(binary_data[0x80:0x84], 'big')
    n_bones = int.from_bytes(binary_data[0x84:0x88], 'big')
    for i in range(0, n_bones):
        name_bone = binary_data[offset_bones+0x2:offset_bones+0x20].decode().strip('\x00')
        data_bone = binary_data[offset_bones:offset_bones+0x20]
        data_table[name_bone] = data_bone
        offset_bones += 0x20
    data_table[''] = b'\x00'*0x20
    return data_table

def write_bytes(origin, data_table, byte_table):
    with open(origin, 'rb') as binary_file:
        binary_data = bytearray(binary_file.read())

    offset_bones = int.from_bytes(binary_data[0x80:0x84], 'big')
    n_bones = int.from_bytes(binary_data[0x84:0x88], 'big')
    print(offset_bones, n_bones)

    for i in range(0, n_bones):
        name_bone = binary_data[offset_bones+0x2:offset_bones+0x20].decode().strip('\x00')
        equivalent_bone = data_table[name_bone]
        print(name_bone, equivalent_bone)

        if equivalent_bone not in byte_table:
            d_equivalent_bone = b'\x00'*0x20
        else:
            d_equivalent_bone = byte_table[equivalent_bone]

        binary_data[offset_bones:offset_bones+0x20] = d_equivalent_bone

        offset_bones += 0x20


    with open(f"{origin}_modified", 'wb') as binary_file:
        binary_file.write(binary_data)



if __name__ == "__main__":
    byte_table = load_byte_table('testing_files/c_am_bone.gmd')
    data_table = load_data_table('y5', 'y0')
    write_bytes('./testing_files/c_at_bone.gmd', data_table, byte_table)

#     parser = argparse.ArgumentParser(description="A bone extractor tool")
#     parser.add_argument('File', metavar='path', type=str, help='GMD file/path')
#     parser.add_argument('-d', '--dir', action='store_true', help='The file is a folder')
#     parser.add_argument('-n', '--name', action='store', required=False, help='Output name')
#     args = parser.parse_args()
#     if not args.dir:
#         bones = get_bones(args.File)
#     else:
#         bones = get_all_bones(args.File)
#     bones = [f"{key};{bones[key]}" for key in bones]
#     name = args.name
#     if not name:
#         name = 'ouput.txt'
#     with open(name, 'w') as f:
#         f.write('\n'.join(bones))



