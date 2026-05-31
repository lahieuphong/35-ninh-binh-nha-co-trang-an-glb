from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .scene import (
    SceneMesh,
    Vec3,
    v_add,
    v_cross,
    v_len,
    v_lerp,
    v_mul,
    v_norm,
    v_sub,
)


@dataclass(frozen=True)
class TreeMaterials:
    """Các material dùng riêng cho cây ven Hồ Gươm.

    Tách material sáng/tối/ấm giúp tán cây không còn một khối xanh đều như bản cũ.
    """

    bark: int
    branch: int
    foliage_deep: int
    foliage_dark: int
    foliage_sunlit: int
    foliage_warm: int
    foliage_haze: int


def _rand(rng: random.Random, lo: float, hi: float) -> float:
    return rng.uniform(lo, hi)


def _polar(angle: float, radius: float = 1.0) -> Vec3:
    return (math.cos(angle) * radius, 0.0, math.sin(angle) * radius)


def _orthonormal_from_forward(forward: Vec3) -> tuple[Vec3, Vec3, Vec3]:
    f = v_norm(forward)
    helper = (0.0, 1.0, 0.0)
    if abs(f[1]) > 0.92:
        helper = (1.0, 0.0, 0.0)
    right = v_norm(v_cross(helper, f))
    up = v_norm(v_cross(f, right))
    return right, up, f


def _add_curved_frustum(
    scene: SceneMesh,
    start: Vec3,
    end: Vec3,
    radius_start: float,
    radius_end: float,
    material: int,
    *,
    rng: random.Random,
    bend: float = 0.08,
    steps: int = 4,
    segments: int = 8,
) -> None:
    """Thân/cành dạng nón cụt cong nhẹ, nhìn tự nhiên hơn trụ thẳng."""
    direction = v_sub(end, start)
    if v_len(direction) < 1e-5:
        return

    right, up, _ = _orthonormal_from_forward(direction)
    side_bias = v_add(v_mul(right, _rand(rng, -bend, bend)), v_mul(up, _rand(rng, -bend * 0.55, bend * 0.55)))

    prev = start
    prev_radius = radius_start
    for i in range(1, steps + 1):
        t = i / steps
        point = v_lerp(start, end, t)
        # Sin bend mạnh ở giữa đoạn, yếu ở hai đầu.
        point = v_add(point, v_mul(side_bias, math.sin(math.pi * t)))
        radius = radius_start + (radius_end - radius_start) * t
        scene.add_frustum_between(prev, point, prev_radius, radius, material, segments=segments, cap_ends=i == steps)
        prev = point
        prev_radius = radius


def _push_canopy_vertex(scene: SceneMesh, position: Vec3, center: Vec3, radii: Vec3, uv: tuple[float, float]) -> int:
    """Thêm vertex tán lá với normal mượt theo elip.

    Các tán lá cũ dùng normal phẳng theo từng mặt nên khi nhìn gần dễ có cảm
    giác đa giác/vuông. Normal mượt giúp cùng một số polygon nhưng silhouette và
    ánh sáng mềm hơn rõ rệt.
    """

    rx, ry, rz = (max(radii[0], 1e-4), max(radii[1], 1e-4), max(radii[2], 1e-4))
    normal = v_norm(((position[0] - center[0]) / rx, (position[1] - center[1]) / ry, (position[2] - center[2]) / rz))
    index = len(scene.positions)
    scene.positions.append(position)
    scene.normals.append(normal)
    scene.texcoords.append(uv)
    return index


