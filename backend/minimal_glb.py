import struct
import json
import base64

def create_minimal_glb():
    # Minimal GLTF JSON
    # A single node, scene, and asset info. No meshes to keep it simple and valid.
    # Or maybe a single empty mesh.
    gltf = {
        "asset": {"version": "2.0"},
        "scenes": [{"nodes": [0]}],
        "nodes": [{"name": "Cube", "mesh": 0}],
        "meshes": [{"primitives": [{"attributes": {}}]}] # Empty primitive? might be invalid.
    }
    
    # Let's use a slightly more complex one with a single triangle if possible, 
    # but strictly speaking, just a valid empty GLB is enough to test the viewer.
    # The viewer might show nothing, but it won't crash the decoder.
    # Actually, let's just make a valid "empty" GLB.
    gltf = {
        "asset": {"version": "2.0"},
        "scenes": [{"nodes": [0]}],
        "nodes": [{"name": "Root"}],
    }
    
    json_str = json.dumps(gltf, separators=(',', ':'))
    json_bytes = json_str.encode('utf-8')
    
    # Padding
    padding = b' ' * ((4 - (len(json_bytes) % 4)) % 4)
    json_bytes += padding
    
    # JSON Chunk
    json_chunk_type = 0x4E4F534A
    json_chunk_len = len(json_bytes)
    json_chunk = struct.pack('<II', json_chunk_len, json_chunk_type) + json_bytes
    
    # Header
    magic = 0x46546C67
    version = 2
    length = 12 + len(json_chunk)
    header = struct.pack('<III', magic, version, length)
    
    glb = header + json_chunk
    return base64.b64encode(glb).decode('utf-8')

if __name__ == "__main__":
    print(create_minimal_glb())
