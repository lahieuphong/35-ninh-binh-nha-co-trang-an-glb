from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

Vec3 = tuple[float, float, float]
Vec2 = tuple[float, float]
ColorRGBA = tuple[float, float, float, float]


@dataclass(frozen=True)
class Material:
    name: str
    color: ColorRGBA
    metallic: float = 0.0
    roughness: float = 0.82
    double_sided: bool = True
    base_color_texture: str | None = None
    normal_texture: str | None = None
    normal_scale: float = 0.55


def v_add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def v_sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def v_mul(a: Vec3, s: float) -> Vec3:
    return (a[0] * s, a[1] * s, a[2] * s)


def v_dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def v_cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def v_len(a: Vec3) -> float:
    return math.sqrt(v_dot(a, a))


def v_norm(a: Vec3) -> Vec3:
    length = v_len(a)
    if length < 1e-9:
        return (0.0, 1.0, 0.0)
    return (a[0] / length, a[1] / length, a[2] / length)


def v_lerp(a: Vec3, b: Vec3, t: float) -> Vec3:
    return (
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
        a[2] + (b[2] - a[2]) * t,
    )


class SceneMesh:
    """Một mesh lớn có nhiều material, phù hợp cho scene procedural.

    Writer sẽ xuất toàn bộ scene thành 1 mesh GLB, mỗi material là 1 primitive.
    Cách này giữ project đơn giản nhưng vẫn đủ tạo nhà, sân, cây, núi, đồ trang trí.
    """

    def __init__(self, name: str = "Procedural Scene") -> None:
        self.name = name
        self.positions: list[Vec3] = []
        self.normals: list[Vec3] = []
        self.texcoords: list[Vec2] = []
        self.materials: list[Material] = []
        self.indices_by_material: dict[int, list[int]] = {}
        self._material_lookup: dict[str, int] = {}

    def add_material(
        self,
        name: str,
        color: ColorRGBA,
        *,
        metallic: float = 0.0,
        roughness: float = 0.82,
        double_sided: bool = True,
        base_color_texture: str | None = None,
        normal_texture: str | None = None,
        normal_scale: float = 0.55,
    ) -> int:
        if name in self._material_lookup:
            return self._material_lookup[name]

        index = len(self.materials)
        self.materials.append(
            Material(
                name=name,
                color=color,
                metallic=metallic,
                roughness=roughness,
                double_sided=double_sided,
                base_color_texture=base_color_texture,
                normal_texture=normal_texture,
                normal_scale=normal_scale,
            )
        )
        self.indices_by_material[index] = []
        self._material_lookup[name] = index
        return index

    def _push_vertex(self, position: Vec3, normal: Vec3, uv: Vec2 | None = None) -> int:
        index = len(self.positions)
        self.positions.append(position)
        self.normals.append(normal)
        self.texcoords.append(uv or (0.0, 0.0))
        return index

    def add_triangle(self, p0: Vec3, p1: Vec3, p2: Vec3, material: int, normal: Vec3 | None = None) -> None:
        n = v_norm(v_cross(v_sub(p1, p0), v_sub(p2, p0))) if normal is None else v_norm(normal)
        i0 = self._push_vertex(p0, n)
        i1 = self._push_vertex(p1, n)
        i2 = self._push_vertex(p2, n)
        self.indices_by_material[material].extend([i0, i1, i2])

    def add_quad(self, p0: Vec3, p1: Vec3, p2: Vec3, p3: Vec3, material: int, normal: Vec3 | None = None) -> None:
        n = v_norm(v_cross(v_sub(p1, p0), v_sub(p2, p0))) if normal is None else v_norm(normal)
        base = len(self.positions)
        self.positions.extend([p0, p1, p2, p3])
        self.normals.extend([n, n, n, n])
        self.texcoords.extend([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        self.indices_by_material[material].extend([base, base + 1, base + 2, base, base + 2, base + 3])

    def add_box(
        self,
        center: Vec3,
        size: Vec3,
        material: int,
        *,
        x_axis: Vec3 = (1.0, 0.0, 0.0),
        y_axis: Vec3 = (0.0, 1.0, 0.0),
        z_axis: Vec3 = (0.0, 0.0, 1.0),
    ) -> None:
        """Thêm hộp chữ nhật. Có thể xoay bằng 3 trục local đã chuẩn hóa."""
        x_axis = v_norm(x_axis)
        y_axis = v_norm(y_axis)
        z_axis = v_norm(z_axis)
        hx, hy, hz = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0

        def point(sx: float, sy: float, sz: float) -> Vec3:
            return v_add(
                center,
                v_add(v_mul(x_axis, sx * hx), v_add(v_mul(y_axis, sy * hy), v_mul(z_axis, sz * hz))),
            )

        p000 = point(-1, -1, -1)
        p100 = point(1, -1, -1)
        p110 = point(1, 1, -1)
        p010 = point(-1, 1, -1)
        p001 = point(-1, -1, 1)
        p101 = point(1, -1, 1)
        p111 = point(1, 1, 1)
        p011 = point(-1, 1, 1)

        # +Z, -Z, +X, -X, +Y, -Y
        self.add_quad(p001, p101, p111, p011, material)
        self.add_quad(p100, p000, p010, p110, material)
        self.add_quad(p101, p100, p110, p111, material)
        self.add_quad(p000, p001, p011, p010, material)
        self.add_quad(p011, p111, p110, p010, material)
        self.add_quad(p000, p100, p101, p001, material)

    def add_box_between(
        self,
        p0: Vec3,
        p1: Vec3,
        thickness: float,
        material: int,
        *,
        width: float | None = None,
        up_hint: Vec3 = (0.0, 1.0, 0.0),
    ) -> None:
        """Thêm thanh hộp nối từ p0 đến p1. Dùng cho xà, rui mè, hàng rào."""
        direction = v_sub(p1, p0)
        length = v_len(direction)
        if length < 1e-6:
            return
        z_axis = v_norm(direction)

        if abs(v_dot(z_axis, v_norm(up_hint))) > 0.94:
            up_hint = (1.0, 0.0, 0.0)

        x_axis = v_norm(v_cross(up_hint, z_axis))
        y_axis = v_norm(v_cross(z_axis, x_axis))
        center = v_mul(v_add(p0, p1), 0.5)
        self.add_box(center, (width or thickness, thickness, length), material, x_axis=x_axis, y_axis=y_axis, z_axis=z_axis)

    def add_frustum(
        self,
        center: Vec3,
        radius_bottom: float,
        radius_top: float,
        height: float,
        material: int,
        *,
        segments: int = 16,
        cap_bottom: bool = True,
        cap_top: bool = True,
    ) -> None:
        """Thêm hình trụ/hình nón cụt đứng theo trục Y."""
        y0 = center[1] - height / 2.0
        y1 = center[1] + height / 2.0
        bottom: list[Vec3] = []
        top: list[Vec3] = []
        for i in range(segments):
            angle = math.tau * i / segments
            c, s = math.cos(angle), math.sin(angle)
            bottom.append((center[0] + c * radius_bottom, y0, center[2] + s * radius_bottom))
            top.append((center[0] + c * radius_top, y1, center[2] + s * radius_top))

        for i in range(segments):
            j = (i + 1) % segments
            self.add_quad(bottom[i], bottom[j], top[j], top[i], material)

        if cap_bottom:
            c0 = (center[0], y0, center[2])
            for i in range(segments):
                j = (i + 1) % segments
                self.add_triangle(c0, bottom[i], bottom[j], material, normal=(0.0, -1.0, 0.0))

        if cap_top:
            c1 = (center[0], y1, center[2])
            for i in range(segments):
                j = (i + 1) % segments
                self.add_triangle(c1, top[j], top[i], material, normal=(0.0, 1.0, 0.0))

    def add_frustum_between(
        self,
        p0: Vec3,
        p1: Vec3,
        radius0: float,
        radius1: float,
        material: int,
        *,
        segments: int = 12,
        cap_ends: bool = True,
    ) -> None:
        """Hình trụ/nón cụt theo đoạn thẳng bất kỳ. Hữu ích cho thân cau, tre, cành."""
        axis = v_sub(p1, p0)
        length = v_len(axis)
        if length < 1e-6:
            return
        axis = v_norm(axis)
        helper = (0.0, 1.0, 0.0)
        if abs(v_dot(axis, helper)) > 0.92:
            helper = (1.0, 0.0, 0.0)
        u = v_norm(v_cross(axis, helper))
        v = v_norm(v_cross(axis, u))

        ring0: list[Vec3] = []
        ring1: list[Vec3] = []
        for i in range(segments):
            angle = math.tau * i / segments
            radial = v_add(v_mul(u, math.cos(angle)), v_mul(v, math.sin(angle)))
            ring0.append(v_add(p0, v_mul(radial, radius0)))
            ring1.append(v_add(p1, v_mul(radial, radius1)))

        for i in range(segments):
            j = (i + 1) % segments
            self.add_quad(ring0[i], ring0[j], ring1[j], ring1[i], material)

        if cap_ends:
            for i in range(segments):
                j = (i + 1) % segments
                self.add_triangle(p0, ring0[j], ring0[i], material, normal=v_mul(axis, -1.0))
                self.add_triangle(p1, ring1[i], ring1[j], material, normal=axis)

    def add_lathe(
        self,
        center: Vec3,
        profile: Sequence[tuple[float, float]],
        material: int,
        *,
        segments: int = 20,
        cap_bottom: bool = True,
        cap_top: bool = True,
    ) -> None:
        """Tạo vật thể tròn xoay từ profile (radius, y). Dùng cho chum nước."""
        rings: list[list[Vec3]] = []
        for radius, y in profile:
            ring: list[Vec3] = []
            for i in range(segments):
                angle = math.tau * i / segments
                ring.append((center[0] + math.cos(angle) * radius, center[1] + y, center[2] + math.sin(angle) * radius))
            rings.append(ring)

        for r in range(len(rings) - 1):
            for i in range(segments):
                j = (i + 1) % segments
                self.add_quad(rings[r][i], rings[r][j], rings[r + 1][j], rings[r + 1][i], material)

        if cap_bottom:
            bottom_center = (center[0], center[1] + profile[0][1], center[2])
            for i in range(segments):
                j = (i + 1) % segments
                self.add_triangle(bottom_center, rings[0][i], rings[0][j], material)

        if cap_top:
            top_center = (center[0], center[1] + profile[-1][1], center[2])
            last = rings[-1]
            for i in range(segments):
                j = (i + 1) % segments
                self.add_triangle(top_center, last[j], last[i], material)

    def validate(self) -> None:
        if not self.positions:
            raise ValueError("Scene rỗng: chưa có vertex nào.")
        if len(self.positions) != len(self.normals):
            raise ValueError("positions và normals phải có cùng độ dài.")
        if self.texcoords and len(self.texcoords) != len(self.positions):
            raise ValueError("texcoords phải rỗng hoặc có cùng độ dài với positions.")
        used_indices = [i for group in self.indices_by_material.values() for i in group]
        if not used_indices:
            raise ValueError("Scene chưa có tam giác nào.")
        max_index = len(self.positions) - 1
        for index in used_indices:
            if index < 0 or index > max_index:
                raise ValueError(f"Index {index} nằm ngoài range 0..{max_index}.")
