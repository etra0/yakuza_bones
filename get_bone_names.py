import sys
import os
import argparse
"""
0x80    Bones offset
0x84    Number of bones
"""

# if (len(sys.argv) == 1):
#     test_file = './testing_files/c_am_bone.gmd'
# else:
#     test_file = sys.argv[1]
# 
# with open(test_file, 'rb') as binary_file:
#     binary_data = binary_file.read()

def get_all_bones(folder):
    files = os.listdir(folder)
    all_bones = {}
    for f in files:
        c_bones = get_bones(os.path.join(folder, f))
        for bone in c_bones:
            if bone not in all_bones:
                all_bones[bone] = []
            all_bones[bone].append(f)
    # check if the bone is contained in all
    for key in all_bones:
        if len(all_bones[key]) == len(files):
            all_bones[key] = 'all'
    return all_bones

def get_bones(filename):
    bones = set()
    with open(filename, 'rb') as binary_file:
        binary_data = binary_file.read()

    bones_offset = int.from_bytes(binary_data[0x4C:0x50], 'big')
    n_bones = int.from_bytes(binary_data[0x48:0x4C], 'big')
    for i in range(0, n_bones):
        bone = binary_data[bones_offset+2:bones_offset+19].decode().strip('\x00')
        bones.add(bone)
        bones_offset += 0x20
    return bones



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A bone extractor tool")
    parser.add_argument('File', metavar='path', type=str, help='GMD file/path')
    parser.add_argument('-d', '--dir', action='store_true', help='The file is a folder')
    parser.add_argument('-n', '--name', action='store', required=False, help='Output name')
    args = parser.parse_args()
    if not args.dir:
        bones = get_bones(args.File)
    else:
        bones = get_all_bones(args.File)
        bones = [f"{key};{bones[key]}" for key in bones]
    name = args.name
    if not name:
        name = 'ouput.txt'
    with open(name, 'w') as f:
        f.write('\n'.join(bones))



