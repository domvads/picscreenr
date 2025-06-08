# Simple CLI tool for storing metadata in PNG files and a local JSON index
import argparse
import json
import os
import struct
import zlib

METADATA_FILE = 'metadata.json'
PNG_HEADER = b'\x89PNG\r\n\x1a\n'


def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_metadata(data):
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def read_text_chunk(data, keyword):
    pos = len(PNG_HEADER)
    while pos + 8 <= len(data):
        length = int.from_bytes(data[pos:pos+4], 'big')
        chunk_type = data[pos+4:pos+8]
        pos += 8
        chunk_data = data[pos:pos+length]
        pos += length
        crc = data[pos:pos+4]
        pos += 4
        if chunk_type == b'tEXt':
            try:
                key, value = chunk_data.split(b'\x00', 1)
                if key.decode('latin-1') == keyword:
                    return value.decode('latin-1')
            except Exception:
                pass
        if chunk_type == b'IEND':
            break
    return None


def write_text_chunk(path, keyword, text):
    with open(path, 'rb') as f:
        data = f.read()
    if not data.startswith(PNG_HEADER):
        raise ValueError('Only PNG files are supported')
    # remove existing chunk with same keyword if present
    chunks = []
    pos = len(PNG_HEADER)
    chunks.append(data[:pos])
    found = False
    while pos + 8 <= len(data):
        length = int.from_bytes(data[pos:pos+4], 'big')
        ctype = data[pos+4:pos+8]
        pos += 8
        chunk_data = data[pos:pos+length]
        pos += length
        crc = data[pos:pos+4]
        pos += 4
        if ctype == b'tEXt':
            try:
                key, _ = chunk_data.split(b'\x00', 1)
                if key.decode('latin-1') == keyword:
                    found = True
                    continue  # skip existing chunk
            except Exception:
                pass
        chunk = (length.to_bytes(4, 'big') + ctype + chunk_data + crc)
        chunks.append(chunk)
        if ctype == b'IEND':
            break
    # build new text chunk
    text_data = keyword.encode('latin-1') + b'\x00' + text.encode('latin-1')
    length_bytes = len(text_data).to_bytes(4, 'big')
    crc = zlib.crc32(b'tEXt' + text_data) & 0xffffffff
    crc_bytes = struct.pack('>I', crc)
    new_chunk = length_bytes + b'tEXt' + text_data + crc_bytes
    # insert before IEND
    chunks.insert(-1, new_chunk)
    with open(path, 'wb') as f:
        for chunk in chunks:
            f.write(chunk)


def add_metadata(image_path, description, tags):
    abs_path = os.path.abspath(image_path)
    data = load_metadata()
    data[abs_path] = {
        'description': description,
        'tags': tags,
    }
    save_metadata(data)
    if description or tags:
        text = json.dumps({'description': description, 'tags': tags})
        write_text_chunk(image_path, 'picscreenr', text)


def get_metadata(image_path):
    abs_path = os.path.abspath(image_path)
    data = load_metadata()
    meta = data.get(abs_path)
    if meta is None:
        try:
            with open(image_path, 'rb') as f:
                img_data = f.read()
            text = read_text_chunk(img_data, 'picscreenr')
            if text:
                meta = json.loads(text)
        except Exception:
            pass
    return meta


def main():
    parser = argparse.ArgumentParser(description='Store metadata in PNG files and local index.')
    sub = parser.add_subparsers(dest='cmd', required=True)

    add_p = sub.add_parser('add', help='Add metadata to an image')
    add_p.add_argument('image', help='Path to PNG image')
    add_p.add_argument('--description', help='Image description', default='')
    add_p.add_argument('--tags', nargs='*', default=[], help='Tags for the image')

    get_p = sub.add_parser('get', help='Get metadata from an image')
    get_p.add_argument('image', help='Path to PNG image')

    args = parser.parse_args()
    if args.cmd == 'add':
        add_metadata(args.image, args.description, args.tags)
    elif args.cmd == 'get':
        meta = get_metadata(args.image)
        if meta:
            print(json.dumps(meta, indent=2))
        else:
            print('No metadata found')


if __name__ == '__main__':
    main()
