from __future__ import annotations

import math
from pathlib import Path
from random import Random

from glb_forge.scene import SceneMesh, Vec3, v_add, v_cross, v_dot, v_len, v_lerp, v_mul, v_norm, v_sub
from glb_forge.trees import (
    TreeMaterials,
    _add_hanging_leaf_curtains,
    _add_irregular_ellipsoid,
    _add_lakeside_infill_tree,
    _add_leaf_diamond,
    _add_loc_vung_tree,
    _add_organic_shrub,
)

# Scene này dùng Y-up:
# x = trái/phải, y = cao/thấp, z = trước/sau.
# Phía trước nhà nằm ở z âm, nền cảnh quan/núi nằm ở z dương.


TexturePair = tuple[str | None, str | None]
MaterialMap = dict[str, int | list[int] | TreeMaterials]

TEXTURE_ROOT = Path(__file__).resolve().parents[3] / "assets" / "textures" / "nha_co_trang_an"


def _texture_path(filename: str | None) -> str | None:
    if filename is None:
        return None
    return str(TEXTURE_ROOT / filename)


def create_trang_an_house(seed: int = 42) -> SceneMesh:
    """Tạo scene nhà cổ Ninh Bình/Tràng An dạng procedural.

    Model cố ý dùng hình học đơn giản + nhiều chi tiết nhỏ thay cho texture ảnh:
    - nhà 1 tầng, bố cục ngang 5 gian
    - mái ngói đỏ nâu có nhiều viên ngói riêng
    - hiên rộng, cột gỗ, nền đá, bậc tam cấp
    - cửa bức bàn gỗ nhiều cánh
    - sân gạch đỏ, chum nước, cau, cây xanh, tường đá thấp
    - núi đá vôi và cây xanh phía sau để gợi Tràng An
    """
    rng = Random(seed)
    scene = SceneMesh("Trang_An_Heritage_House")
    mat = _make_materials(scene)

    _add_ground_and_courtyard(scene, mat, rng)
    _add_low_walls_and_fence(scene, mat, rng)
    _add_house_base(scene, mat, rng)
    _add_house_body_and_doors(scene, mat, rng)
    _add_roof(scene, mat, rng)
    _add_columns_and_wood_frame(scene, mat, rng)
    _add_jars_and_garden(scene, mat, rng)
    _add_side_gardens(scene, mat, rng)
    _add_background_karst(scene, mat, rng)

    return scene


def _make_materials(scene: SceneMesh) -> MaterialMap:
    """Tạo material theo barem file 1: mỗi vật liệu chính có baseColor + normal texture.

    Texture dùng ảnh procedural tự sinh trong assets/textures/nha_co_trang_an/.
    Không nhúng ảnh báo/ảnh web để tránh vấn đề bản quyền; màu và loại vật liệu được
    chọn theo tư liệu về nhà cổ Tràng An: gỗ lim, mái ngói vảy, nền/cột đá, sân gạch
    đỏ, rêu và cảnh quan núi đá vôi.
    """
    materials: MaterialMap = {}

    earth_tex = _texture_path("warm_earth_basecolor.png")
    earth_nrm = _texture_path("warm_earth_normal.png")
    wood_tex = _texture_path("old_lim_wood_basecolor.png")
    wood_nrm = _texture_path("old_lim_wood_normal.png")
    stone_tex = _texture_path("limestone_wall_basecolor.png")
    stone_nrm = _texture_path("limestone_wall_normal.png")
    roof_tex = _texture_path("fishscale_roof_tile_basecolor.png")
    roof_nrm = _texture_path("fishscale_roof_tile_normal.png")
    brick_tex = _texture_path("courtyard_brick_basecolor.png")
    brick_nrm = _texture_path("courtyard_brick_normal.png")
    mortar_tex = _texture_path("dark_mortar_basecolor.png")
    mortar_nrm = _texture_path("dark_mortar_normal.png")
    moss_tex = _texture_path("moss_basecolor.png")
    moss_nrm = _texture_path("moss_normal.png")
    leaf_tex = _texture_path("village_leaf_basecolor.png")
    leaf_nrm = _texture_path("village_leaf_normal.png")
    bamboo_tex = _texture_path("bamboo_basecolor.png")
    bamboo_nrm = _texture_path("bamboo_normal.png")
    bamboo_fence_tex = _texture_path("bamboo_fence_basecolor.png")
    bamboo_fence_nrm = _texture_path("bamboo_fence_normal.png")
    jar_tex = _texture_path("ceramic_jar_basecolor.png")
    jar_nrm = _texture_path("ceramic_jar_normal.png")
    underside_tex = _texture_path("display_underside_basecolor.png")
    underside_nrm = _texture_path("display_underside_normal.png")

    materials["earth"] = scene.add_material(
        "warm earth base",
        (0.55, 0.46, 0.36, 1.0),
        roughness=0.96,
        base_color_texture=earth_tex,
        normal_texture=earth_nrm,
        normal_scale=0.42,
    )
    materials["shadow"] = scene.add_material("dark interior shadow", (0.015, 0.012, 0.009, 1.0), roughness=1.0)
    materials["plinth_bottom"] = scene.add_material(
        "warm brown orange compact earth underside",
        (0.96, 0.82, 0.62, 1.0),
        roughness=0.96,
        base_color_texture=underside_tex,
        normal_texture=underside_nrm,
        normal_scale=0.34,
    )

    materials["wood_dark"] = scene.add_material(
        "old dark lim wood",
        (0.48, 0.36, 0.27, 1.0),
        roughness=0.88,
        base_color_texture=wood_tex,
        normal_texture=wood_nrm,
        normal_scale=0.72,
    )
    materials["wood"] = scene.add_material(
        "aged brown wood",
        (0.72, 0.55, 0.42, 1.0),
        roughness=0.84,
        base_color_texture=wood_tex,
        normal_texture=wood_nrm,
        normal_scale=0.66,
    )
    materials["wood_light"] = scene.add_material(
        "worn golden wood edge",
        (0.93, 0.72, 0.50, 1.0),
        roughness=0.80,
        base_color_texture=wood_tex,
        normal_texture=wood_nrm,
        normal_scale=0.50,
    )
    materials["wood_black"] = scene.add_material(
        "nearly black carved wood",
        (0.26, 0.20, 0.16, 1.0),
        roughness=0.92,
        base_color_texture=wood_tex,
        normal_texture=wood_nrm,
        normal_scale=0.80,
    )

    materials["stone"] = scene.add_material(
        "old grey limestone",
        (0.66, 0.64, 0.58, 1.0),
        roughness=0.94,
        base_color_texture=stone_tex,
        normal_texture=stone_nrm,
        normal_scale=0.65,
    )
    materials["stone_dark"] = scene.add_material(
        "dark stone gaps",
        (0.36, 0.36, 0.32, 1.0),
        roughness=0.98,
        base_color_texture=stone_tex,
        normal_texture=stone_nrm,
        normal_scale=0.82,
    )
    materials["stone_light"] = scene.add_material(
        "light worn stone edge",
        (0.88, 0.85, 0.76, 1.0),
        roughness=0.90,
        base_color_texture=stone_tex,
        normal_texture=stone_nrm,
        normal_scale=0.46,
    )

    materials["moss"] = scene.add_material(
        "soft green moss",
        (0.72, 0.90, 0.62, 1.0),
        roughness=0.98,
        base_color_texture=moss_tex,
        normal_texture=moss_nrm,
        normal_scale=0.55,
    )
    materials["leaf"] = scene.add_material(
        "deep village green leaves",
        (0.42, 0.70, 0.30, 1.0),
        roughness=0.94,
        base_color_texture=leaf_tex,
        normal_texture=leaf_nrm,
        normal_scale=0.46,
    )
    materials["leaf_light"] = scene.add_material(
        "soft young leaf highlights",
        (0.62, 0.86, 0.38, 1.0),
        roughness=0.92,
        base_color_texture=leaf_tex,
        normal_texture=leaf_nrm,
        normal_scale=0.40,
    )
    materials["leaf_dark"] = scene.add_material(
        "soft shaded village foliage",
        (0.26, 0.46, 0.18, 1.0),
        roughness=0.96,
        base_color_texture=leaf_tex,
        normal_texture=leaf_nrm,
        normal_scale=0.48,
    )
    materials["leaf_sunlit"] = scene.add_material(
        "soft sunlit leaf clusters",
        (0.74, 0.90, 0.44, 1.0),
        roughness=0.91,
        base_color_texture=leaf_tex,
        normal_texture=leaf_nrm,
        normal_scale=0.36,
    )
    materials["bamboo"] = scene.add_material(
        "dry bamboo",
        (0.92, 0.78, 0.48, 1.0),
        roughness=0.90,
        base_color_texture=bamboo_tex,
        normal_texture=bamboo_nrm,
        normal_scale=0.58,
    )
    materials["bamboo_fence"] = scene.add_material(
        "aged darker bamboo fence",
        (0.88, 0.74, 0.42, 1.0),
        roughness=0.92,
        base_color_texture=bamboo_fence_tex,
        normal_texture=bamboo_fence_nrm,
        normal_scale=0.66,
    )
    materials["jar"] = scene.add_material(
        "old countryside brown ceramic water jar",
        (0.58, 0.30, 0.17, 1.0),
        roughness=0.84,
        base_color_texture=jar_tex,
        normal_texture=jar_nrm,
        normal_scale=0.48,
    )
    materials["jar_dark"] = scene.add_material(
        "dark jar mouth and aged raised bands",
        (0.18, 0.11, 0.08, 1.0),
        roughness=0.97,
        base_color_texture=jar_tex,
        normal_texture=jar_nrm,
        normal_scale=0.42,
    )
    materials["jar_water"] = scene.add_material(
        "dark still rain water inside jar",
        (0.07, 0.095, 0.090, 0.82),
        metallic=0.0,
        roughness=0.38,
        double_sided=True,
    )
    materials["base_under"] = scene.add_material(
        "brown orange earth backing without green spots",
        (0.90, 0.74, 0.54, 1.0),
        roughness=0.96,
        base_color_texture=underside_tex,
        normal_texture=underside_nrm,
        normal_scale=0.30,
    )
    materials["base_edge"] = scene.add_material(
        "neat dark display base edge",
        (0.22, 0.15, 0.10, 1.0),
        roughness=0.94,
        base_color_texture=wood_tex,
        normal_texture=wood_nrm,
        normal_scale=0.42,
    )

    materials["roof_base"] = scene.add_material(
        "old red brown roof base slightly muted",
        (0.66, 0.39, 0.29, 1.0),
        roughness=0.92,
        base_color_texture=roof_tex,
        normal_texture=roof_nrm,
        normal_scale=0.64,
    )
    roof_variants: list[int] = []
    # Hệ số tint sáng/tối khác nhau nhưng cùng dùng texture mái ngói vảy.
    roof_tints = [
        (0.76, 0.47, 0.35, 1.0),
        (0.85, 0.52, 0.39, 1.0),
        (0.63, 0.36, 0.28, 1.0),
        (0.91, 0.60, 0.43, 1.0),
        (0.56, 0.32, 0.25, 1.0),
        (0.79, 0.48, 0.35, 1.0),
        (0.72, 0.45, 0.33, 1.0),
        (0.88, 0.61, 0.45, 1.0),
    ]
    for i, color in enumerate(roof_tints):
        roof_variants.append(
            scene.add_material(
                f"individual roof tile {i + 1}",
                color,
                roughness=0.95,
                base_color_texture=roof_tex,
                normal_texture=roof_nrm,
                normal_scale=0.74,
            )
        )
    materials["roof_tiles"] = roof_variants

    brick_variants: list[int] = []
    # Bản v6: sân giữ họ màu từ mái ngói nhưng kéo về cam đất nung,
    # bớt hồng và không đậm đỏ như mái.
    brick_tints = [
        (1.00, 0.96, 0.84, 1.0),
        (0.98, 0.93, 0.80, 1.0),
        (0.94, 0.90, 0.78, 1.0),
        (1.00, 0.98, 0.86, 1.0),
        (0.96, 0.91, 0.76, 1.0),
    ]
    for i, color in enumerate(brick_tints):
        brick_variants.append(
            scene.add_material(
                f"old courtyard brick {i + 1}",
                color,
                roughness=0.97,
                base_color_texture=brick_tex,
                normal_texture=brick_nrm,
                normal_scale=0.52,
            )
        )
    materials["bricks"] = brick_variants
    materials["brick_gap"] = scene.add_material(
        "warm dusty courtyard grout",
        (0.80, 0.70, 0.56, 1.0),
        roughness=1.0,
        # Khe sân vẫn sáng nhưng ấm hơn để hợp nền cam đất.
        normal_texture=mortar_nrm,
        normal_scale=0.18,
    )

    return materials