def _add_irregular_ellipsoid(
    scene: SceneMesh,
    center: Vec3,
    radii: Vec3,
    material: int,
    *,
    rng: random.Random,
    segments: int = 26,
    rings: int = 13,
    wobble: float = 0.11,
    squash_bottom: float = 0.18,
) -> None:
    """Tán lá dạng cụm elip méo nhẹ, tránh cảm giác khối hộp/khối cầu giả."""
    rx, ry, rz = radii
    phase1 = _rand(rng, 0.0, math.tau)
    phase2 = _rand(rng, 0.0, math.tau)

    def ring_point(lat: float, seg: int, ring_index: int) -> Vec3:
        angle = math.tau * seg / segments
        radial = math.cos(lat)
        y = math.sin(lat) * ry
        if y < 0.0:
            y *= 1.0 - squash_bottom
        w = 1.0 + wobble * (
            0.45 * math.sin(angle * 2.0 + phase1)
            + 0.32 * math.sin(angle * 5.0 + ring_index * 0.9 + phase2)
            + 0.23 * math.sin((angle + lat) * 3.0 + phase1 * 0.7)
        )
        return (
            center[0] + math.cos(angle) * radial * rx * w,
            center[1] + y * (1.0 + wobble * 0.18 * math.sin(angle * 3.0 + phase2)),
            center[2] + math.sin(angle) * radial * rz * w,
        )

    ring_vertices: list[list[Vec3]] = []
    for r in range(1, rings):
        lat = -math.pi / 2.0 + math.pi * r / rings
        ring_vertices.append([ring_point(lat, s, r) for s in range(segments)])

    bottom = (center[0], center[1] - ry * (1.0 - squash_bottom), center[2])
    top = (center[0], center[1] + ry, center[2])

    first = ring_vertices[0]
    for s in range(segments):
        j = (s + 1) % segments
        base = len(scene.positions)
        _push_canopy_vertex(scene, bottom, center, radii, (0.5, 0.0))
        _push_canopy_vertex(scene, first[j], center, radii, (j / segments, 0.12))
        _push_canopy_vertex(scene, first[s], center, radii, (s / segments, 0.12))
        scene.indices_by_material[material].extend([base, base + 1, base + 2])

    for r in range(len(ring_vertices) - 1):
        a = ring_vertices[r]
        b = ring_vertices[r + 1]
        for s in range(segments):
            j = (s + 1) % segments
            base = len(scene.positions)
            v0 = (r + 1) / rings
            v1 = (r + 2) / rings
            _push_canopy_vertex(scene, a[s], center, radii, (s / segments, v0))
            _push_canopy_vertex(scene, a[j], center, radii, (j / segments, v0))
            _push_canopy_vertex(scene, b[j], center, radii, (j / segments, v1))
            _push_canopy_vertex(scene, b[s], center, radii, (s / segments, v1))
            scene.indices_by_material[material].extend([base, base + 1, base + 2, base, base + 2, base + 3])

    last = ring_vertices[-1]
    for s in range(segments):
        j = (s + 1) % segments
        base = len(scene.positions)
        _push_canopy_vertex(scene, top, center, radii, (0.5, 1.0))
        _push_canopy_vertex(scene, last[s], center, radii, (s / segments, 0.90))
        _push_canopy_vertex(scene, last[j], center, radii, (j / segments, 0.90))
        scene.indices_by_material[material].extend([base, base + 1, base + 2])


def _add_leaf_diamond(
    scene: SceneMesh,
    center: Vec3,
    material: int,
    *,
    rng: random.Random,
    width: float,
    height: float,
    tilt: float = 0.18,
) -> None:
    """Một lá/cụm lá nhỏ dạng oval mềm, không còn là hình thoi vuông cạnh."""
    angle = _rand(rng, 0.0, math.tau)
    right = v_norm((math.cos(angle), _rand(rng, -tilt, tilt), math.sin(angle)))
    up = v_norm((_rand(rng, -tilt, tilt), 1.0, _rand(rng, -tilt, tilt)))
    normal = v_norm(v_cross(right, up))

    base = len(scene.positions)
    scene.positions.append(center)
    scene.normals.append(normal)
    scene.texcoords.append((0.5, 0.5))

    # Fan 8 cạnh tạo card lá bo tròn, mép mềm hơn quad/hình thoi.
    segments = 8
    for i in range(segments):
        theta = math.tau * i / segments
        # Dáng hơi thuôn ở hai đầu như lá nhỏ, nhưng không sắc cạnh/vuông.
        c = math.cos(theta)
        ss = math.sin(theta)
        taper = 0.86 + 0.14 * abs(ss)
        p = v_add(
            center,
            v_add(v_mul(right, c * width * 0.5 * taper), v_mul(up, ss * height * 0.5)),
        )
        scene.positions.append(p)
        scene.normals.append(normal)
        scene.texcoords.append(((c + 1.0) * 0.5, (ss + 1.0) * 0.5))

    out = scene.indices_by_material[material]
    for i in range(segments):
        j = 1 + ((i + 1) % segments)
        out.extend((base, base + 1 + i, base + j))


