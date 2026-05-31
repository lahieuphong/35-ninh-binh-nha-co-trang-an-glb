# 35 - Ninh Bình - Nhà Cổ Tràng An - GLB Textured

Project Python thuần để tạo file `.glb` cho **Nhà cổ Tràng An, Ninh Bình**.

Bản này đã được nâng cấp theo barem của file mẫu **29 - Hà Nội - Tháp Rùa Hồ Gươm**:

- `SceneMesh` có `TEXCOORD_0`/UV.
- `Material` hỗ trợ `base_color_texture`, `normal_texture`, `normal_scale`.
- `scene_writer.py` nhúng trực tiếp PNG texture vào BIN chunk của GLB.
- Có script sinh texture procedural bằng Pillow.
- GLB output mở độc lập, không cần folder texture đi kèm.

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

## Texture Đã Thêm

Texture nằm tại:

```text
assets/textures/nha_co_trang_an/
```

Danh sách chính:

```text
old_lim_wood_basecolor.png / old_lim_wood_normal.png
fishscale_roof_tile_basecolor.png / fishscale_roof_tile_normal.png
limestone_wall_basecolor.png / limestone_wall_normal.png
courtyard_brick_basecolor.png / courtyard_brick_normal.png
warm_earth_basecolor.png / warm_earth_normal.png
moss_basecolor.png / moss_normal.png
village_leaf_basecolor.png / village_leaf_normal.png
bamboo_basecolor.png / bamboo_normal.png
ceramic_jar_basecolor.png / ceramic_jar_normal.png
dark_mortar_basecolor.png / dark_mortar_normal.png
display_underside_basecolor.png / display_underside_normal.png
```

Các texture được tạo procedural, không lấy trực tiếp ảnh từ báo/web. Tông màu được chọn theo tư liệu về nhà cổ vùng lõi Tràng An: gỗ lim sẫm, mái ngói vảy đỏ nâu cũ, nền/cột/bậc đá vôi xám, sân gạch đỏ, rêu phong và cây xanh quanh núi đá vôi.

Preview texture:

```text
docs/texture_preview_contact_sheet.png
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
      ├─ ceramic_jar_basecolor.png
      ├─ ceramic_jar_normal.png
      ├─ dark_mortar_basecolor.png
      ├─ dark_mortar_normal.png
      ├─ display_underside_basecolor.png
      └─ display_underside_normal.png

src/glb_forge/
├─ scene.py                         # primitive + Material có hỗ trợ texture/UV
├─ scene_writer.py                  # ghi GLB, nhúng PNG texture vào BIN chunk
├─ build.py                         # luồng generate dùng chung
├─ scenes/
│  └─ trang_an_house.py             # source dựng nhà cổ Tràng An + map texture
└─ sites/
   ├─ models.py
   ├─ registry.py
   └─ provinces/
      └─ ninh_binh.py

generators/
└─ 35_ninh_binh/
   └─ nha_co_trang_an.py            # lệnh chạy riêng di tích này

scripts/
├─ generate_site.py                 # generate theo registry key
├─ generate_all.py                  # generate toàn bộ di tích đã đăng ký
└─ generate_textures.py             # sinh lại texture PNG procedural
```

## Chạy Code

1. Vào thư mục project:

```bash
cd 35-ninh-binh-nha-co-trang-an-glb-textured
```

2. Project cần Python `>= 3.10` và Pillow:

```bash
python3 --version
python3 -m pip install Pillow
```

3. Sinh lại texture nếu cần:

```bash
python3 scripts/generate_textures.py
```

4. Generate file GLB:

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

## Cách Map Texture

Trong `src/glb_forge/scenes/trang_an_house.py`, các nhóm material được map như sau:

```python
warm earth base                 -> warm_earth
old dark lim wood               -> old_lim_wood
aged brown wood                 -> old_lim_wood
worn golden wood edge           -> old_lim_wood
nearly black carved wood        -> old_lim_wood
old grey limestone              -> limestone_wall
dark stone gaps                 -> limestone_wall
light worn stone edge           -> limestone_wall
soft green moss                 -> moss
deep village green leaves       -> village_leaf
young leaf highlights           -> village_leaf
dry bamboo                      -> bamboo
old brown ceramic jar           -> ceramic_jar
dark jar mouth                  -> ceramic_jar
old red brown roof base          -> fishscale_roof_tile
individual roof tile 1..8       -> fishscale_roof_tile
old courtyard brick 1..5        -> courtyard_brick
light dusty courtyard grout      -> dark_mortar normal only
clean display underside          -> display_underside
```

Bản này giữ nguyên hình học/scene của file 2, chỉ nâng cấp barem texture/UV/writer theo file 1 và thêm bộ texture cho đúng chất liệu nhà cổ Tràng An.

## Round 2 chỉnh theo feedback

- Làm lại cây/bụi bằng tán mềm, dày và liền khối hơn.
- Làm lại lu nước kiểu sân quê: sành nâu cũ, miệng dày, gờ nổi, mặt nước và gáo tre.
- Sửa mặt đáy thành plinth có viền/gân đối xứng.
- Khép khe hai hông mái để mái dính vào hồi tam giác.

## Chỉnh sửa v3

- Sân gạch đỏ ngoài sân đã được hạ tông cam/tươi xuống đỏ nâu trầm hơn.
- Mái ngói giảm tươi nhẹ, vẫn giữ cảm giác ngói đỏ cũ.
- Hai mép sân gạch được lát thêm nửa viên để không còn khoảng hở ở cạnh trái/phải.
- Mặt đáy dùng texture riêng `display_underside`, bỏ đốm xanh/rêu và làm đường nứt mảnh, tự nhiên hơn.


## Chỉnh sửa v4

- Chỉ chỉnh màu sân trước nhà theo ảnh tham chiếu mới của người dùng.
- Sân đổi từ đỏ nâu đậm sang tông hồng đất / be đào nhạt, sáng hơn mái ngói.
- Khe ron sân chuyển sang màu bụi sáng; không còn nền vữa đỏ sẫm làm sân tối hơn mái.
- Giảm tương phản texture sân và giảm vết nứt/đốm đen để nhìn gần với sân gạch thật hơn.
- Các phần còn lại giữ nguyên từ bản v3.

## Round 8 - Núi đá vôi mềm hơn

Bản v8 chỉ chỉnh lớp núi đá vôi phía sau: tạo chân núi loe/bo, thân núi cong nhẹ, normal mượt hơn, rãnh đá cong tự nhiên hơn và thêm rêu/cây bụi bám sườn để nền sau dày hơn. Các phần sân, mái, cửa, lu nước, hàng rào, cây trước, tường, đáy và bố cục giữ nguyên từ v7.


## Ghi chú chỉnh sửa v9

```text
- Chỉ tinh lại đỉnh núi đá vôi phía sau.
- Thu nhỏ nhẹ tiết diện đoạn trên bằng taper mềm.
- Thêm 2 vòng cap thấp trước khi lên tip nhỏ để đỉnh bo/nhọn tự nhiên hơn.
- Không chỉnh texture/vật liệu và không thay đổi các phần còn lại của mô hình.
```
