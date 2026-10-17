import struct
import json
import hashlib
import io
import os
import shutil

def calc_integrity(data_bytes):
    block_size = 4 * 1024 * 1024
    blocks = []
    for i in range(0, len(data_bytes), block_size):
        chunk = data_bytes[i:i+block_size]
        blocks.append(hashlib.sha256(chunk).hexdigest())
    if not blocks:
        blocks = [hashlib.sha256(b"").hexdigest()]
    return {
        "algorithm": "SHA256",
        "hash": hashlib.sha256(data_bytes).hexdigest(),
        "blockSize": block_size,
        "blocks": blocks
    }

class AsarArchive:
    def __init__(self, asar_path):
        self.asar_path = asar_path
        self.header = None
        self.base_offset = 0
        self.files_map = {}  # virtual_path -> {'node': node_ref, 'data': None or bytes, 'original_offset': int, 'size': int}
        self._load()

    def _load(self):
        with open(self.asar_path, 'rb') as f:
            buf = f.read(16)
            if len(buf) < 16:
                raise ValueError("Invalid ASAR archive: file too small")
            u1, h_size, u2, j_len = struct.unpack('<IIII', buf)
            header_bytes = f.read(j_len)
            self.header = json.loads(header_bytes.decode('utf-8'))
            pad = (4 - (j_len % 4)) % 4
            if pad:
                f.read(pad)
            self.base_offset = 16 + j_len + pad

            def collect(node, p=''):
                for k, v in node.items():
                    curr_p = f"{p}/{k}"
                    if 'files' in v:
                        collect(v['files'], curr_p)
                    else:
                        is_unpacked = v.get('unpacked', False)
                        offset = int(v.get('offset', 0)) if not is_unpacked else 0
                        size = int(v.get('size', 0))
                        self.files_map[curr_p] = {
                            'node': v,
                            'data': None,
                            'original_offset': offset,
                            'size': size,
                            'unpacked': is_unpacked
                        }

            collect(self.header['files'])

    def list_files(self):
        return sorted(list(self.files_map.keys()))

    def has_file(self, virtual_path):
        if not virtual_path.startswith('/'):
            virtual_path = '/' + virtual_path
        return virtual_path in self.files_map

    def read_file(self, virtual_path):
        if not virtual_path.startswith('/'):
            virtual_path = '/' + virtual_path
        if virtual_path not in self.files_map:
            raise KeyError(f"File not found in asar: {virtual_path}")
        entry = self.files_map[virtual_path]
        if entry['data'] is not None:
            return entry['data']
        if entry['unpacked']:
            raise ValueError(f"File {virtual_path} is unpacked outside asar")

        with open(self.asar_path, 'rb') as f:
            f.seek(self.base_offset + entry['original_offset'])
            data = f.read(entry['size'])
            entry['data'] = data
            return data

    def read_text(self, virtual_path, encoding='utf-8'):
        return self.read_file(virtual_path).decode(encoding)

    def write_file(self, virtual_path, data_bytes):
        if not virtual_path.startswith('/'):
            virtual_path = '/' + virtual_path

        if virtual_path in self.files_map:
            entry = self.files_map[virtual_path]
            entry['data'] = data_bytes
            entry['size'] = len(data_bytes)
        else:
            # Create node in header
            parts = [p for p in virtual_path.split('/') if p]
            curr = self.header['files']
            for p in parts[:-1]:
                if p not in curr:
                    curr[p] = {'files': {}}
                curr = curr[p]['files']
            fname = parts[-1]
            node = {'size': len(data_bytes), 'offset': '0'}
            curr[fname] = node
            self.files_map[virtual_path] = {
                'node': node,
                'data': data_bytes,
                'original_offset': -1,
                'size': len(data_bytes),
                'unpacked': False
            }

    def write_text(self, virtual_path, text, encoding='utf-8'):
        self.write_file(virtual_path, text.encode(encoding))

    def save(self, output_path):
        """重新打包并输出到指定的 ASAR 文件"""
        # 收集所有非 unpacked 文件
        file_entries = []
        for path, entry in self.files_map.items():
            if not entry['unpacked']:
                file_entries.append((path, entry))

        # 保持稳定的顺序
        file_entries.sort(key=lambda x: (x[1]['original_offset'] if x[1]['original_offset'] >= 0 else 999999999, x[0]))

        new_data = io.BytesIO()
        current_offset = 0

        # 需要从原文件中读取未被修改的文件
        with open(self.asar_path, 'rb') as f_orig:
            for path, entry in file_entries:
                if entry['data'] is not None:
                    b = entry['data']
                else:
                    f_orig.seek(self.base_offset + entry['original_offset'])
                    b = f_orig.read(entry['size'])

                size = len(b)
                node_ref = entry['node']
                node_ref['size'] = size
                node_ref['offset'] = str(current_offset)
                node_ref['integrity'] = calc_integrity(b)
                new_data.write(b)
                current_offset += size

        json_str = json.dumps(self.header, separators=(',', ':'))
        json_bytes = json_str.encode('utf-8')
        j_len = len(json_bytes)
        pad = (4 - (j_len % 4)) % 4
        h_size = j_len + pad + 8
        u2_val = j_len + pad + 4

        tmp_out = output_path + ".tmp"
        with open(tmp_out, 'wb') as out:
            out.write(struct.pack('<IIII', 4, h_size, u2_val, j_len))
            out.write(json_bytes)
            if pad:
                out.write(b'\x00' * pad)
            out.write(new_data.getvalue())

        shutil.move(tmp_out, output_path)