def _random_point_on_canopy(center: Vec3, radii: Vec3, rng: random.Random, *, lower: float = -0.25) -> Vec3:
    y_frac = _rand(rng, lower, 0.82)
    radial = math.sqrt(max(0.0, 1.0 - y_frac * y_frac))
    angle = _rand(rng, 0.0, math.tau)
    edge = _rand(rng, 0.72, 1.05)
    return (
        center[0] + math.cos(angle) * radii[0] * radial * edge,
        center[1] + y_frac * radii[1],
        center[2] + math.sin(angle) * radii[2] * radial * edge,
    )


def _add_leaf_sparkle_layer(
    scene: SceneMesh,
    center: Vec3,
    radii: Vec3,
    materials: TreeMaterials,
    *,
    rng: random.Random,
    count: int,
    warm_ratio: float = 0.10,
) -> None:
    for _ in range(count):
        p = _random_point_on_canopy(center, radii, rng)
        if rng.random() < warm_ratio:
            mat = materials.foliage_warm
        elif rng.random() < 0.62:
            mat = materials.foliage_sunlit
        else:
            mat = materials.foliage_deep
        size = _rand(rng, 0.055, 0.135) * (1.0 + radii[1] * 0.22)
        _add_leaf_diamond(scene, p, mat, rng=rng, width=size * _rand(rng, 0.75, 1.15), height=size * _rand(rng, 1.0, 1.55))



def _add_leaf_cluster_sprays(
    scene: SceneMesh,
    center: Vec3,
    radii: Vec3,
    materials: TreeMaterials,
    *,
    rng: random.Random,
    count: int,
) -> None:
    """Cụm lá nhỏ đặt theo chùm, làm tán cây dày hơn mà vẫn không vuông giả."""
    for _ in range(count):
        anchor = _random_point_on_canopy(center, radii, rng, lower=-0.38)
        mat_base = materials.foliage_dark if rng.random() < 0.28 else materials.foliage_deep
        if rng.random() < 0.28:
            mat_base = materials.foliage_sunlit
        leaf_count = rng.randint(4, 7)
        spread = _rand(rng, 0.05, 0.15) * (1.0 + max(radii) * 0.15)
        for i in range(leaf_count):
            p = v_add(
                anchor,
                (
                    _rand(rng, -spread, spread),
                    _rand(rng, -spread * 0.55, spread * 0.70),
                    _rand(rng, -spread, spread),
                ),
            )
            mat = materials.foliage_warm if rng.random() < 0.035 else mat_base
            w = _rand(rng, 0.040, 0.090) * (1.0 + radii[1] * 0.10)
            h = _rand(rng, 0.070, 0.135) * (1.0 + radii[1] * 0.10)
            _add_leaf_diamond(scene, p, mat, rng=rng, width=w, height=h, tilt=0.28)


def _add_hanging_leaf_curtains(
    scene: SceneMesh,
    center: Vec3,
    radii: Vec3,
    materials: TreeMaterials,
    *,
    rng: random.Random,
    count: int,
) -> None:
    """Một ít cành/lá rủ gợi dáng lộc vừng quanh Hồ Gươm."""
    for _ in range(count):
        angle = _rand(rng, 0.0, math.tau)
        start = (
            center[0] + math.cos(angle) * radii[0] * _rand(rng, 0.25, 0.82),
            center[1] - radii[1] * _rand(rng, 0.10, 0.42),
            center[2] + math.sin(angle) * radii[2] * _rand(rng, 0.25, 0.82),
        )
        length = _rand(rng, 0.28, 0.72) * (0.8 + radii[1] * 0.3)
        end = (start[0] + _rand(rng, -0.04, 0.04), start[1] - length, start[2] + _rand(rng, -0.04, 0.04))
        scene.add_frustum_between(start, end, 0.012, 0.004, materials.branch, segments=7, cap_ends=True)
        for t in (0.28, 0.46, 0.64, 0.82, 0.94):
            leaf_center = v_lerp(start, end, t)
            leaf_center = v_add(leaf_center, (_rand(rng, -0.05, 0.05), _rand(rng, -0.02, 0.02), _rand(rng, -0.05, 0.05)))
            mat = materials.foliage_warm if rng.random() < 0.16 else materials.foliage_sunlit
            _add_leaf_diamond(scene, leaf_center, mat, rng=rng, width=_rand(rng, 0.08, 0.15), height=_rand(rng, 0.12, 0.24))


