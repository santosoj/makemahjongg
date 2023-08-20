from os import path
from sys import argv, exit

from makemahjongg.tileutil import mktileset


def main():
    if len(argv) < 3:
        print(f"Usage: {argv[0]} source_dir output_file")
        exit(-1)
    
    [_cmd, source_dir, output_file, *_] = argv

    if not path.isdir(source_dir):
        print(f"{source_dir} is not a directory.")
        exit(-1)

    tileset = mktileset(source_dir)
    tileset.save(output_file)


if __name__ == "__main__":
    main()