def _mat(materials: MaterialMap, name: str) -> int:
    value = materials[name]
    if isinstance(value, list):
        raise TypeError(f"Material {name!r} là list, không phải int.")
    return value


def _mat_list(materials: MaterialMap, name: str) -> list[int]:
    value = materials[name]
    if not isinstance(value, list):
        raise TypeError(f"Material {name!r} là int, không phải list.")
    return value


def _roof_axes(y_eave: float, y_ridge: float, start_z: float, ridge_z: float) -> tuple[Vec3, Vec3, Vec3, Vec3, float]:
    """Trả về trục cho một mặt mái.

    Giá trị trả về:
    - u: trục ngang theo chiều dài nhà.
    - v: trục đi từ mép mái lên sống mái, dùng để đặt vị trí hàng ngói.
    - n: normal hướng lên ngoài mặt mái, dùng để đẩy ngói nổi lên khỏi nền mái.
    - tile_v: trục dọc viên ngói, cùng phương với v nhưng được chọn để hệ trục hộp đúng chiều.
    - slope_len: chiều dài dốc mái.

    Với mặt mái sau, nếu lấy trực tiếp v_cross(v, u) thì normal bị hướng xuống dưới,
    làm các viên ngói bị đặt ở mặt dưới roof_base. Vì vậy ép n luôn có thành phần Y dương.
    """
    u = (1.0, 0.0, 0.0)
    v = v_norm((0.0, y_ridge - y_eave, ridge_z - start_z))
    n = v_norm(v_cross(v, u))
    if n[1] < 0.0:
        n = v_mul(n, -1.0)

    # Giữ hệ trục local của hộp ngói đúng chiều để normal/shading ổn hơn.
    tile_v = v_norm(v_cross(u, n))
    slope_len = math.sqrt((y_ridge - y_eave) ** 2 + (ridge_z - start_z) ** 2)
    return u, v, n, tile_v, slope_len



# -----------------------------------------------------------------------------
# Helper cây mềm: lấy tinh thần cây file 1 nhưng thu gọn cho scene Nhà cổ Tràng An
# -----------------------------------------------------------------------------


def _rand(rng: Random, lo: float, hi: float) -> float:
    return rng.uniform(lo, hi)


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
    rng: Random,
    bend: float = 0.08,
    steps: int = 4,
    segments: int = 8,
) -> None:
    """Thân/cành cong nhẹ, tránh cảm giác que thẳng cứng."""
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
        point = v_add(point, v_mul(side_bias, math.sin(math.pi * t)))
        radius = radius_start + (radius_end - radius_start) * t
        scene.add_frustum_between(prev, point, prev_radius, radius, material, segments=segments, cap_ends=i == steps)
        prev = point
        prev_radius = radius


def _push_canopy_vertex(scene: SceneMesh, position: Vec3, center: Vec3, radii: Vec3, uv: tuple[float, float]) -> int:
    """Vertex tán lá có normal theo elip để bề mặt nhìn mềm hơn lathe/quad phẳng."""
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
    rng: Random,
    segments: int = 18,
    rings: int = 8,
    wobble: float = 0.14,
    squash_bottom: float = 0.22,
) -> None:
    """Cụm tán lá elip méo nhẹ, dày và bo mềm thay cho tán tam giác/rời rạc."""
    rx, ry, rz = radii
    if rx <= 0.0 or ry <= 0.0 or rz <= 0.0:
        return
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
    out = scene.indices_by_material[material]

    first = ring_vertices[0]
    for s in range(segments):
        j = (s + 1) % segments
        base = len(scene.positions)
        _push_canopy_vertex(scene, bottom, center, radii, (0.5, 0.0))
        _push_canopy_vertex(scene, first[j], center, radii, (j / segments, 0.12))
        _push_canopy_vertex(scene, first[s], center, radii, (s / segments, 0.12))
        out.extend([base, base + 1, base + 2])

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
            out.extend([base, base + 1, base + 2, base, base + 2, base + 3])

    last = ring_vertices[-1]
    for s in range(segments):
        j = (s + 1) % segments
        base = len(scene.positions)
        _push_canopy_vertex(scene, top, center, radii, (0.5, 1.0))
        _push_canopy_vertex(scene, last[s], center, radii, (s / segments, 0.90))
        _push_canopy_vertex(scene, last[j], center, radii, (j / segments, 0.90))
        out.extend([base, base + 1, base + 2])


def _add_leaf_card(
    scene: SceneMesh,
    center: Vec3,
    material: int,
    *,
    rng: Random,
    width: float,
    height: float,
    tilt: float = 0.18,
) -> None:
    """Lá phụ dạng oval 8 cạnh; mềm hơn tam giác nhọn và vẫn nhẹ file."""
    angle = _rand(rng, 0.0, math.tau)
    right = v_norm((math.cos(angle), _rand(rng, -tilt, tilt), math.sin(angle)))
    up = v_norm((_rand(rng, -tilt, tilt), 1.0, _rand(rng, -tilt, tilt)))
    normal = v_norm(v_cross(right, up))

    base = len(scene.positions)
    scene.positions.append(center)
    scene.normals.append(normal)
    scene.texcoords.append((0.5, 0.5))

    segs = 8
    for i in range(segs):
        theta = math.tau * i / segs
        c = math.cos(theta)
        s = math.sin(theta)
        taper = 0.86 + 0.14 * abs(s)
        p = v_add(center, v_add(v_mul(right, c * width * 0.5 * taper), v_mul(up, s * height * 0.5)))
        scene.positions.append(p)
        scene.normals.append(normal)
        scene.texcoords.append(((c + 1.0) * 0.5, (s + 1.0) * 0.5))

    out = scene.indices_by_material[material]
    for i in range(segs):
        j = 1 + ((i + 1) % segs)
        out.extend((base, base + 1 + i, base + j))


def _random_point_on_canopy(center: Vec3, radii: Vec3, rng: Random, *, lower: float = -0.25) -> Vec3:
    y_frac = _rand(rng, lower, 0.82)
    radial = math.sqrt(max(0.0, 1.0 - y_frac * y_frac))
    angle = _rand(rng, 0.0, math.tau)
    edge = _rand(rng, 0.72, 1.05)
    return (
        center[0] + math.cos(angle) * radii[0] * radial * edge,
        center[1] + y_frac * radii[1],
        center[2] + math.sin(angle) * radii[2] * radial * edge,
    )


def _add_canopy_sparkles(
    scene: SceneMesh,
    center: Vec3,
    radii: Vec3,
    leaf: int,
    leaf_light: int,
    *,
    rng: Random,
    count: int,
) -> None:
    for _ in range(count):
        p = _random_point_on_canopy(center, radii, rng, lower=-0.34)
        mat = leaf_light if rng.random() < 0.58 else leaf
        size = _rand(rng, 0.045, 0.105) * (1.0 + radii[1] * 0.16)
        _add_leaf_card(scene, p, mat, rng=rng, width=size * _rand(rng, 0.82, 1.18), height=size * _rand(rng, 1.05, 1.50), tilt=0.26)


def _add_moss_blob(scene: SceneMesh, center: Vec3, radii: Vec3, moss: int, rng: Random) -> None:
    """Mảng rêu mềm dạng oval thấp, thay các hộp vuông xanh trên đá/nền/lu."""
    _add_irregular_ellipsoid(
        scene,
        center,
        radii,
        moss,
        rng=rng,
        segments=10,
        rings=5,
        wobble=0.20,
        squash_bottom=0.42,
    )

# -----------------------------------------------------------------------------
# Nền, sân gạch, tường, hàng rào
# -----------------------------------------------------------------------------