def _add_surface_roots(scene: SceneMesh, base: Vec3, trunk_radius: float, material: int, *, rng: random.Random) -> None:
    for i in range(rng.randint(4, 7)):
        angle = math.tau * i / rng.randint(5, 7) + _rand(rng, -0.22, 0.22)
        length = _rand(rng, 0.34, 0.78)
        start = v_add(base, (math.cos(angle) * trunk_radius * 0.45, 0.02, math.sin(angle) * trunk_radius * 0.45))
        end = v_add(base, (math.cos(angle) * length, _rand(rng, -0.01, 0.05), math.sin(angle) * length))
        scene.add_frustum_between(start, end, trunk_radius * _rand(rng, 0.20, 0.33), trunk_radius * 0.045, material, segments=7, cap_ends=True)


def _add_loc_vung_tree(
    scene: SceneMesh,
    x: float,
    z: float,
    ground_y: float,
    scale: float,
    materials: TreeMaterials,
    *,
    rng: random.Random,
    lean_to_lake: float = 0.0,
) -> None:
    trunk_h = _rand(rng, 1.15, 1.72) * scale
    trunk_r = _rand(rng, 0.075, 0.13) * scale
    base = (x, ground_y, z)
    lean_x = _rand(rng, -0.16, 0.16) * scale
    lean_z = (-0.10 + lean_to_lake) * scale + _rand(rng, -0.06, 0.08) * scale
    trunk_top = (x + lean_x, ground_y + trunk_h, z + lean_z)

    _add_curved_frustum(scene, base, trunk_top, trunk_r, trunk_r * 0.45, materials.bark, rng=rng, bend=0.09 * scale, steps=6, segments=14)
    _add_surface_roots(scene, base, trunk_r, materials.bark, rng=rng)

    crown_center = (
        trunk_top[0] + _rand(rng, -0.12, 0.12) * scale,
        trunk_top[1] + _rand(rng, 0.42, 0.66) * scale,
        trunk_top[2] + _rand(rng, -0.07, 0.13) * scale,
    )
    crown_radii = (
        _rand(rng, 0.64, 0.94) * scale,
        _rand(rng, 0.58, 0.82) * scale,
        _rand(rng, 0.50, 0.74) * scale,
    )

    # Cành chính vươn ra trước khi gặp các cụm lá.
    branch_count = rng.randint(7, 10)
    for b in range(branch_count):
        angle = math.tau * b / branch_count + _rand(rng, -0.36, 0.36)
        start_t = _rand(rng, 0.58, 0.92)
        start = v_lerp(base, trunk_top, start_t)
        length = _rand(rng, 0.45, 0.86) * scale
        end = (
            start[0] + math.cos(angle) * length,
            start[1] + _rand(rng, 0.22, 0.58) * scale,
            start[2] + math.sin(angle) * length * _rand(rng, 0.72, 1.05),
        )
        _add_curved_frustum(
            scene,
            start,
            end,
            trunk_r * _rand(rng, 0.22, 0.34),
            trunk_r * _rand(rng, 0.050, 0.10),
            materials.branch,
            rng=rng,
            bend=0.11 * scale,
            steps=3,
            segments=10,
        )
        # Thêm vài cành con mảnh như ảnh cây ven hồ: thân/cành chia tán không đều.
        for _twig in range(rng.randint(1, 3)):
            twig_angle = angle + rng.choice([-1.0, 1.0]) * _rand(rng, 0.35, 0.92)
            twig_len = _rand(rng, 0.18, 0.38) * scale
            twig_end = (
                end[0] + math.cos(twig_angle) * twig_len,
                end[1] + _rand(rng, -0.03, 0.18) * scale,
                end[2] + math.sin(twig_angle) * twig_len,
            )
            scene.add_frustum_between(end, twig_end, trunk_r * _rand(rng, 0.030, 0.055), trunk_r * 0.014, materials.branch, segments=7, cap_ends=True)

    # Nhiều cụm tán chồng lên nhau tạo silhouette tự nhiên, không còn hộp vuông.
    _add_irregular_ellipsoid(scene, crown_center, crown_radii, materials.foliage_deep, rng=rng, segments=28, rings=13, wobble=0.15)

    puff_count = rng.randint(10, 14)
    for i in range(puff_count):
        angle = math.tau * i / puff_count + _rand(rng, -0.42, 0.42)
        lateral = _rand(rng, 0.36, 0.86)
        offset = (
            math.cos(angle) * crown_radii[0] * lateral,
            _rand(rng, -0.22, 0.35) * crown_radii[1],
            math.sin(angle) * crown_radii[2] * lateral,
        )
        p_center = v_add(crown_center, offset)
        p_radii = (
            crown_radii[0] * _rand(rng, 0.36, 0.62),
            crown_radii[1] * _rand(rng, 0.36, 0.64),
            crown_radii[2] * _rand(rng, 0.36, 0.66),
        )
        if offset[1] < -0.05:
            mat = materials.foliage_dark
        elif rng.random() < 0.34:
            mat = materials.foliage_sunlit
        else:
            mat = materials.foliage_deep
        _add_irregular_ellipsoid(scene, p_center, p_radii, mat, rng=rng, segments=20, rings=9, wobble=0.17, squash_bottom=0.23)
        if rng.random() < 0.82:
            _add_leaf_sparkle_layer(scene, p_center, p_radii, materials, rng=rng, count=rng.randint(6, 11), warm_ratio=0.045)

    _add_leaf_sparkle_layer(scene, crown_center, crown_radii, materials, rng=rng, count=rng.randint(85, 125), warm_ratio=0.055)
    _add_leaf_cluster_sprays(scene, crown_center, crown_radii, materials, rng=rng, count=rng.randint(36, 58))
    _add_hanging_leaf_curtains(scene, crown_center, crown_radii, materials, rng=rng, count=rng.randint(6, 10))


