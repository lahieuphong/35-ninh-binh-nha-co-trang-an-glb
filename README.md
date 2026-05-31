# 35 - Ninh Bình - Nhà Cổ Tràng An - GLB

Project Python thuần để tạo file `.glb` cho **Nhà cổ Tràng An, Ninh Bình**.

Bản hiện tại dùng **procedural texture**, có `TEXCOORD_0`, `baseColorTexture`, `normalTexture`, `roughnessFactor` và nhúng toàn bộ PNG texture trực tiếp vào file GLB. Texture được sinh bằng Python/Pillow, không dùng ảnh tải từ internet hay ảnh báo chí làm texture.

Output hiện tại:

```text
output/35_ninh_binh/nha_co_trang_an.glb
```

## Thông Số Model

```text
Scene:        Trang_An_Heritage_House
Vertices:     731,026
Materials:    37
Primitives:   36
UV/TEXCOORD:  có, 36/36 primitive
Images:       23 PNG nhúng trong GLB
Textures:     23 texture slots
Registry key: 35-ninh-binh/nha-co-trang-an
```

## Cấu Trúc Chính

```text
assets/
└─ textures/
   └─ nha_co_trang_an/
      ├─ old_lim_wood_basecolor.png
      ├─ old_lim_wood_normal.png
      ├─ fishscale_roof_tile_basecolor.png
      ├─ fishscale_roof_tile_normal.png
      ├─ limestone_wall_basecolor.png
      ├─ limestone_wall_normal.png
      ├─ courtyard_brick_basecolor.png
      ├─ courtyard_brick_normal.png
      ├─ warm_earth_basecolor.png
      ├─ warm_earth_normal.png
      ├─ moss_basecolor.png
      ├─ moss_normal.png
      ├─ village_leaf_basecolor.png
      ├─ village_leaf_normal.png
      ├─ bamboo_basecolor.png
      ├─ bamboo_normal.png
      ├─ bamboo_fence_basecolor.png
      ├─ bamboo_fence_normal.png
      ├─ ceramic_jar_basecolor.png
      ├─ ceramic_jar_normal.png
      ├─ dark_mortar_basecolor.png
      ├─ dark_mortar_normal.png
      ├─ display_underside_basecolor.png
      └─ display_underside_normal.png

docs/
├─ texture_preview_contact_sheet.png
└─ nha_co_trang_an_notes.md          # ghi chú tổng hợp tiếng Việt UTF-8

pyproject.toml                         # khai báo package và dependency Pillow

src/glb_forge/
├─ scene.py                            # primitive, vertex, normal, TEXCOORD_0, Material có hỗ trợ texture
├─ scene_writer.py                     # ghi GLB 2.0, nhúng PNG texture vào BIN chunk
├─ trees.py                            # cây/bụi organic dùng cho cảnh quan quanh nhà
├─ build.py                            # luồng generate dùng chung theo registry
├─ scenes/
│  └─ trang_an_house.py                # dựng hình học Nhà cổ Tràng An + map texture
└─ sites/
   ├─ models.py
   ├─ registry.py
   └─ provinces/
      └─ ninh_binh.py                 # đăng ký registry key 35-ninh-binh/nha-co-trang-an

generators/
└─ 35_ninh_binh/
   └─ nha_co_trang_an.py              # lệnh chạy riêng di tích này

scripts/
├─ generate_textures.py                # sinh texture PNG procedural bằng Pillow
├─ generate_site.py                    # generate theo registry key
└─ generate_all.py                     # generate toàn bộ di tích đã đăng ký
```

## Chạy Code

1. Vào thư mục project:

```bash
cd 35-ninh-binh-nha-co-trang-an-glb
```

2. Project cần Python `>= 3.10`:

```bash
python3 --version
```

3. Cài dependency nếu muốn generate lại GLB/texture:

```bash
python3 -m pip install -e .
```

Hoặc cài Pillow trực tiếp:

```bash
python3 -m pip install "Pillow>=10.0.0"
```

Dependency hiện tại:

```text
Pillow>=10.0.0
```

4. Generate file GLB bằng generator riêng của di tích:

```bash
python3 generators/35_ninh_binh/nha_co_trang_an.py
```

Hoặc generate theo registry key:

```bash
python3 scripts/generate_site.py 35-ninh-binh/nha-co-trang-an
```

Hoặc generate toàn bộ di tích đã đăng ký:

```bash
python3 scripts/generate_all.py
```

Kết quả nằm tại:

```text
output/35_ninh_binh/nha_co_trang_an.glb
```

Không cần Blender. Nếu chỉ dùng file GLB đã có sẵn trong `output/`, không cần chạy lại code.

## Sinh Lại Texture

Texture đã được tạo sẵn trong:

```text
assets/textures/nha_co_trang_an/
```

Nếu muốn sinh lại ảnh texture bằng Python:

```bash
python3 scripts/generate_textures.py
```

Sau đó generate lại GLB:

```bash
python3 generators/35_ninh_binh/nha_co_trang_an.py
```

Bộ texture chính gồm 12 nhóm, mỗi nhóm có `basecolor` và `normal`:

```text
old_lim_wood          gỗ lim/gỗ cổ nâu sẫm cho cột, cửa, khung nhà, xà, viền đế
fishscale_roof_tile   mái ngói vảy đỏ nâu cũ, giảm độ tươi, có vân và mép ngói
limestone_wall        đá vôi xám kem cho tường, bậc, chân cột, núi đá phía sau
courtyard_brick       sân gạch cam đất nung, lấy họ màu từ mái nhưng giảm tone
warm_earth            nền đất ấm quanh nhà
moss                  rêu, mảng ẩm, vết cũ trên đá và cảnh quan
village_leaf          lá cây/bụi làng quê, nhiều sắc xanh sáng/tối
bamboo                tre/cau khô, thân cây và chi tiết tre nhỏ
bamboo_fence          hàng rào tre nâu mật ong đậm hơn để tách khỏi nền sân
ceramic_jar           lu/chum nước nâu sành kiểu quê cũ
dark_mortar           khe ron/mạch tối và normal mảnh cho đường vữa
display_underside     mặt đáy dạng đất nâu cam, hợp bối cảnh Tràng An
```

Preview texture nằm trong:

```text
docs/texture_preview_contact_sheet.png
```

## Cách Map Texture

Trong `src/glb_forge/scenes/trang_an_house.py`, hàm `_make_materials(scene)` map các material của scene vào texture như sau:

```python
OLD_LIM_WOOD = {
    "basecolor": "old_lim_wood_basecolor.png",
    "normal": "old_lim_wood_normal.png",
}

ROOF = {
    "basecolor": "fishscale_roof_tile_basecolor.png",
    "normal": "fishscale_roof_tile_normal.png",
}

LIMESTONE = {
    "basecolor": "limestone_wall_basecolor.png",
    "normal": "limestone_wall_normal.png",
}

COURTYARD_BRICK = {
    "basecolor": "courtyard_brick_basecolor.png",
    "normal": "courtyard_brick_normal.png",
}

WARM_EARTH = {
    "basecolor": "warm_earth_basecolor.png",
    "normal": "warm_earth_normal.png",
}

MOSS = {
    "basecolor": "moss_basecolor.png",
    "normal": "moss_normal.png",
}

VILLAGE_LEAF = {
    "basecolor": "village_leaf_basecolor.png",
    "normal": "village_leaf_normal.png",
}

BAMBOO = {
    "basecolor": "bamboo_basecolor.png",
    "normal": "bamboo_normal.png",
}

BAMBOO_FENCE = {
    "basecolor": "bamboo_fence_basecolor.png",
    "normal": "bamboo_fence_normal.png",
}

CERAMIC_JAR = {
    "basecolor": "ceramic_jar_basecolor.png",
    "normal": "ceramic_jar_normal.png",
}

DARK_MORTAR = {
    "basecolor": "dark_mortar_basecolor.png",
    "normal": "dark_mortar_normal.png",
}

DISPLAY_UNDERSIDE = {
    "basecolor": "display_underside_basecolor.png",
    "normal": "display_underside_normal.png",
}
```

Các nhóm material chính trong scene được gắn như sau:

```python
MATERIAL_TEXTURES = {
    "warm earth base": WARM_EARTH,

    "old dark lim wood": OLD_LIM_WOOD,
    "aged brown wood": OLD_LIM_WOOD,
    "worn golden wood edge": OLD_LIM_WOOD,
    "nearly black carved wood": OLD_LIM_WOOD,
    "neat dark display base edge": OLD_LIM_WOOD,

    "old grey limestone": LIMESTONE,
    "dark stone gaps": LIMESTONE,
    "light worn stone edge": LIMESTONE,

    "soft green moss": MOSS,

    "deep village green leaves": VILLAGE_LEAF,
    "soft young leaf highlights": VILLAGE_LEAF,
    "soft shaded village foliage": VILLAGE_LEAF,
    "soft sunlit leaf clusters": VILLAGE_LEAF,

    "dry bamboo": BAMBOO,
    "aged darker bamboo fence": BAMBOO_FENCE,

    "old countryside brown ceramic water jar": CERAMIC_JAR,
    "dark jar mouth and aged raised bands": CERAMIC_JAR,

    "old red brown roof base slightly muted": ROOF,
    "individual roof tile 1..8": ROOF,

    "old courtyard brick 1..5": COURTYARD_BRICK,

    "warm brown orange compact earth underside": DISPLAY_UNDERSIDE,
    "brown orange earth backing without green spots": DISPLAY_UNDERSIDE,
}
```

Một số material đặc biệt dùng màu trực tiếp thay vì texture đầy đủ:

```text
dark interior shadow             nền tối phía sau cửa để tạo chiều sâu
dark still rain water inside jar mặt nước tối trong lu/chum
warm dusty courtyard grout       khe ron sân, dùng normal mảnh để tránh đường ron quá gắt
```

`src/glb_forge/scene.py` lưu `TEXCOORD_0` cho từng vertex. Các UV được tạo tự động khi dựng primitive/procedural geometry. `src/glb_forge/scene_writer.py` xuất GLB 2.0 và nhúng trực tiếp các PNG vào BIN chunk, khai báo `baseColorTexture` và `normalTexture` theo chuẩn glTF.

## Ghi Chú Dựng Hình

Mô hình tập trung vào các yếu tố nhận diện chính của **Nhà cổ Tràng An, Ninh Bình**:

- Nhà cổ dạng ngang, gợi bố cục nhiều gian, có hiên trước và hệ cột gỗ.
- Cửa bức bàn/cửa gỗ nâu sẫm được chia đều bằng các pano và ô cửa để mặt tiền cân hơn.
- Mái ngói đỏ nâu dạng ngói vảy/ngói cổ, có nhiều viên ngói riêng và giảm nhẹ độ tươi.
- Hai hông mái được khép sát vào hồi tam giác để tránh khe hở không tự nhiên.
- Bậc tam cấp, bó thềm, chân cột và tường thấp dùng đá vôi xám kem/cũ.
- Sân trước dùng gạch cam đất nung, lấy họ màu từ mái nhưng giảm tone để không lấn mái.
- Hàng rào tre được làm đậm hơn sân để nhìn rõ từng thanh tre.
- Lu nước/chum nước có dáng quê cũ: bụng phình, miệng dày, gờ nổi, mặt nước tối và gáo/que tre.
- Cây xanh hai bên và phía sau được làm mềm, dày, nhiều lớp tán, tránh cảm giác vuông/rời.
- Cảnh quan sau nhà có núi đá vôi karst gợi Tràng An: chân núi loe, thân uốn nhẹ, rãnh đá cong, rêu/cây bụi bám sườn.
- Đỉnh núi bản v9 đã được làm nhẹ hơn: taper mềm, cap bo nhiều tầng, tránh cảm giác mặt cắt phẳng.
- Mặt đáy/đế mô hình chuyển sang đất nâu cam, không còn xám lạnh, để hợp hơn với bối cảnh đất và đá vôi Tràng An.

Các chi tiết chưa có đủ số đo thực địa như kích thước nhà, kích thước sân, số lượng cột, số viên ngói, số cánh cửa, độ cao núi đá và mật độ cây xanh được dựng theo ước lượng hợp lý để mô hình dễ xem trong GLB viewer. Đây là bản procedural/semi-realistic phục vụ học tập và trực quan hóa, không phải bản scan hay phục dựng đo đạc tuyệt đối.
