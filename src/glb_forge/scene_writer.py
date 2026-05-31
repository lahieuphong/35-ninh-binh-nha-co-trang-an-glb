from __future__ import annotations

import json
import struct
from pathlib import Path

from .scene import SceneMesh, Vec2, Vec3

GLB_MAGIC = 0x46546C67      # b"glTF"
GLB_VERSION = 2
CHUNK_JSON = 0x4E4F534A     # b"JSON"
CHUNK_BIN = 0x004E4942      # b"BIN\0"

FLOAT = 5126
UNSIGNED_SHORT = 5123
UNSIGNED_INT = 5125
ARRAY_BUFFER = 34962
ELEMENT_ARRAY_BUFFER = 34963
TRIANGLES = 4

REPEAT = 10497
LINEAR = 9729
LINEAR_MIPMAP_LINEAR = 9987


def _pad4(data: bytes, pad_byte: bytes) -> bytes:
    padding = (4 - len(data) % 4) % 4
    return data + pad_byte * padding


def _append_aligned(blob: bytearray, data: bytes) -> int:
    while len(blob) % 4 != 0:
        blob.append(0)
    offset = len(blob)
    blob.extend(data)
    return offset


def _pack_vec3(values: list[Vec3]) -> bytes:
    return b"".join(struct.pack("<3f", *v) for v in values)


def _pack_vec2(values: list[Vec2]) -> bytes:
    return b"".join(struct.pack("<2f", *v) for v in values)


def _pack_indices(indices: list[int]) -> tuple[bytes, int]:
    if max(indices) <= 65535:
        return b"".join(struct.pack("<H", i) for i in indices), UNSIGNED_SHORT
    return b"".join(struct.pack("<I", i) for i in indices), UNSIGNED_INT


def _bounds(positions: list[Vec3]) -> tuple[list[float], list[float]]:
    return (
        [min(p[i] for p in positions) for i in range(3)],
        [max(p[i] for p in positions) for i in range(3)],
    )


def _texture_mime_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "image/png"
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    raise ValueError(f"Texture phải là PNG/JPG, không hỗ trợ: {path}")