def _add_organic_shrub(
    scene: SceneMesh,
    center: Vec3,
    size: Vec3,
    materials: TreeMaterials,
    *,
    rng: random.Random,
    clumps: int = 5,
) -> None:
    for i in range(clumps):
        offset = (
            _rand(rng, -0.42, 0.42) * size[0],
            _rand(rng, -0.10, 0.18) * size[1],
            _rand(rng, -0.28, 0.28) * size[2],
        )
        c = v_add(center, offset)
        radii = (
            size[0] * _rand(rng, 0.34, 0.64),
            size[1] * _rand(rng, 0.36, 0.65),
            size[2] * _rand(rng, 0.42, 0.72),
        )
        mat = materials.foliage_dark if i == 0 or rng.random() < 0.34 else materials.foliage_deep
        _add_irregular_ellipsoid(scene, c, radii, mat, rng=rng, segments=20, rings=9, wobble=0.17, squash_bottom=0.28)
    for _ in range(rng.randint(26, 42)):
        p = _random_point_on_canopy(center, (size[0] * 0.72, size[1] * 0.70, size[2] * 0.78), rng, lower=-0.35)
        mat = materials.foliage_sunlit if rng.random() < 0.75 else materials.foliage_warm
        _add_leaf_diamond(scene, p, mat, rng=rng, width=_rand(rng, 0.07, 0.14), height=_rand(rng, 0.09, 0.18))