def _add_ground_and_courtyard(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    earth = _mat(mat, "earth")
    brick_gap = _mat(mat, "brick_gap")
    bricks = _mat_list(mat, "bricks")
    plinth = _mat(mat, "plinth_bottom")
    wood_dark = _mat(mat, "wood_dark")

    # Đế lớn được tách thành plinth đá + lớp đất mỏng phía trên.
    # Bản trước dùng một hộp đất nâu nên khi soi mặt đáy thấy một mảng nâu quá phẳng.
    # Lớp plinth đá tối bên dưới giúp đáy cân mắt hơn, còn mặt trên vẫn giữ nền đất/sân cũ.
    scene.add_box((0.0, -0.23, -2.05), (18.9, 0.30, 12.05), _mat(mat, "base_under"))
    scene.add_box((0.0, -0.055, -2.05), (18.45, 0.10, 11.55), earth)
    scene.add_box((0.0, -0.395, -2.05), (18.25, 0.055, 11.35), _mat(mat, "plinth_bottom"))
    # Viền mỏng dưới đáy và các thanh ngang tạo cảm giác như sa bàn có khung, không còn phẳng trống.
    scene.add_box((0.0, -0.365, -7.86), (18.55, 0.09, 0.22), _mat(mat, "wood_dark"))
    scene.add_box((0.0, -0.365, 3.76), (18.55, 0.09, 0.22), _mat(mat, "wood_dark"))
    scene.add_box((-9.18, -0.365, -2.05), (0.22, 0.09, 11.55), _mat(mat, "wood_dark"))
    scene.add_box((9.18, -0.365, -2.05), (0.22, 0.09, 11.55), _mat(mat, "wood_dark"))
    for x in (-5.8, 0.0, 5.8):
        scene.add_box((x, -0.43, -2.05), (0.10, 0.035, 10.60), _mat(mat, "plinth_bottom"))

    # Tấm cap thấp nhất che mặt đáy bằng texture xám sạch: không còn chấm xanh/rêu ở mặt dưới.
    scene.add_box((0.0, -0.438, -2.05), (18.95, 0.040, 12.05), plinth)

    # Mặt đáy được phủ thêm tấm đế xám cũ + gân đối xứng để nhìn cân mắt khi soi từ dưới.
    y_bottom = -0.265
    scene.add_quad(
        (-9.30, y_bottom, -7.95),
        (-9.30, y_bottom, 3.85),
        (9.30, y_bottom, 3.85),
        (9.30, y_bottom, -7.95),
        plinth,
        normal=(0.0, -1.0, 0.0),
    )
    # Viền ngoài + các thanh đỡ ngang dọc tạo đáy dạng sa bàn thay vì một mảng texture lớn.
    scene.add_box((0.0, y_bottom - 0.025, -7.95), (18.75, 0.10, 0.16), wood_dark)
    scene.add_box((0.0, y_bottom - 0.025, 3.85), (18.75, 0.10, 0.16), wood_dark)
    scene.add_box((-9.30, y_bottom - 0.025, -2.05), (0.16, 0.10, 11.85), wood_dark)
    scene.add_box((9.30, y_bottom - 0.025, -2.05), (0.16, 0.10, 11.85), wood_dark)
    for x in (-6.10, -3.05, 0.0, 3.05, 6.10):
        scene.add_box((x, y_bottom - 0.045, -2.05), (0.09, 0.12, 11.55), plinth)
    for z in (-6.70, -4.60, -2.50, -0.40, 1.70):
        scene.add_box((0.0, y_bottom - 0.050, z), (18.15, 0.11, 0.09), plinth)

    # Lớp vữa tối nằm dưới những viên gạch.
    # Bản v2 bị hở nửa viên ở hai mép do hàng gạch so le bị skip ở cạnh.
    # Ở đây lát theo kiểu clip từng viên ở biên, nên hai bên được lấp đầy bằng nửa viên gạch.
    scene.add_box((0.0, 0.015, -4.95), (17.95, 0.05, 5.55), brick_gap)

    x_min, x_max = -8.95, 8.95
    z_min, z_max = -7.45, -2.55
    brick_w = 0.62
    brick_d = 0.34
    gap = 0.035
    y = 0.065

    row = 0
    z = z_min + brick_d / 2.0
    while z < z_max:
        offset = 0.0 if row % 2 == 0 else brick_w * 0.5
        x0 = x_min - offset
        col = 0
        while x0 < x_max:
            x1 = x0 + brick_w
            bx0 = max(x0 + gap * 0.50, x_min + gap * 0.50)
            bx1 = min(x1 - gap * 0.50, x_max - gap * 0.50)
            visible_w = bx1 - bx0
            if visible_w > 0.10:
                cx = (bx0 + bx1) * 0.5
                color_mat = bricks[(row * 3 + col + rng.randrange(len(bricks))) % len(bricks)]
                h = 0.035 + rng.random() * 0.012
                scene.add_box((cx, y + h * 0.5, z), (visible_w, h, brick_d - gap), color_mat)
            x0 += brick_w
            col += 1
        z += brick_d
        row += 1

    # Viền sân thấp màu đất/đá.
    scene.add_box((0.0, 0.12, -7.80), (18.6, 0.28, 0.28), earth)
    scene.add_box((-9.18, 0.12, -2.05), (0.28, 0.28, 11.5), earth)
    scene.add_box((9.18, 0.12, -2.05), (0.28, 0.28, 11.5), earth)


def _add_low_walls_and_fence(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    stone = _mat(mat, "stone")
    stone_dark = _mat(mat, "stone_dark")
    stone_light = _mat(mat, "stone_light")
    bamboo = _mat(mat, "bamboo_fence")
    moss = _mat(mat, "moss")

    # Tường đá thấp hai bên và phía sau.
    wall_specs = [
        ((-8.55, 0.62, 0.55), (0.38, 1.24, 6.9)),
        ((8.55, 0.62, 0.55), (0.38, 1.24, 6.9)),
        ((0.0, 0.70, 3.90), (17.4, 1.40, 0.38)),
    ]
    for center, size in wall_specs:
        scene.add_box(center, size, stone)

    # Trụ tường ở các góc, nhìn giống cột đá làng quê.
    for x in (-8.55, 8.55):
        for z in (-2.75, 3.90):
            scene.add_box((x, 0.78, z), (0.62, 1.55, 0.62), stone)
            scene.add_box((x, 1.60, z), (0.78, 0.18, 0.78), stone_light)
            scene.add_box((x, 0.08, z), (0.78, 0.16, 0.78), stone_dark)

    # Vẽ mạch đá bằng các thanh tối rất mỏng trên mặt tường.
    for x in (-8.77, 8.77):
        for zi in range(12):
            z = -2.45 + zi * 0.55
            scene.add_box((x, 0.62, z), (0.035, 0.025, 0.42), stone_dark)
        for yi in range(4):
            y = 0.25 + yi * 0.28
            scene.add_box((x, y, 0.55), (0.035, 0.025, 6.55), stone_dark)

    for xi in range(28):
        x = -8.0 + xi * 0.60
        if abs(x) < 6.8:
            scene.add_box((x, 0.68, 3.68), (0.45, 0.025, 0.035), stone_dark)
    for yi in range(4):
        scene.add_box((0.0, 0.25 + yi * 0.30, 3.68), (16.4, 0.025, 0.035), stone_dark)

    # Rêu giữ lại nhẹ trên tường đá; phần cây/bụi hai hông được dựng riêng phía dưới.
    for _ in range(18):
        side = rng.choice([-1.0, 1.0])
        x = side * 8.78
        y = rng.uniform(0.22, 0.90)
        z = rng.uniform(-2.1, 3.0)
        _add_moss_blob(
            scene,
            (x, y, z),
            (0.024, rng.uniform(0.045, 0.105), rng.uniform(0.09, 0.20)),
            moss,
            rng,
        )

    # Hàng rào tre thấp phía trước, chừa khoảng giữa cho bậc tam cấp.
    _add_bamboo_fence(scene, bamboo, x0=-8.05, x1=-2.05, z=-6.62)
    _add_bamboo_fence(scene, bamboo, x0=2.05, x1=8.05, z=-6.62)
    _add_bamboo_fence(scene, bamboo, x0=-8.15, x1=-5.4, z=-3.10)
    _add_bamboo_fence(scene, bamboo, x0=5.4, x1=8.15, z=-3.10)


def _add_bamboo_fence(scene: SceneMesh, bamboo: int, *, x0: float, x1: float, z: float) -> None:
    step = 0.72
    x = x0
    posts: list[float] = []
    while x <= x1 + 1e-6:
        posts.append(x)
        scene.add_frustum_between((x, 0.12, z), (x, 0.88, z), 0.035, 0.028, bamboo, segments=8)
        x += step

    for y in (0.42, 0.70):
        scene.add_box_between((x0, y, z), (x1, y, z), 0.045, bamboo, width=0.055)

    # Thanh chéo vài đoạn cho cảm giác thủ công.
    for i in range(0, max(0, len(posts) - 1), 2):
        scene.add_box_between((posts[i], 0.18, z + 0.02), (posts[i + 1], 0.78, z + 0.02), 0.035, bamboo, width=0.045)


# -----------------------------------------------------------------------------
# Nhà chính: nền đá, thân nhà, cửa, mái, cột
# -----------------------------------------------------------------------------


def _add_house_base(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    stone = _mat(mat, "stone")
    stone_dark = _mat(mat, "stone_dark")
    stone_light = _mat(mat, "stone_light")
    moss = _mat(mat, "moss")

    # Nền nhà cao bằng đá tảng.
    scene.add_box((0.0, 0.30, -0.10), (13.75, 0.60, 4.65), stone)
    scene.add_box((0.0, 0.64, -1.50), (13.55, 0.12, 1.45), stone_light)

    # Mặt trước nền đá: các khối đá riêng để nhìn cổ hơn.
    x_min, x_max = -6.75, 6.75
    z_front = -2.43
    rows = 3
    cols = 25
    for r in range(rows):
        for c in range(cols):
            w = (x_max - x_min) / cols
            x = x_min + w * (c + 0.5)
            y = 0.14 + r * 0.18
            h = 0.14
            block_mat = stone if (r + c + rng.randrange(3)) % 3 else stone_light
            scene.add_box((x, y, z_front - 0.025), (w - 0.035, h, 0.06), block_mat)

    # Mạch ngang/dọc tối.
    for r in range(rows + 1):
        y = 0.055 + r * 0.18
        scene.add_box((0.0, y, z_front - 0.065), (13.35, 0.018, 0.035), stone_dark)
    for c in range(cols + 1):
        x = x_min + (x_max - x_min) * c / cols
        scene.add_box((x, 0.32, z_front - 0.07), (0.018, 0.48, 0.035), stone_dark)

    # Bậc tam cấp bằng đá.
    scene.add_box((0.0, 0.11, -3.42), (3.35, 0.22, 0.72), stone)
    scene.add_box((0.0, 0.27, -3.10), (2.85, 0.22, 0.62), stone_light)
    scene.add_box((0.0, 0.43, -2.80), (2.35, 0.22, 0.52), stone)
    for i, z in enumerate((-3.42, -3.10, -2.80)):
        scene.add_box((0.0, 0.23 + i * 0.16, z - 0.36), (3.15 - i * 0.45, 0.035, 0.045), stone_dark)

    # Rêu xanh nhẹ ở mép bậc và chân nền.
    for _ in range(28):
        x = rng.uniform(-6.2, 6.2)
        y = rng.uniform(0.47, 0.68)
        z = rng.choice([-2.47, -1.95]) + rng.uniform(-0.015, 0.015)
        _add_moss_blob(scene, (x, y, z), (rng.uniform(0.07, 0.18), 0.020, 0.030), moss, rng)


def _add_house_body_and_doors(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    wood = _mat(mat, "wood")
    wood_dark = _mat(mat, "wood_dark")
    wood_light = _mat(mat, "wood_light")
    wood_black = _mat(mat, "wood_black")
    shadow = _mat(mat, "shadow")

    # Thân nhà gỗ thấp, dài ngang.
    scene.add_box((0.0, 1.42, 0.10), (12.55, 1.65, 3.25), wood_dark)
    scene.add_box((0.0, 1.50, 1.69), (12.55, 1.80, 0.20), wood)
    scene.add_box((-6.38, 1.42, 0.05), (0.22, 1.75, 3.35), wood)
    scene.add_box((6.38, 1.42, 0.05), (0.22, 1.75, 3.35), wood)

    # Vách bên dạng ván ngang.
    for side_x in (-6.52, 6.52):
        for i in range(8):
            y = 0.78 + i * 0.19
            scene.add_box((side_x, y, 0.12), (0.05, 0.035, 3.05), wood_light if i % 3 == 0 else wood_dark)

    # Dải xà ngang mặt trước.
    scene.add_box((0.0, 2.40, -1.72), (12.75, 0.22, 0.18), wood_black)
    scene.add_box((0.0, 0.78, -1.73), (12.75, 0.18, 0.18), wood_black)
    scene.add_box((0.0, 2.16, -1.74), (12.40, 0.10, 0.14), wood_light)

    # 5 gian cửa bức bàn, nhiều cánh.
    # Bản v7: khép đều các ô cánh giữa ở những gian đang bị trống đen
    # để mặt tiền nhìn cân và liền mạch hơn; các phần còn lại giữ nguyên.
    bay_centers = [-4.95, -2.48, 0.0, 2.48, 4.95]
    for bay_i, cx in enumerate(bay_centers):
        open_middle = False
        _add_door_bay(
            scene,
            cx=cx,
            y_base=0.83,
            z=-1.86,
            width=1.78,
            height=1.34,
            open_middle=open_middle,
            wood=wood,
            wood_dark=wood_dark,
            wood_light=wood_light,
            shadow=shadow,
        )

    # Các mảng vách gỗ giữa cửa/cột.
    for x in (-6.00, -3.72, -1.22, 1.22, 3.72, 6.00):
        scene.add_box((x, 1.48, -1.83), (0.18, 1.32, 0.08), wood_black)
        scene.add_box((x, 2.05, -1.87), (0.32, 0.16, 0.10), wood_light)
        # Ô trang trí nhỏ phía trên như chạm khắc đơn giản.
        scene.add_box((x, 2.31, -1.90), (0.28, 0.24, 0.08), wood)
        scene.add_box((x, 2.31, -1.955), (0.18, 0.14, 0.03), wood_dark)

    # Vì kèo gợi hình ở hai đầu hồi.
    for x in (-6.25, 6.25):
        sign = 1 if x > 0 else -1
        scene.add_box_between((x, 2.00, -1.58), (x, 3.32, -0.02), 0.09, wood_black, width=0.12, up_hint=(sign, 0.0, 0.0))
        scene.add_box_between((x, 2.00, 1.58), (x, 3.32, -0.02), 0.09, wood_black, width=0.12, up_hint=(sign, 0.0, 0.0))
        scene.add_box_between((x, 2.18, -1.20), (x, 2.18, 1.20), 0.075, wood_light, width=0.10, up_hint=(sign, 0.0, 0.0))


def _add_door_bay(
    scene: SceneMesh,
    *,
    cx: float,
    y_base: float,
    z: float,
    width: float,
    height: float,
    open_middle: bool,
    wood: int,
    wood_dark: int,
    wood_light: int,
    shadow: int,
) -> None:
    # Khoảng tối phía sau cửa.
    scene.add_box((cx, y_base + height * 0.50, z - 0.055), (width, height, 0.045), shadow)

    leaves = 4
    leaf_w = width / leaves
    for i in range(leaves):
        # Mở hờ 2 cánh giữa ở một số gian để tạo nhịp tối/sáng tự nhiên.
        if open_middle and i in (1, 2):
            continue
        lx = cx - width / 2.0 + leaf_w * (i + 0.5)
        scene.add_box((lx, y_base + height * 0.50, z), (leaf_w - 0.045, height, 0.055), wood)
        # Khung cánh cửa.
        scene.add_box((lx - leaf_w * 0.39, y_base + height * 0.50, z - 0.04), (0.035, height, 0.035), wood_dark)
        scene.add_box((lx + leaf_w * 0.39, y_base + height * 0.50, z - 0.04), (0.035, height, 0.035), wood_dark)
        scene.add_box((lx, y_base + 0.12, z - 0.045), (leaf_w - 0.09, 0.035, 0.035), wood_dark)
        scene.add_box((lx, y_base + height - 0.12, z - 0.045), (leaf_w - 0.09, 0.035, 0.035), wood_dark)

        # Hai ô pano nổi.
        scene.add_box((lx, y_base + height * 0.35, z - 0.075), (leaf_w - 0.16, height * 0.32, 0.030), wood_light)
        scene.add_box((lx, y_base + height * 0.72, z - 0.075), (leaf_w - 0.16, height * 0.25, 0.030), wood_light)
        scene.add_box((lx, y_base + height * 0.35, z - 0.100), (leaf_w - 0.24, height * 0.22, 0.025), wood_dark)
        scene.add_box((lx, y_base + height * 0.72, z - 0.100), (leaf_w - 0.24, height * 0.15, 0.025), wood_dark)

    # Khung bao cửa.
    scene.add_box((cx, y_base - 0.03, z - 0.02), (width + 0.16, 0.07, 0.08), wood_dark)
    scene.add_box((cx, y_base + height + 0.03, z - 0.02), (width + 0.16, 0.07, 0.08), wood_dark)
    scene.add_box((cx - width / 2.0 - 0.05, y_base + height / 2.0, z - 0.02), (0.07, height + 0.08, 0.08), wood_dark)
    scene.add_box((cx + width / 2.0 + 0.05, y_base + height / 2.0, z - 0.02), (0.07, height + 0.08, 0.08), wood_dark)


def _add_roof(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    roof_base = _mat(mat, "roof_base")
    roof_tiles = _mat_list(mat, "roof_tiles")
    stone = _mat(mat, "stone")
    stone_light = _mat(mat, "stone_light")
    wood_dark = _mat(mat, "wood_dark")
    wood = _mat(mat, "wood")
    width = 14.70
    z_front = -2.82
    z_back = 2.82
    z_ridge = 0.00
    y_eave = 2.55
    y_ridge = 4.02

    # Hai mặt mái chính.
    _add_roof_plane(
        scene,
        start_z=z_front,
        ridge_z=z_ridge,
        y_eave=y_eave,
        y_ridge=y_ridge,
        width=width,
        roof_base=roof_base,
        roof_tiles=roof_tiles,
        rng=rng,
    )
    _add_roof_plane(
        scene,
        start_z=z_back,
        ridge_z=z_ridge,
        y_eave=y_eave,
        y_ridge=y_ridge,
        width=width,
        roof_base=roof_base,
        roof_tiles=roof_tiles,
        rng=rng,
    )

    # Diềm mái trước/sau hơi cong nhẹ ở hai đầu, không tạo cảm giác chùa.
    # Chia làm 3 đoạn: giữa thẳng, hai đầu nâng nhẹ.
    for z in (z_front, z_back):
        scene.add_box_between((-6.45, y_eave - 0.03, z), (6.45, y_eave - 0.03, z), 0.16, stone, width=0.22)
        scene.add_box_between((-7.35, y_eave + 0.13, z), (-6.45, y_eave - 0.03, z), 0.16, stone_light, width=0.22)
        scene.add_box_between((6.45, y_eave - 0.03, z), (7.35, y_eave + 0.13, z), 0.16, stone_light, width=0.22)
        scene.add_box_between((-7.20, y_eave - 0.20, z + (0.08 if z < 0 else -0.08)), (7.20, y_eave - 0.20, z + (0.08 if z < 0 else -0.08)), 0.10, wood_dark, width=0.16)

    # Đỉnh mái và bờ chảy hai đầu hồi.
    scene.add_box_between((-7.20, y_ridge + 0.06, z_ridge), (7.20, y_ridge + 0.06, z_ridge), 0.18, stone_light, width=0.24)
    for x in (-7.32, 7.32):
        scene.add_box_between((x, y_eave + 0.03, z_front), (x, y_ridge + 0.08, z_ridge), 0.16, stone_light, width=0.24, up_hint=(1.0, 0.0, 0.0))
        scene.add_box_between((x, y_ridge + 0.08, z_ridge), (x, y_eave + 0.03, z_back), 0.16, stone_light, width=0.24, up_hint=(1.0, 0.0, 0.0))

    # Mặt hồi tam giác bằng gỗ. Đẩy hồi ra sát mép mái để không còn khe hở ở hai hông.
    for x in (-7.20, 7.20):
        sign = 1.0 if x > 0 else -1.0
        normal = (sign, 0.0, 0.0)
        p0 = (x, y_eave - 0.10, z_front + 0.06)
        p1 = (x, y_eave - 0.10, z_back - 0.06)
        p2 = (x, y_ridge - 0.03, z_ridge)
        if x > 0:
            scene.add_triangle(p0, p1, p2, wood, normal=normal)
        else:
            scene.add_triangle(p1, p0, p2, wood, normal=normal)

        # Nẹp chéo nằm ngay dưới bờ chảy, che tiếp giáp giữa mái và mặt tam giác.
        scene.add_box_between(
            (x + sign * 0.018, y_eave - 0.03, z_front + 0.03),
            (x + sign * 0.018, y_ridge + 0.02, z_ridge),
            0.105,
            wood_dark,
            width=0.16,
            up_hint=(sign, 0.0, 0.0),
        )
        scene.add_box_between(
            (x + sign * 0.018, y_ridge + 0.02, z_ridge),
            (x + sign * 0.018, y_eave - 0.03, z_back - 0.03),
            0.105,
            wood_dark,
            width=0.16,
            up_hint=(sign, 0.0, 0.0),
        )
        scene.add_box_between(
            (x + sign * 0.020, y_eave - 0.12, z_front + 0.06),
            (x + sign * 0.020, y_eave - 0.12, z_back - 0.06),
            0.085,
            wood_dark,
            width=0.12,
            up_hint=(sign, 0.0, 0.0),
        )

        # Ván dọc trên hồi ăn sát theo tam giác mới.
        for i in range(7):
            z = -1.35 + i * 0.45
            y_mid = 2.58 + (1.0 - abs(z) / 1.55) * 0.72
            scene.add_box((x + sign * 0.035, y_mid, z), (0.06, 0.98, 0.035), wood_dark)

    # Tấm bịt đầu hồi ngoài cùng: khép kín khe giữa mái và mặt tam giác hai bên.
    # Đặt sát dưới bờ chảy để khi nhìn ngang không còn cảm giác mái rời khỏi hồi nhà.
    for x in (-7.18, 7.18):
        sign = 1.0 if x > 0 else -1.0
        normal = (sign, 0.0, 0.0)
        q0 = (x, y_eave - 0.045, z_front + 0.035)
        q1 = (x, y_eave - 0.045, z_back - 0.035)
        q2 = (x, y_ridge - 0.020, z_ridge)
        if x > 0:
            scene.add_triangle(q0, q1, q2, wood_dark, normal=normal)
        else:
            scene.add_triangle(q1, q0, q2, wood_dark, normal=normal)
        scene.add_box_between((x, y_eave - 0.03, z_front + 0.06), (x, y_ridge + 0.03, z_ridge), 0.08, wood, width=0.12, up_hint=(sign, 0.0, 0.0))
        scene.add_box_between((x, y_ridge + 0.03, z_ridge), (x, y_eave - 0.03, z_back - 0.06), 0.08, wood, width=0.12, up_hint=(sign, 0.0, 0.0))
        for i in range(5):
            z = -1.08 + i * 0.54
            y_mid = 2.52 + (1.0 - abs(z) / 1.55) * 0.58
            scene.add_box((x + sign * 0.032, y_mid, z), (0.055, 0.72, 0.030), wood)

    # Rui mè dưới mái hiên trước.
    for i in range(27):
        x = -6.6 + i * 0.51
        scene.add_box_between((x, 2.33, -1.70), (x, 2.50, -2.62), 0.055, wood_dark, width=0.070)


def _add_roof_plane(
    scene: SceneMesh,
    *,
    start_z: float,
    ridge_z: float,
    y_eave: float,
    y_ridge: float,
    width: float,
    roof_base: int,
    roof_tiles: list[int],
    rng: Random,
) -> None:
    # Plane từ mép mái lên sống mái.
    half_w = width / 2.0
    p0 = (-half_w, y_eave, start_z)
    p1 = (half_w, y_eave, start_z)
    p2 = (half_w, y_ridge, ridge_z)
    p3 = (-half_w, y_ridge, ridge_z)

    u, v, n, tile_v, slope_len = _roof_axes(y_eave, y_ridge, start_z, ridge_z)
    scene.add_quad(p0, p1, p2, p3, roof_base, normal=n)

    cols = 42
    rows = 14
    tile_w = width / cols * 0.96
    tile_d = slope_len / rows * 0.92
    step_x = width / cols
    step_d = slope_len / rows

    for row in range(rows):
        row_offset = 0.0 if row % 2 == 0 else step_x * 0.5
        dist = step_d * (row + 0.5)
        for col in range(cols):
            x = -half_w + step_x * (col + 0.5) + row_offset
            if x > half_w - step_x * 0.35:
                continue
            # Ngói hơi không đều để nhìn cũ.
            mat_index = roof_tiles[(row * 5 + col + rng.randrange(len(roof_tiles))) % len(roof_tiles)]
            jitter_x = rng.uniform(-0.018, 0.018)
            jitter_d = rng.uniform(-0.014, 0.014)
            center = v_add((x + jitter_x, y_eave, start_z), v_add(v_mul(v, dist + jitter_d), v_mul(n, 0.035)))
            scene.add_box(center, (tile_w * rng.uniform(0.90, 1.02), 0.040, tile_d * rng.uniform(0.82, 1.05)), mat_index, x_axis=u, y_axis=n, z_axis=tile_v)

    # Một số hàng ngói âm/dương nổi nhẹ theo chiều ngang.
    for row in range(1, rows, 3):
        dist = step_d * row
        center = v_add((0.0, y_eave, start_z), v_add(v_mul(v, dist), v_mul(n, 0.060)))
        scene.add_box(center, (width - 0.55, 0.045, 0.045), roof_tiles[row % len(roof_tiles)], x_axis=u, y_axis=n, z_axis=tile_v)


def _add_columns_and_wood_frame(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    wood = _mat(mat, "wood")
    wood_dark = _mat(mat, "wood_dark")
    wood_light = _mat(mat, "wood_light")
    stone = _mat(mat, "stone")
    stone_light = _mat(mat, "stone_light")

    column_xs = [-6.05, -4.55, -3.05, -1.52, 0.0, 1.52, 3.05, 4.55, 6.05]
    for x in column_xs:
        # Chân tảng đá vuông + đế tròn.
        scene.add_box((x, 0.70, -2.05), (0.42, 0.18, 0.42), stone_light)
        scene.add_frustum((x, 0.84, -2.05), 0.17, 0.14, 0.16, stone, segments=16)
        # Cột gỗ hơi thuôn.
        scene.add_frustum((x, 1.56, -2.05), 0.105, 0.085, 1.55, wood, segments=18)
        scene.add_frustum((x, 2.37, -2.05), 0.14, 0.12, 0.16, wood_dark, segments=18)
        scene.add_box((x, 2.52, -2.05), (0.38, 0.16, 0.30), wood_light)

    # Xà ngang trước, xà hiên.
    scene.add_box((0.0, 2.48, -2.05), (12.55, 0.16, 0.18), wood_dark)
    scene.add_box((0.0, 2.25, -2.07), (12.30, 0.10, 0.14), wood_light)
    scene.add_box((0.0, 0.72, -2.04), (12.40, 0.10, 0.12), wood_dark)

    # Thanh xà dọc từ tường ra cột hiên.
    for x in column_xs:
        scene.add_box_between((x, 2.28, -1.72), (x, 2.38, -2.52), 0.065, wood_dark, width=0.085)

    # Một vài chi tiết đầu dư gỗ dưới mái.
    for x in [-5.35, -4.00, -2.68, -1.35, 1.35, 2.68, 4.00, 5.35]:
        scene.add_box((x, 2.18, -2.18), (0.20, 0.22, 0.20), wood_light)
        scene.add_box((x, 2.18, -2.33), (0.13, 0.14, 0.08), wood_dark)


# -----------------------------------------------------------------------------
# Đồ sân vườn: chum nước, cau, bụi cây
# -----------------------------------------------------------------------------


def _add_jars_and_garden(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    jar = _mat(mat, "jar")
    jar_dark = _mat(mat, "jar_dark")
    jar_water = _mat(mat, "jar_water")
    moss = _mat(mat, "moss")
    leaf = _mat(mat, "leaf")
    leaf_light = _mat(mat, "leaf_light")
    bamboo = _mat(mat, "bamboo")

    _add_water_jar(scene, (-7.05, 0.07, -4.55), 0.95, jar, jar_dark, jar_water, moss, bamboo, rng)
    _add_water_jar(scene, (-4.95, 0.07, -4.12), 0.58, jar, jar_dark, jar_water, moss, bamboo, rng)
    _add_water_jar(scene, (5.00, 0.07, -4.35), 0.82, jar, jar_dark, jar_water, moss, bamboo, rng)
    _add_water_jar(scene, (6.25, 0.07, -4.05), 0.54, jar, jar_dark, jar_water, moss, bamboo, rng)

    _add_areca_palm(scene, (-7.65, 0.08, -3.18), height=2.85, trunk=bamboo, leaf=leaf, leaf_light=leaf_light, rng=rng)
    _add_areca_palm(scene, (7.45, 0.08, -2.90), height=3.05, trunk=bamboo, leaf=leaf, leaf_light=leaf_light, rng=rng)

    # Bụi cây quanh chân tường và hai bên hiên.
    for center, scale, count in [
        ((-7.20, 0.16, -2.30), 0.55, 22),
        ((7.15, 0.16, -2.20), 0.55, 22),
        ((-5.05, 0.18, -3.40), 0.36, 14),
        ((5.60, 0.18, -3.35), 0.36, 14),
        ((-6.85, 0.18, 2.90), 0.75, 24),
        ((6.85, 0.18, 2.90), 0.75, 24),
    ]:
        _add_leaf_cluster(scene, center, scale, count, leaf, leaf_light, rng)


def _add_side_gardens(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    """Thêm cây/bụi hai bên hông nhà để mảng tường đá có chiều sâu hơn."""
    leaf = _mat(mat, "leaf")
    leaf_light = _mat(mat, "leaf_light")
    leaf_dark = _mat(mat, "leaf_dark")
    leaf_sunlit = _mat(mat, "leaf_sunlit")
    trunk = _mat(mat, "wood_dark")
    bamboo = _mat(mat, "bamboo")
    moss = _mat(mat, "moss")

    # Bụi cây chạy dọc hai hông, nằm trong khoảng giữa tường đá và thân nhà.
    side_specs = [
        (-1.0, -7.82, -8.78),
        (1.0, 7.82, 8.78),
    ]
    side_zs = [-1.95, -1.20, -0.45, 0.32, 1.10, 1.88, 2.62]
    for side, inside_x, wall_x in side_specs:
        for index, z in enumerate(side_zs):
            x = inside_x + side * rng.uniform(-0.08, 0.12)
            center = (x, 0.39 + rng.uniform(-0.04, 0.09), z + rng.uniform(-0.12, 0.12))
            # Tán hông được tăng scale/count và dùng cụm ellipsoid, không còn mảng lá vuông rời.
            _add_leaf_cluster(
                scene,
                center,
                rng.uniform(0.54, 0.76),
                rng.randint(24, 34),
                leaf_dark if index % 3 == 0 else leaf,
                leaf_sunlit if index % 3 == 1 else leaf_light,
                rng,
            )

            if index % 2 == 0:
                scene.add_frustum_between(
                    (x - side * 0.10, 0.10, z - 0.08),
                    (x - side * 0.06, 0.70 + rng.uniform(-0.06, 0.08), z + 0.08),
                    0.025,
                    0.018,
                    trunk,
                    segments=7,
                )

        # Dây leo có nhánh và cụm tán lá bám tường, thay cho các ô xanh rời rạc.
        for z in [-2.08, -1.38, -0.68, 0.08, 0.82, 1.58, 2.34]:
            _add_wall_climber(
                scene,
                wall_x=wall_x,
                side=side,
                z=z + rng.uniform(-0.08, 0.08),
                base_y=rng.uniform(0.16, 0.28),
                height=rng.uniform(0.92, 1.25),
                lean=rng.uniform(-0.20, 0.20),
                vine=bamboo,
                branch=trunk,
                leaf=leaf_dark if index % 2 == 0 else leaf,
                leaf_light=leaf_sunlit,
                rng=rng,
            )

    # Cây nhỏ ở hai hông sau nhà, tán cao hơn tường để nhìn rõ từ các góc bên.
    side_trees = [
        (-7.72, -0.72, 1.65, 0.45),
        (-7.88, 1.32, 1.95, 0.52),
        (-7.64, 2.72, 1.72, 0.48),
        (7.72, -0.62, 1.70, 0.46),
        (7.88, 1.20, 1.92, 0.52),
        (7.64, 2.58, 1.78, 0.50),
    ]
    for x, z, height, canopy_scale in side_trees:
        _add_background_tree(
            scene,
            base=(x + rng.uniform(-0.08, 0.08), 0.12, z + rng.uniform(-0.10, 0.10)),
            height=height * rng.uniform(0.92, 1.08),
            canopy_scale=canopy_scale * rng.uniform(0.90, 1.12),
            trunk=trunk,
            leaf=leaf_dark if x < 0 else leaf,
            leaf_light=leaf_sunlit,
            rng=rng,
        )

    # Một vài khóm cau thấp ở góc hông trước để nối với sân gạch.
    _add_areca_palm(scene, (-7.72, 0.08, -1.92), height=2.18, trunk=bamboo, leaf=leaf, leaf_light=leaf_light, rng=rng)
    _add_areca_palm(scene, (7.72, 0.08, -1.82), height=2.24, trunk=bamboo, leaf=leaf, leaf_light=leaf_light, rng=rng)

    # Rêu nền dưới bụi cây giúp chân tường bớt trống nhưng không còn thành các chấm riêng lẻ.
    for side, inside_x, _ in side_specs:
        for z in [-1.55, -0.35, 0.85, 2.05, 2.95]:
            _add_moss_blob(scene, (inside_x - side * 0.08, 0.13, z), (0.23, 0.035, 0.13), moss, rng)


def _add_wall_climber(
    scene: SceneMesh,
    *,
    wall_x: float,
    side: float,
    z: float,
    base_y: float,
    height: float,
    lean: float,
    vine: int,
    branch: int,
    leaf: int,
    leaf_light: int,
    rng: Random,
) -> None:
    """Dây leo sát tường có thân, nhánh và tán lá low-poly."""
    inner_x = wall_x - side * 0.055
    top_y = base_y + height

    bottom = (inner_x, base_y, z)
    top = (inner_x, top_y, z + lean)
    scene.add_box_between(bottom, top, 0.016, vine, width=0.022)

    # Nhánh ngang/chéo mọc ra hai phía để khi nhìn ngang tường thấy rõ cành.
    for step in range(4):
        t = (step + 1) / 5.0
        y = base_y + height * t
        stem_z = z + lean * t
        branch_side = -1.0 if step % 2 == 0 else 1.0
        branch_len = rng.uniform(0.22, 0.42)
        start = (inner_x - side * 0.010, y, stem_z)
        end = (
            inner_x - side * rng.uniform(0.05, 0.10),
            y + rng.uniform(0.04, 0.14),
            stem_z + branch_side * branch_len,
        )
        scene.add_box_between(start, end, 0.012, branch, width=0.017)
        _add_leaf_cluster(scene, end, rng.uniform(0.16, 0.27), rng.randint(8, 13), leaf, leaf_light, rng)

        # Vài lá đơn nhỏ nằm dọc nhánh để tán không bị gom thành khối tròn quá đều.
        for leaf_i in range(2):
            lt = (leaf_i + 1) / 3.0
            leaf_center = v_lerp(start, end, lt)
            leaf_center = (leaf_center[0] - side * 0.018, leaf_center[1] + rng.uniform(-0.02, 0.04), leaf_center[2])
            _add_single_leaf(scene, leaf_center, rng.uniform(0.18, 0.28), leaf_light if leaf_i == 0 else leaf, rng)

    # Tán nhỏ ở ngọn dây leo để phần trên tường có cụm lá rõ hơn.
    crown = (inner_x - side * 0.08, top_y + rng.uniform(-0.02, 0.08), z + lean + rng.uniform(-0.08, 0.08))
    _add_leaf_cluster(scene, crown, rng.uniform(0.24, 0.38), rng.randint(14, 22), leaf, leaf_light, rng)


def _add_water_jar(
    scene: SceneMesh,
    center: Vec3,
    scale: float,
    jar: int,
    jar_dark: int,
    jar_water: int,
    moss: int,
    bamboo: int,
    rng: Random,
) -> None:
    """Lu/chum nước làng quê: bụng phình, miệng dày, màu sành nâu cũ."""
    profile = [
        (0.17 * scale, 0.00 * scale),
        (0.30 * scale, 0.08 * scale),
        (0.47 * scale, 0.28 * scale),
        (0.55 * scale, 0.52 * scale),
        (0.49 * scale, 0.72 * scale),
        (0.34 * scale, 0.92 * scale),
        (0.39 * scale, 1.02 * scale),
        (0.31 * scale, 1.10 * scale),
    ]
    scene.add_lathe(center, profile, jar, segments=32, cap_top=False)

    # Chân lu thấp và các gờ nổi quanh thân để nhìn đúng kiểu gốm sành thủ công.
    scene.add_frustum((center[0], center[1] + 0.045 * scale, center[2]), 0.26 * scale, 0.23 * scale, 0.09 * scale, jar_dark, segments=32, cap_bottom=False, cap_top=False)
    for y, radius, thick in [
        (0.33, 0.515, 0.030),
        (0.58, 0.545, 0.034),
        (0.86, 0.405, 0.030),
    ]:
        scene.add_frustum(
            (center[0], center[1] + y * scale, center[2]),
            radius * scale,
            (radius * 0.985) * scale,
            thick * scale,
            jar_dark if y > 0.80 else jar,
            segments=32,
            cap_bottom=False,
            cap_top=False,
        )

    top_y = center[1] + 1.10 * scale
    scene.add_frustum((center[0], top_y + 0.012 * scale, center[2]), 0.34 * scale, 0.30 * scale, 0.070 * scale, jar_dark, segments=32, cap_bottom=False, cap_top=False)
    # Mặt nước tối nằm thấp bên trong miệng lu, không phủ kín gờ miệng.
    scene.add_frustum((center[0], top_y - 0.018 * scale, center[2]), 0.235 * scale, 0.235 * scale, 0.012 * scale, jar_water, segments=32, cap_bottom=False, cap_top=True)

    # Gáo/que múc tre nhỏ cho lu lớn, tạo cảm giác sân quê nhưng vẫn nhẹ file.
    if scale > 0.75:
        start = (center[0] - 0.18 * scale, top_y + 0.05 * scale, center[2] + 0.08 * scale)
        end = (center[0] + 0.52 * scale, top_y + 0.42 * scale, center[2] - 0.30 * scale)
        scene.add_frustum_between(start, end, 0.018 * scale, 0.012 * scale, bamboo, segments=8, cap_ends=True)
        bowl_center = (end[0] + 0.05 * scale, end[1] - 0.015 * scale, end[2] - 0.02 * scale)
        scene.add_frustum(bowl_center, 0.105 * scale, 0.078 * scale, 0.055 * scale, jar_dark, segments=16, cap_bottom=True, cap_top=False)

    # Vệt rêu nhỏ bám thấp trên lu, đặt sát thân để không thành mảng xanh rời.
    for angle, y, h in [(0.65, 0.44, 0.12), (3.72, 0.30, 0.10), (5.15, 0.66, 0.09)]:
        radius = 0.548 * scale if y < 0.60 else 0.46 * scale
        x = center[0] + math.cos(angle) * radius
        z = center[2] + math.sin(angle) * radius
        _add_moss_blob(scene, (x, center[1] + y * scale, z), (0.030 * scale, h * 0.55 * scale, 0.095 * scale), moss, rng)


def _add_areca_palm(
    scene: SceneMesh,
    base: Vec3,
    *,
    height: float,
    trunk: int,
    leaf: int,
    leaf_light: int,
    rng: Random,
) -> None:
    lean_x = rng.uniform(-0.16, 0.16)
    lean_z = rng.uniform(-0.10, 0.10)
    top = (base[0] + lean_x, base[1] + height, base[2] + lean_z)
    scene.add_frustum_between(base, top, 0.060, 0.038, trunk, segments=10)

    # Đốt cau mảnh.
    for i in range(7):
        t = (i + 1) / 8.0
        p = v_lerp(base, top, t)
        scene.add_frustum_between((p[0] - 0.035, p[1], p[2]), (p[0] + 0.035, p[1], p[2]), 0.010, 0.010, trunk, segments=6)

    # Tán lá cau dạng cánh quạt.
    for i in range(14):
        angle = math.tau * i / 14.0 + rng.uniform(-0.08, 0.08)
        length = rng.uniform(0.72, 1.05)
        droop = rng.uniform(0.15, 0.38)
        dir_vec = v_norm((math.cos(angle), -droop, math.sin(angle)))
        side = v_norm(v_cross(dir_vec, (0.0, 1.0, 0.0)))
        if v_len(side) < 0.01:
            side = (1.0, 0.0, 0.0)
        p0 = v_add(top, v_mul(side, -0.06))
        p1 = v_add(top, v_mul(side, 0.06))
        p2 = v_add(top, v_mul(dir_vec, length))
        p_mid = v_add(top, v_mul(dir_vec, length * 0.45))
        leaf_mat = leaf_light if i % 3 == 0 else leaf
        scene.add_triangle(p0, p1, p_mid, leaf_mat)
        scene.add_triangle(p1, p2, p_mid, leaf_mat)
        scene.add_triangle(p2, p0, p_mid, leaf_mat)


def _add_leaf_cluster(
    scene: SceneMesh,
    center: Vec3,
    scale: float,
    count: int,
    leaf: int,
    leaf_light: int,
    rng: Random,
) -> None:
    """Cụm tán/bụi mềm: nhiều ellipsoid nhỏ chồng dính, kèm lá bo tròn ở rìa.

    Bản cũ dùng nhiều tam giác rời nên khi xem gần dễ thấy vuông/cứng. Cách này
    tạo khối tán chính + tán phụ liên kết giống một bụi/cây thật hơn.
    """
    main_radii = (
        scale * rng.uniform(0.62, 0.84),
        scale * rng.uniform(0.34, 0.52),
        scale * rng.uniform(0.54, 0.78),
    )
    main_center = (
        center[0] + rng.uniform(-0.04, 0.04) * scale,
        center[1] + main_radii[1] * 0.58,
        center[2] + rng.uniform(-0.04, 0.04) * scale,
    )
    _add_irregular_ellipsoid(
        scene,
        main_center,
        main_radii,
        leaf,
        rng=rng,
        segments=16,
        rings=8,
        wobble=0.16,
        squash_bottom=0.30,
    )

    # Cụm phụ chồng vào mép để tán không tròn đều nhưng vẫn liền khối.
    puff_count = max(3, min(9, count // 3))
    for i in range(puff_count):
        angle = math.tau * i / puff_count + rng.uniform(-0.45, 0.45)
        offset = (
            math.cos(angle) * main_radii[0] * rng.uniform(0.30, 0.72),
            rng.uniform(-0.16, 0.28) * main_radii[1],
            math.sin(angle) * main_radii[2] * rng.uniform(0.30, 0.72),
        )
        pc = v_add(main_center, offset)
        pr = (
            main_radii[0] * rng.uniform(0.26, 0.46),
            main_radii[1] * rng.uniform(0.30, 0.54),
            main_radii[2] * rng.uniform(0.26, 0.50),
        )
        _add_irregular_ellipsoid(
            scene,
            pc,
            pr,
            leaf_light if (i % 4 == 0 or offset[1] > 0.10 * main_radii[1]) else leaf,
            rng=rng,
            segments=12,
            rings=6,
            wobble=0.20,
            squash_bottom=0.34,
        )

    # Lá rìa nhỏ, bo tròn, bám sát bề mặt để không còn cảm giác lá xanh bay rời.
    fringe_count = max(10, min(42, count * 2))
    for _ in range(fringe_count):
        p = _random_point_on_canopy(main_center, main_radii, rng, lower=-0.38)
        mat = leaf_light if rng.random() < 0.42 else leaf
        size = scale * rng.uniform(0.055, 0.115)
        _add_leaf_diamond(
            scene,
            p,
            mat,
            rng=rng,
            width=size * rng.uniform(0.76, 1.12),
            height=size * rng.uniform(1.00, 1.55),
            tilt=0.30,
        )

# -----------------------------------------------------------------------------
# Nền sau: núi đá vôi Tràng An mềm hơn, dày cây hơn
# -----------------------------------------------------------------------------


def _add_background_karst(scene: SceneMesh, mat: MaterialMap, rng: Random) -> None:
    stone = _mat(mat, "stone")
    stone_dark = _mat(mat, "stone_dark")
    moss = _mat(mat, "moss")
    leaf = _mat(mat, "leaf")
    leaf_light = _mat(mat, "leaf_light")
    trunk = _mat(mat, "wood_dark")

    # Bản v9: giữ nguyên logic nền sau của v8; chỉ làm phần đỉnh núi nhẹ hơn nữa
    # để tránh cảm giác cắt phẳng/nặng ở ngọn, các phần khác không đổi.
    # Dáng này hợp hơn với cảnh quan Tràng An: núi đá vôi gần thẳng đứng nhưng bề
    # mặt bị bào mòn, chân núi có cây bụi/rừng thấp chứ không phải các cột phẳng.
    clusters = [
        ((-5.55, 0.10, 4.70), 3.25, 1.20, 6),
        ((-1.25, 0.10, 5.10), 4.05, 1.35, 7),
        ((3.55, 0.10, 4.90), 3.70, 1.22, 6),
        ((6.35, 0.10, 4.30), 2.55, 0.95, 4),
    ]
    for center, height, radius, count in clusters:
        _add_karst_cluster(scene, center, height, radius, count, stone, stone_dark, moss, leaf, leaf_light, rng)

    # Vành đai cây phía sau tạo lớp cảnh quan riêng trước nền núi đá.
    # Mỗi cây có thân, cành và tán lá dạng khối low-poly.
    _add_background_tree_belt(scene, trunk, leaf, leaf_light, rng)

    # Bụi cây thấp sát chân tường + chân núi để phần nền sau dày và liên kết hơn.
    for i in range(24):
        x = -8.05 + i * 0.68 + rng.uniform(-0.13, 0.13)
        z = rng.uniform(3.12, 3.95)
        scale = rng.uniform(0.26, 0.44)
        _add_leaf_cluster(scene, (x, 1.02 + rng.uniform(-0.08, 0.16), z), scale, rng.randint(7, 11), leaf, leaf_light, rng)

    # Một lớp lùm xanh thưa ngay giữa các chân núi, để đá không còn cảm giác trơ/cứng.
    for i in range(8):
        x = rng.uniform(-7.35, 7.35)
        z = rng.uniform(4.10, 5.55)
        _add_leaf_cluster(scene, (x, rng.uniform(0.62, 1.12), z), rng.uniform(0.22, 0.36), rng.randint(7, 10), leaf, leaf_light, rng)



def _add_background_tree_belt(
    scene: SceneMesh,
    trunk: int,
    leaf: int,
    leaf_light: int,
    rng: Random,
) -> None:
    """Thêm hàng cây phía sau nhà và quanh chân núi.

    Cây ở xa nên dùng hình học thấp-poly: thân nhỏ, vài cành, nhiều cụm tán lá.
    Như vậy nhìn trong GLB rõ là cây xanh nhưng file vẫn nhẹ.
    """
    # Hàng cây ngay sau tường: tán cao hơn tường đá để nhìn rõ từ phía trước.
    front_row = [
        (-7.55, 3.58, 2.35, 0.72),
        (-6.80, 3.76, 1.85, 0.58),
        (-5.95, 3.52, 2.15, 0.66),
        (-4.75, 3.78, 2.55, 0.76),
        (-3.65, 3.45, 1.95, 0.60),
        (-2.55, 3.85, 2.40, 0.70),
        (-1.45, 3.58, 1.85, 0.56),
        (-0.35, 3.92, 2.75, 0.80),
        (0.85, 3.50, 2.10, 0.63),
        (1.95, 3.80, 2.45, 0.72),
        (3.10, 3.58, 1.95, 0.60),
        (4.20, 3.88, 2.65, 0.78),
        (5.35, 3.48, 2.15, 0.66),
        (6.45, 3.76, 2.30, 0.70),
        (7.35, 3.50, 1.90, 0.58),
    ]
    for x, z, height, canopy_scale in front_row:
        _add_background_tree(
            scene,
            base=(x + rng.uniform(-0.12, 0.12), 0.12, z + rng.uniform(-0.10, 0.10)),
            height=height * rng.uniform(0.92, 1.08),
            canopy_scale=canopy_scale * rng.uniform(0.92, 1.12),
            trunk=trunk,
            leaf=leaf,
            leaf_light=leaf_light,
            rng=rng,
        )

    # Một số cây cao hơn chen giữa núi đá vôi để tạo cảm giác có rừng phía sau.
    back_row = [
        (-6.20, 4.85, 2.90, 0.82),
        (-4.20, 5.10, 3.20, 0.90),
        (-2.20, 5.35, 2.80, 0.78),
        (0.30, 5.48, 3.25, 0.95),
        (2.35, 5.25, 2.95, 0.82),
        (4.80, 5.05, 3.10, 0.88),
        (6.80, 4.65, 2.70, 0.76),
    ]
    for x, z, height, canopy_scale in back_row:
        _add_background_tree(
            scene,
            base=(x + rng.uniform(-0.20, 0.20), 0.10, z + rng.uniform(-0.18, 0.18)),
            height=height * rng.uniform(0.88, 1.10),
            canopy_scale=canopy_scale * rng.uniform(0.90, 1.15),
            trunk=trunk,
            leaf=leaf,
            leaf_light=leaf_light,
            rng=rng,
        )

    # Bản v8 thêm vài cây thấp ở chân núi sau: tán phủ lên chân đá để nền sau không còn
    # cảm giác các cột núi trơ trọi.
    filler_row = [
        (-7.10, 4.35, 1.50, 0.46),
        (-5.35, 4.22, 1.65, 0.48),
        (-3.05, 4.48, 1.55, 0.44),
        (-0.85, 4.30, 1.70, 0.50),
        (1.45, 4.42, 1.58, 0.46),
        (3.70, 4.28, 1.68, 0.50),
        (5.95, 4.40, 1.52, 0.44),
        (7.20, 4.18, 1.42, 0.42),
    ]
    for x, z, height, canopy_scale in filler_row:
        _add_background_tree(
            scene,
            base=(x + rng.uniform(-0.16, 0.16), 0.10, z + rng.uniform(-0.12, 0.12)),
            height=height * rng.uniform(0.90, 1.08),
            canopy_scale=canopy_scale * rng.uniform(0.90, 1.14),
            trunk=trunk,
            leaf=leaf,
            leaf_light=leaf_light,
            rng=rng,
        )


def _add_background_tree(
    scene: SceneMesh,
    *,
    base: Vec3,
    height: float,
    canopy_scale: float,
    trunk: int,
    leaf: int,
    leaf_light: int,
    rng: Random,
) -> None:
    """Cây nền phía sau/hai hông: tán mềm, dày, các cụm lá chồng dính nhau."""
    top = (
        base[0] + rng.uniform(-0.18, 0.18),
        base[1] + height,
        base[2] + rng.uniform(-0.12, 0.12),
    )

    # Thân hơi nghiêng + nhiều cành phụ để tán lá có điểm bám tự nhiên.
    scene.add_frustum_between(
        base,
        top,
        0.070 * canopy_scale,
        0.032 * canopy_scale,
        trunk,
        segments=10,
    )

    branch_tips: list[Vec3] = []
    branch_count = rng.randint(5, 7)
    for i in range(branch_count):
        angle = math.tau * i / branch_count + rng.uniform(-0.36, 0.36)
        start = v_lerp(base, top, rng.uniform(0.52, 0.82))
        length = canopy_scale * rng.uniform(0.42, 0.82)
        tip = (
            start[0] + math.cos(angle) * length,
            start[1] + canopy_scale * rng.uniform(0.12, 0.46),
            start[2] + math.sin(angle) * length,
        )
        branch_tips.append(tip)
        scene.add_frustum_between(
            start,
            tip,
            0.026 * canopy_scale,
            0.010 * canopy_scale,
            trunk,
            segments=7,
        )

    crown_center = (top[0], top[1] - 0.10 * canopy_scale, top[2])
    crown_radii = (
        canopy_scale * rng.uniform(0.76, 0.96),
        canopy_scale * rng.uniform(0.54, 0.72),
        canopy_scale * rng.uniform(0.64, 0.88),
    )

    # Tán chính lớn + tán phụ chồng lên nhau: nhìn dày, liền khối nhưng không bị vuông.
    _add_irregular_ellipsoid(scene, crown_center, crown_radii, leaf, rng=rng, segments=20, rings=10, wobble=0.14, squash_bottom=0.22)

    puff_count = rng.randint(6, 9)
    for i in range(puff_count):
        angle = math.tau * i / puff_count + rng.uniform(-0.42, 0.42)
        lateral = rng.uniform(0.32, 0.78)
        offset = (
            math.cos(angle) * crown_radii[0] * lateral,
            rng.uniform(-0.22, 0.30) * crown_radii[1],
            math.sin(angle) * crown_radii[2] * lateral,
        )
        p_center = v_add(crown_center, offset)
        p_radii = (
            crown_radii[0] * rng.uniform(0.30, 0.48),
            crown_radii[1] * rng.uniform(0.30, 0.52),
            crown_radii[2] * rng.uniform(0.30, 0.54),
        )
        mat = leaf_light if rng.random() < 0.28 or offset[1] > 0.08 else leaf
        _add_irregular_ellipsoid(scene, p_center, p_radii, mat, rng=rng, segments=16, rings=8, wobble=0.18, squash_bottom=0.25)

    for tip_i, tip in enumerate(branch_tips):
        blob_mat = leaf_light if tip_i % 3 == 0 else leaf
        _add_irregular_ellipsoid(
            scene,
            tip,
            (canopy_scale * rng.uniform(0.24, 0.38), canopy_scale * rng.uniform(0.20, 0.32), canopy_scale * rng.uniform(0.24, 0.40)),
            blob_mat,
            rng=rng,
            segments=14,
            rings=7,
            wobble=0.18,
            squash_bottom=0.28,
        )

    # Lá rìa dùng fan bo tròn nhỏ, bám sát tán; không còn các tam giác xanh bay rời.
    for _ in range(18):
        c = _random_point_on_canopy(crown_center, crown_radii, rng, lower=-0.34)
        _add_leaf_diamond(scene, c, leaf_light if rng.random() < 0.32 else leaf, rng=rng, width=canopy_scale * rng.uniform(0.08, 0.15), height=canopy_scale * rng.uniform(0.10, 0.20))


def _add_leaf_blob(
    scene: SceneMesh,
    center: Vec3,
    scale: float,
    material: int,
    rng: Random,
    *,
    segments: int = 10,
) -> None:
    """Khối tán lá oval mềm, dùng elipsoid méo nhẹ thay cho lathe faceted."""
    jittered_center = (
        center[0] + rng.uniform(-0.035, 0.035) * scale,
        center[1] + rng.uniform(-0.025, 0.025) * scale,
        center[2] + rng.uniform(-0.035, 0.035) * scale,
    )
    segs = max(10, min(18, segments + 4))
    _add_irregular_ellipsoid(
        scene,
        jittered_center,
        (scale * 0.62, scale * 0.45, scale * 0.56),
        material,
        rng=rng,
        segments=segs,
        rings=7,
        wobble=0.16,
        squash_bottom=0.26,
    )


def _add_single_leaf(scene: SceneMesh, center: Vec3, scale: float, material: int, rng: Random) -> None:
    _add_leaf_diamond(
        scene,
        center,
        material,
        rng=rng,
        width=0.42 * scale,
        height=0.86 * scale,
        tilt=0.34,
    )


def _add_karst_cluster(
    scene: SceneMesh,
    center: Vec3,
    height: float,
    radius: float,
    count: int,
    stone: int,
    stone_dark: int,
    moss: int,
    leaf: int,
    leaf_light: int,
    rng: Random,
) -> None:
    # Chân cụm đá được nối bằng các mound thấp để nhiều cột không còn tách rời/cứng.
    for _ in range(max(3, count // 2)):
        mound_base = (
            center[0] + rng.uniform(-radius * 0.72, radius * 0.72),
            center[1],
            center[2] + rng.uniform(-radius * 0.48, radius * 0.52),
        )
        _add_karst_foot_mound(scene, mound_base, radius * rng.uniform(0.65, 1.05), height * rng.uniform(0.35, 0.55), stone, moss, rng)

    for i in range(count):
        if i == 0:
            angle = rng.uniform(-0.22, 0.22)
            dist = rng.uniform(0.0, radius * 0.16)
            h = height * rng.uniform(0.92, 1.04)
            r = radius * rng.uniform(0.50, 0.62)
        else:
            angle = math.tau * i / count + rng.uniform(-0.55, 0.55)
            dist = rng.uniform(radius * 0.12, radius * 0.82)
            h = height * rng.uniform(0.54, 0.90)
            r = radius * rng.uniform(0.30, 0.52)

        base = (
            center[0] + math.cos(angle) * dist,
            center[1],
            center[2] + math.sin(angle) * dist,
        )

        _add_karst_foot_mound(scene, base, r * rng.uniform(0.95, 1.30), h * rng.uniform(0.30, 0.44), stone, moss, rng)
        _add_rock_pillar(scene, base, h, r, stone, rng)
        _add_soft_karst_grooves(scene, base, h, r, stone_dark, rng)
        _add_karst_vegetation(scene, base, h, r, moss, leaf, leaf_light, rng)


def _add_karst_foot_mound(
    scene: SceneMesh,
    base: Vec3,
    radius: float,
    height: float,
    stone: int,
    moss: int,
    rng: Random,
) -> None:
    """Mảng đá chân núi thấp, bo tròn để cụm núi không còn dựng như cọc."""
    mound_center = (
        base[0] + rng.uniform(-0.05, 0.05) * radius,
        base[1] + max(0.13, height * rng.uniform(0.10, 0.16)),
        base[2] + rng.uniform(-0.05, 0.05) * radius,
    )
    mound_radii = (
        radius * rng.uniform(1.25, 1.85),
        max(0.22, height * rng.uniform(0.10, 0.16)),
        radius * rng.uniform(0.95, 1.45),
    )
    _add_irregular_ellipsoid(
        scene,
        mound_center,
        mound_radii,
        stone,
        rng=rng,
        segments=14,
        rings=6,
        wobble=0.11,
        squash_bottom=0.34,
    )

    # Rêu thấp ở chân núi, dạng mảng mềm thay vì chấm vuông.
    for _ in range(1):
        a = rng.uniform(0.0, math.tau)
        p = (
            mound_center[0] + math.cos(a) * mound_radii[0] * rng.uniform(0.34, 0.82),
            mound_center[1] + mound_radii[1] * rng.uniform(0.10, 0.52),
            mound_center[2] + math.sin(a) * mound_radii[2] * rng.uniform(0.34, 0.82),
        )
        _add_moss_blob(scene, p, (radius * rng.uniform(0.08, 0.15), 0.028, radius * rng.uniform(0.06, 0.12)), moss, rng)


def _add_soft_karst_grooves(scene: SceneMesh, base: Vec3, height: float, radius: float, stone_dark: int, rng: Random) -> None:
    """Rãnh đá cong nhẹ; tránh các đường thẳng đứng làm núi bị đơ."""
    for _ in range(rng.randint(2, 3)):
        a = rng.uniform(0.0, math.tau)
        side = (math.cos(a), math.sin(a))
        y0 = base[1] + height * rng.uniform(0.14, 0.26)
        y1 = base[1] + height * rng.uniform(0.58, 0.86)
        r0 = radius * rng.uniform(0.74, 0.98)
        r1 = radius * rng.uniform(0.38, 0.70)
        start = (base[0] + side[0] * r0, y0, base[2] + side[1] * r0)
        end = (
            base[0] + side[0] * r1 + rng.uniform(-0.08, 0.08) * radius,
            y1,
            base[2] + side[1] * r1 + rng.uniform(-0.08, 0.08) * radius,
        )
        _add_curved_frustum(
            scene,
            start,
            end,
            radius * rng.uniform(0.010, 0.016),
            radius * rng.uniform(0.006, 0.011),
            stone_dark,
            rng=rng,
            bend=radius * rng.uniform(0.05, 0.11),
            steps=4,
            segments=6,
        )


def _add_karst_vegetation(
    scene: SceneMesh,
    base: Vec3,
    height: float,
    radius: float,
    moss: int,
    leaf: int,
    leaf_light: int,
    rng: Random,
) -> None:
    """Cây/rêu bám sườn núi để nền sau rậm rạp hơn nhưng vẫn nhẹ file."""
    for _ in range(rng.randint(2, 3)):
        t = rng.uniform(0.18, 0.78)
        a = rng.uniform(0.0, math.tau)
        side = (math.cos(a), math.sin(a))
        ledge_radius = radius * (1.02 - 0.52 * t) * rng.uniform(0.72, 1.04)
        ledge = (
            base[0] + side[0] * ledge_radius,
            base[1] + height * t,
            base[2] + side[1] * ledge_radius,
        )
        _add_leaf_cluster(scene, ledge, rng.uniform(0.18, 0.32), rng.randint(6, 10), leaf, leaf_light, rng)
        _add_moss_blob(scene, (ledge[0], ledge[1] - 0.07, ledge[2]), (radius * 0.14, 0.030, radius * 0.09), moss, rng)

    # Tán nhỏ trên vai/đỉnh thấp để phá đường silhouette thẳng.
    for _ in range(1):
        t = rng.uniform(0.62, 0.88)
        a = rng.uniform(0.0, math.tau)
        side = (math.cos(a), math.sin(a))
        cap_radius = radius * (0.70 - 0.36 * t) * rng.uniform(0.65, 0.95)
        p = (base[0] + side[0] * cap_radius, base[1] + height * t, base[2] + side[1] * cap_radius)
        _add_leaf_cluster(scene, p, rng.uniform(0.16, 0.26), rng.randint(6, 9), leaf_light, leaf, rng)


def _add_rock_pillar(scene: SceneMesh, base: Vec3, height: float, radius: float, material: int, rng: Random) -> None:
    """Núi đá vôi bo mềm: nhiều ring, chân loe, vai cong, normal mượt.

    Giữ logic tower-karst phía sau nhà nhưng dùng vertex chung + normal hướng tâm
    để bề mặt không còn bị faceted/cứng như các cột add_quad riêng lẻ.
    """
    segments = 18
    levels = 13
    rings: list[list[int]] = []
    centers: list[Vec3] = []
    out = scene.indices_by_material[material]

    phase = rng.random() * math.tau
    phase2 = rng.random() * math.tau
    bend_x = rng.uniform(-0.13, 0.14) * radius
    bend_z = rng.uniform(-0.11, 0.13) * radius
    lean_x = rng.uniform(-0.10, 0.10) * radius
    lean_z = rng.uniform(-0.10, 0.10) * radius
    x_scale = rng.uniform(0.88, 1.18)
    z_scale = rng.uniform(0.82, 1.12)

    def push_vertex(pos: Vec3, ring_center: Vec3, uv: tuple[float, float]) -> int:
        n = v_norm((pos[0] - ring_center[0], 0.16, pos[2] - ring_center[2]))
        idx = len(scene.positions)
        scene.positions.append(pos)
        scene.normals.append(n)
        scene.texcoords.append(uv)
        return idx

    for level in range(levels):
        t = level / (levels - 1)
        y = base[1] + height * t
        smooth = t * t * (3.0 - 2.0 * t)

        # Dáng karst: chân nở, giữa hơi thắt, vai có bụng.
        # Bản v9 siết nhẹ thêm phần crown/top để đỉnh thanh và mềm hơn,
        # không còn cảm giác mặt cắt phẳng/nặng ở phía trên.
        lower_bulge = 0.16 * math.exp(-((t - 0.25) / 0.18) ** 2)
        shoulder_bulge = 0.10 * math.exp(-((t - 0.58) / 0.16) ** 2)
        taper = 1.04 - 0.58 * smooth + lower_bulge + shoulder_bulge
        taper *= 1.0 - 0.10 * t * t
        if t > 0.70:
            tip_t = (t - 0.70) / 0.30
            tip_smooth = tip_t * tip_t * (3.0 - 2.0 * tip_t)
            taper *= 1.0 - 0.42 * tip_smooth
        taper = max(0.135, taper)

        # Tim núi cong nhẹ theo chiều cao để silhouette không còn cột thẳng.
        ring_center = (
            base[0] + math.sin(t * math.pi + phase) * bend_x + lean_x * t,
            y,
            base[2] + math.cos(t * math.pi * 0.92 + phase * 0.8) * bend_z + lean_z * t,
        )
        centers.append(ring_center)

        ring: list[int] = []
        for i in range(segments):
            angle = math.tau * i / segments
            layered_noise = (
                0.075 * math.sin(angle * 2.0 + phase + t * 2.6)
                + 0.045 * math.sin(angle * 5.0 + phase2 + level * 0.55)
                + 0.026 * math.sin(angle * 9.0 + phase * 1.3)
            )
            rough = 1.0 + layered_noise + rng.uniform(-0.014, 0.014)
            rx = radius * taper * x_scale * rough
            rz = radius * taper * z_scale * (1.0 + layered_noise * 0.72)
            if t < 0.18:
                rx *= 1.0 + (0.18 - t) * 0.60
                rz *= 1.0 + (0.18 - t) * 0.50
            # Mép ring lên xuống rất nhẹ để đỉnh/chân không cắt quá phẳng.
            y_jitter = rng.uniform(-0.010, 0.010) * height * (0.45 + 0.55 * (1.0 - t))
            if t > 0.78:
                tip_rim_t = (t - 0.78) / 0.22
                y_jitter += radius * 0.026 * tip_rim_t * tip_rim_t * math.sin(angle * 3.0 + phase2)
            pos = (ring_center[0] + math.cos(angle) * rx, y + y_jitter, ring_center[2] + math.sin(angle) * rz)
            ring.append(push_vertex(pos, ring_center, (i / segments, t * 1.55)))
        rings.append(ring)

    for level in range(levels - 1):
        for i in range(segments):
            j = (i + 1) % segments
            a = rings[level][i]
            b = rings[level][j]
            c = rings[level + 1][j]
            d = rings[level + 1][i]
            out.extend([a, b, c, a, c, d])

    # Nắp chân để không hở khi xoay thấp.
    bottom_center = (centers[0][0], base[1] - 0.012, centers[0][2])
    bottom_idx = len(scene.positions)
    scene.positions.append(bottom_center)
    scene.normals.append((0.0, -1.0, 0.0))
    scene.texcoords.append((0.5, 0.0))
    for i in range(segments):
        j = (i + 1) % segments
        out.extend([bottom_idx, rings[0][j], rings[0][i]])

    # Bản v9: đỉnh núi được làm nhẹ hơn nữa bằng cap bo 2 tầng.
    # Thay vì kéo thẳng lên một chóp cao, phần top thu dần qua 2 vòng nhỏ
    # rồi chốt bằng tip thấp, giúp silhouette mềm hơn và không bị mặt cắt phẳng.
    # Chỉ chỉnh phần cap đỉnh, logic thân núi/scene hiện tại giữ nguyên.
    top_ring = rings[-1]
    top_center = centers[-1]

    cap_rings: list[list[int]] = []
    cap_specs = [
        (0.58, radius * 0.024, 0.045, 1.64),
        (0.24, radius * 0.045, 0.026, 1.74),
    ]
    previous_center = top_center
    for ring_index, (shrink, lift, wobble, v_coord) in enumerate(cap_specs):
        cap_center = (
            top_center[0] + math.sin(phase + ring_index * 0.7) * radius * 0.010,
            top_center[1] + lift,
            top_center[2] + math.cos(phase2 + ring_index * 0.5) * radius * 0.010,
        )
        cap_ring: list[int] = []
        for i, top_idx in enumerate(top_ring):
            angle = math.tau * i / segments
            top_pos = scene.positions[top_idx]
            dx = top_pos[0] - top_center[0]
            dz = top_pos[2] - top_center[2]
            local_shrink = shrink * (1.0 + wobble * math.sin(angle * 3.0 + phase2 + ring_index))
            y_soft = radius * 0.004 * math.sin(angle * 4.0 + phase + ring_index)
            pos = (
                cap_center[0] + dx * local_shrink,
                cap_center[1] + y_soft,
                cap_center[2] + dz * local_shrink,
            )
            idx = len(scene.positions)
            scene.positions.append(pos)
            scene.normals.append(v_norm((pos[0] - cap_center[0], 0.34, pos[2] - cap_center[2])))
            scene.texcoords.append((i / segments, v_coord))
            cap_ring.append(idx)
        cap_rings.append(cap_ring)
        previous_center = cap_center

    previous_ring = top_ring
    for cap_ring in cap_rings:
        for i in range(segments):
            j = (i + 1) % segments
            a = previous_ring[i]
            b = previous_ring[j]
            c = cap_ring[j]
            d = cap_ring[i]
            out.extend([a, b, c, a, c, d])
        previous_ring = cap_ring

    peak = (
        previous_center[0] + rng.uniform(-0.006, 0.006) * radius,
        top_center[1] + radius * rng.uniform(0.052, 0.066),
        previous_center[2] + rng.uniform(-0.006, 0.006) * radius,
    )
    peak_idx = len(scene.positions)
    scene.positions.append(peak)
    scene.normals.append((0.0, 1.0, 0.0))
    scene.texcoords.append((0.5, 1.0))
    for i in range(segments):
        j = (i + 1) % segments
        out.extend([peak_idx, previous_ring[i], previous_ring[j]])