def write_scene_glb(scene: SceneMesh, output_path: str | Path) -> Path:
    """Ghi SceneMesh nhiều material ra file GLB thuần Python.

    Writer này hỗ trợ cả baseColorTexture và normalTexture. Ảnh texture được
    nhúng thẳng vào BIN chunk của GLB, nên file output có thể mở độc lập.
    """
    scene.validate()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    positions = list(scene.positions)
    normals = list(scene.normals)

    uses_textures = any(m.base_color_texture or m.normal_texture for m in scene.materials)
    include_texcoords = bool(scene.texcoords) or uses_textures
    texcoords = list(scene.texcoords) if scene.texcoords else [(0.0, 0.0)] * len(positions)

    position_bytes = _pack_vec3(positions)
    normal_bytes = _pack_vec3(normals)

    bin_blob = bytearray()
    offset_positions = _append_aligned(bin_blob, position_bytes)
    offset_normals = _append_aligned(bin_blob, normal_bytes)

    position_min, position_max = _bounds(positions)

    buffer_views: list[dict] = [
        {
            "buffer": 0,
            "byteOffset": offset_positions,
            "byteLength": len(position_bytes),
            "target": ARRAY_BUFFER,
        },
        {
            "buffer": 0,
            "byteOffset": offset_normals,
            "byteLength": len(normal_bytes),
            "target": ARRAY_BUFFER,
        },
    ]

    accessors: list[dict] = [
        {
            "bufferView": 0,
            "byteOffset": 0,
            "componentType": FLOAT,
            "count": len(positions),
            "type": "VEC3",
            "min": position_min,
            "max": position_max,
        },
        {
            "bufferView": 1,
            "byteOffset": 0,
            "componentType": FLOAT,
            "count": len(normals),
            "type": "VEC3",
        },
    ]

    texcoord_accessor_index: int | None = None
    if include_texcoords:
        texcoord_bytes = _pack_vec2(texcoords)
        offset_texcoords = _append_aligned(bin_blob, texcoord_bytes)
        texcoord_buffer_view = len(buffer_views)
        buffer_views.append(
            {
                "buffer": 0,
                "byteOffset": offset_texcoords,
                "byteLength": len(texcoord_bytes),
                "target": ARRAY_BUFFER,
            }
        )
        texcoord_accessor_index = len(accessors)
        accessors.append(
            {
                "bufferView": texcoord_buffer_view,
                "byteOffset": 0,
                "componentType": FLOAT,
                "count": len(texcoords),
                "type": "VEC2",
            }
        )

    primitives: list[dict] = []

    for material_index, indices in scene.indices_by_material.items():
        if not indices:
            continue

        index_bytes, index_component_type = _pack_indices(indices)
        offset_indices = _append_aligned(bin_blob, index_bytes)

        buffer_view_index = len(buffer_views)
        buffer_views.append(
            {
                "buffer": 0,
                "byteOffset": offset_indices,
                "byteLength": len(index_bytes),
                "target": ELEMENT_ARRAY_BUFFER,
            }
        )

        accessor_index = len(accessors)
        accessors.append(
            {
                "bufferView": buffer_view_index,
                "byteOffset": 0,
                "componentType": index_component_type,
                "count": len(indices),
                "type": "SCALAR",
            }
        )

        attributes = {
            "POSITION": 0,
            "NORMAL": 1,
        }
        if texcoord_accessor_index is not None:
            attributes["TEXCOORD_0"] = texcoord_accessor_index

        primitives.append(
            {
                "attributes": attributes,
                "indices": accessor_index,
                "material": material_index,
                "mode": TRIANGLES,
            }
        )

    samplers: list[dict] = []
    images: list[dict] = []
    textures: list[dict] = []
    texture_cache: dict[Path, int] = {}

    if uses_textures:
        samplers.append(
            {
                "magFilter": LINEAR,
                "minFilter": LINEAR_MIPMAP_LINEAR,
                "wrapS": REPEAT,
                "wrapT": REPEAT,
            }
        )

    def register_texture(texture_path: str | None) -> int | None:
        if not texture_path:
            return None
        path = Path(texture_path)
        if not path.is_absolute():
            path = path.resolve()
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy texture: {path}")

        key = path.resolve()
        if key in texture_cache:
            return texture_cache[key]

        data = path.read_bytes()
        offset_image = _append_aligned(bin_blob, data)
        buffer_view_index = len(buffer_views)
        buffer_views.append(
            {
                "buffer": 0,
                "byteOffset": offset_image,
                "byteLength": len(data),
            }
        )

        image_index = len(images)
        images.append(
            {
                "name": path.stem,
                "mimeType": _texture_mime_type(path),
                "bufferView": buffer_view_index,
            }
        )

        texture_index = len(textures)
        textures.append(
            {
                "sampler": 0 if samplers else None,
                "source": image_index,
            }
        )
        texture_cache[key] = texture_index
        return texture_index

    gltf_materials: list[dict] = []
    for material in scene.materials:
        pbr = {
            "baseColorFactor": list(material.color),
            "metallicFactor": material.metallic,
            "roughnessFactor": material.roughness,
        }

        base_texture_index = register_texture(material.base_color_texture)
        if base_texture_index is not None:
            pbr["baseColorTexture"] = {"index": base_texture_index}

        gltf_material = {
            "name": material.name,
            "doubleSided": material.double_sided,
            "pbrMetallicRoughness": pbr,
        }

        # glTF chỉ dùng kênh alpha của baseColorFactor/texture khi alphaMode được bật.
        # Tự động đặt BLEND cho vật liệu có alpha < 1 để nước/đáy hồ có cảm giác trong suốt.
        if len(material.color) >= 4 and material.color[3] < 0.999:
            gltf_material["alphaMode"] = "BLEND"

        normal_texture_index = register_texture(material.normal_texture)
        if normal_texture_index is not None:
            gltf_material["normalTexture"] = {
                "index": normal_texture_index,
                "scale": material.normal_scale,
            }

        gltf_materials.append(gltf_material)

    gltf_json = {
        "asset": {
            "version": "2.0",
            "generator": "35-ninh-binh-nha-co-trang-an-glb pure-python textured scene writer",
        },
        "scene": 0,
        "scenes": [
            {
                "name": "Scene",
                "nodes": [0],
            }
        ],
        "nodes": [
            {
                "name": scene.name,
                "mesh": 0,
            }
        ],
        "meshes": [
            {
                "name": scene.name,
                "primitives": primitives,
            }
        ],
        "materials": gltf_materials,
        "buffers": [
            {
                "byteLength": len(bin_blob),
            }
        ],
        "bufferViews": buffer_views,
        "accessors": accessors,
    }

    if samplers:
        gltf_json["samplers"] = samplers
    if images:
        gltf_json["images"] = images
    if textures:
        # Loại bỏ sampler None nếu không dùng texture sampler.
        gltf_json["textures"] = [
            {k: v for k, v in texture.items() if v is not None}
            for texture in textures
        ]

    json_bytes = json.dumps(gltf_json, separators=(",", ":")).encode("utf-8")
    json_chunk = _pad4(json_bytes, b" ")
    bin_chunk = _pad4(bytes(bin_blob), b"\x00")

    total_length = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)

    glb_data = b"".join(
        [
            struct.pack("<III", GLB_MAGIC, GLB_VERSION, total_length),
            struct.pack("<II", len(json_chunk), CHUNK_JSON),
            json_chunk,
            struct.pack("<II", len(bin_chunk), CHUNK_BIN),
            bin_chunk,
        ]
    )

    output_path.write_bytes(glb_data)
    return output_path