def _add_background_haze_tree(
    scene: SceneMesh,
    x: float,
    z: float,
    ground_y: float,
    scale: float,
    materials: TreeMaterials,
    *,
    rng: random.Random,
) -> None:
    base = (x, ground_y, z)
    top = (x + _rand(rng, -0.08, 0.08) * scale, ground_y + _rand(rng, 0.68, 1.05) * scale, z)
    scene.add_frustum_between(base, top, 0.035 * scale, 0.018 * scale, materials.branch, segments=7, cap_ends=True)
    center = (top[0], top[1] + 0.30 * scale, top[2])
    _add_irregular_ellipsoid(
        scene,
        center,
        (_rand(rng, 0.48, 0.72) * scale, _rand(rng, 0.28, 0.46) * scale, _rand(rng, 0.22, 0.36) * scale),
        materials.foliage_haze,
        rng=rng,
        segments=18,
        rings=8,
        wobble=0.13,
        squash_bottom=0.25,
    )



def _add_lakeside_infill_tree(
    scene: SceneMesh,
    x: float,
    z: float,
    ground_y: float,
    scale: float,
    materials: TreeMaterials,
    *,
    rng: random.Random,
) -> None:
    """Cây xen kẽ nhỏ hơn để hàng cây dày mà không quá nặng polygon."""
    trunk_h = _rand(rng, 0.84, 1.18) * scale
    trunk_r = _rand(rng, 0.040, 0.070) * scale
    base = (x, ground_y, z)
    top = (x + _rand(rng, -0.10, 0.10) * scale, ground_y + trunk_h, z + _rand(rng, -0.08, 0.05) * scale)
    _add_curved_frustum(scene, base, top, trunk_r, trunk_r * 0.45, materials.bark, rng=rng, bend=0.07 * scale, steps=5, segments=12)

    crown_center = (top[0] + _rand(rng, -0.06, 0.06) * scale, top[1] + _rand(rng, 0.28, 0.42) * scale, top[2])
    crown_radii = (
        _rand(rng, 0.40, 0.58) * scale,
        _rand(rng, 0.34, 0.50) * scale,
        _rand(rng, 0.34, 0.52) * scale,
    )

    branch_count = rng.randint(4, 7)
    for b in range(branch_count):
        angle = math.tau * b / branch_count + _rand(rng, -0.45, 0.45)
        start = v_lerp(base, top, _rand(rng, 0.62, 0.92))
        end = (
            start[0] + math.cos(angle) * _rand(rng, 0.20, 0.46) * scale,
            start[1] + _rand(rng, 0.08, 0.25) * scale,
            start[2] + math.sin(angle) * _rand(rng, 0.18, 0.40) * scale,
        )
        _add_curved_frustum(scene, start, end, trunk_r * _rand(rng, 0.20, 0.32), trunk_r * 0.060, materials.branch, rng=rng, bend=0.07 * scale, steps=3, segments=9)

    _add_irregular_ellipsoid(scene, crown_center, crown_radii, materials.foliage_deep, rng=rng, segments=16, rings=7, wobble=0.17, squash_bottom=0.25)
    puff_count = rng.randint(4, 7)
    for i in range(puff_count):
        angle = math.tau * i / puff_count + _rand(rng, -0.35, 0.35)
        offset = (
            math.cos(angle) * crown_radii[0] * _rand(rng, 0.30, 0.78),
            _rand(rng, -0.20, 0.28) * crown_radii[1],
            math.sin(angle) * crown_radii[2] * _rand(rng, 0.30, 0.78),
        )
        pc = v_add(crown_center, offset)
        pr = (
            crown_radii[0] * _rand(rng, 0.32, 0.52),
            crown_radii[1] * _rand(rng, 0.34, 0.54),
            crown_radii[2] * _rand(rng, 0.32, 0.56),
        )
        mat = materials.foliage_dark if offset[1] < -0.04 else materials.foliage_sunlit if rng.random() < 0.28 else materials.foliage_deep
        _add_irregular_ellipsoid(scene, pc, pr, mat, rng=rng, segments=14, rings=6, wobble=0.18, squash_bottom=0.27)

    _add_leaf_sparkle_layer(scene, crown_center, crown_radii, materials, rng=rng, count=rng.randint(32, 54), warm_ratio=0.045)
    _add_leaf_cluster_sprays(scene, crown_center, crown_radii, materials, rng=rng, count=rng.randint(10, 18))
    if rng.random() < 0.70:
        _add_hanging_leaf_curtains(scene, crown_center, crown_radii, materials, rng=rng, count=rng.randint(1, 3))

def add_hoan_kiem_lakeside_trees(scene: SceneMesh, materials: TreeMaterials, *, seed: int = 42) -> None:
    """Thay hàng cây cũ bằng cụm cây ven Hồ Gươm chi tiết hơn.

    Dáng chính lấy cảm hứng từ cây lộc vừng/banyan ven hồ: thân mảnh hơi cong,
    cành chia tầng, tán tròn nhưng méo tự nhiên, có vài lá vàng-đỏ nhẹ theo mùa.
    """
    rng = random.Random(seed)

    # Hàng cây chính trên bờ xa: thêm cây xen kẽ để hàng cây không còn thưa.
    tree_xs = [-20.4, -17.8, -15.1, -12.5, -9.8, -7.2, -4.5, -1.9, 0.8, 3.5, 6.1, 8.8, 11.4, 14.1, 16.8, 19.5]
    for index, x in enumerate(tree_xs):
        edge_scale = 0.78 if index in {0, len(tree_xs) - 1} else 1.0
        scale = _rand(rng, 0.74, 1.12) * edge_scale
        z = _rand(rng, 16.82, 17.48)
        ground_y = _rand(rng, 0.46, 0.58)
        lean = -0.07 if index % 3 == 0 else (0.04 if index % 4 == 0 else 0.00)
        _add_loc_vung_tree(scene, x + _rand(rng, -0.17, 0.17), z, ground_y, scale, materials, rng=rng, lean_to_lake=lean)

    # Cây nhỏ xen vào các khoảng trống để hàng cây dày hơn nhưng vẫn tự nhiên.
    # Dùng generator nhẹ hơn cây chính để thêm mật độ mà không làm file quá nặng.
    for x in [-18.7, -15.9, -13.2, -10.5, -7.8, -5.1, -2.4, 0.4, 3.2, 6.0, 8.8, 11.6, 14.4, 17.2, 19.2]:
        _add_lakeside_infill_tree(
            scene,
            x + _rand(rng, -0.18, 0.18),
            _rand(rng, 16.42, 16.96),
            _rand(rng, 0.43, 0.55),
            _rand(rng, 0.52, 0.72),
            materials,
            rng=rng,
        )

    # Một vài cây nền phía sau làm đường chân trời mềm hơn.
    for x in [-21.0, -17.2, -13.4, -9.8, -6.1, -2.3, 1.6, 5.4, 9.0, 12.7, 16.4, 20.3]:
        _add_background_haze_tree(
            scene,
            x + _rand(rng, -0.35, 0.35),
            _rand(rng, 17.95, 18.25),
            _rand(rng, 0.20, 0.36),
            _rand(rng, 0.76, 1.18),
            materials,
            rng=rng,
        )

    # Hàng bụi thấp thay cho các khối hộp xanh ở mép kè.
    shrub_specs = [
        (-19.8, 0.66), (-16.8, 0.76), (-13.8, 0.72), (-10.8, 0.74),
        (-7.8, 0.66), (-4.8, 0.70), (-1.8, 0.68), (1.3, 0.66),
        (4.4, 0.70), (7.6, 0.80), (10.7, 0.72), (13.8, 0.74),
        (16.9, 0.70), (19.8, 0.66),
    ]
    for x, width in shrub_specs:
        center = (x + _rand(rng, -0.18, 0.18), _rand(rng, 0.63, 0.73), _rand(rng, 16.82, 17.12))
        size = (width, _rand(rng, 0.32, 0.48), _rand(rng, 0.30, 0.46))
        _add_organic_shrub(scene, center, size, materials, rng=rng, clumps=rng.randint(6, 9))


__all__ = ["TreeMaterials", "add_hoan_kiem_lakeside_trees"]
