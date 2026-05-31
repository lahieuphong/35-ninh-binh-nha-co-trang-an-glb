# Ghi chú tổng hợp - Nhà cổ Tràng An, Ninh Bình

## Mục tiêu

Dự án tạo mô hình `.glb` procedural cho Nhà cổ Tràng An bằng Python thuần. Bản hiện tại nâng cấp scene theo hướng có UV, texture base color, normal map và writer nhúng trực tiếp PNG vào GLB để file output có thể mở độc lập.

## Kỹ thuật chính

- `SceneMesh` hỗ trợ `TEXCOORD_0` và lưu UV cơ bản cho primitive.
- `Material` hỗ trợ `base_color_texture`, `normal_texture` và `normal_scale`.
- `scene_writer.py` ghi GLB theo glTF 2.0, nhúng ảnh PNG vào BIN chunk và tạo `images`, `textures`, `samplers`.
- `scripts/generate_textures.py` dùng Pillow để sinh texture procedural và contact sheet preview.
- Texture là procedural, không nhúng ảnh chụp từ báo/web.

## Vật liệu và texture

Các texture chính nằm trong `assets/textures/nha_co_trang_an/`:

- Gỗ lim cũ: nâu đỏ đến nâu đen, có vân dọc, mắt gỗ và nứt nhỏ.
- Mái ngói vảy: đỏ nâu đất nung, mép tối, bạc màu và có vài vệt rêu.
- Đá vôi: xám kem, xám trắng, nứt tự nhiên, hợp bối cảnh Tràng An.
- Sân gạch: tông cam đất nung ấm, dịu hơn mái, có ron sáng và vết cũ nhẹ.
- Tre và hàng rào tre: tre khô vàng nâu; hàng rào dùng texture riêng tối hơn để nổi trên sân.
- Lu nước gốm sành: nâu cánh gián trầm, có vệt men, vết nung và gờ nổi.
- Cây, rêu, bụi: xanh làng quê, có lớp sáng/tối để tán không bị phẳng.
- Mặt đáy sa bàn: nâu cam đất khô, có vệt khoáng sáng và nứt mảnh, không còn đốm rêu xanh.

Preview texture nằm tại `docs/texture_preview_contact_sheet.png`.

## Các vòng chỉnh sửa đã gộp

- Round 2: làm lại cây và bụi bằng tán ellipsoid mềm, dày hơn; làm lại lu nước với bụng phình, miệng dày, mặt nước và gáo tre; thêm viền/gân đáy sa bàn; khép khe hai hông mái.
- Round 3: hạ độ tươi của sân và mái; lát nửa viên ở mép sân để không hở cạnh; thêm texture riêng cho mặt đáy sạch hơn.
- Round 4: thử tông sân hồng đất/be đào nhạt theo ảnh tham chiếu, đồng thời giữ nguyên các phần còn lại.
- Round 5: điều chỉnh riêng màu sân, lấy họ màu từ mái rồi làm dịu để không còn quá pastel.
- Round 6: chốt sân về cam đất nung ấm; thêm texture hàng rào tre tối hơn; đổi underside sang đất nâu cam hợp bối cảnh Tràng An.
- Round 7: cân lại mặt tiền bằng cách khép đều các cánh cửa giữa, giảm mảng trống đen ở các ô cửa.
- Round 8: làm mềm cụm núi đá vôi phía sau bằng chân loe, thân cong nhẹ, normal mượt, rãnh đá cong và cây bụi/rêu bám sườn.
- Round 9: làm nhẹ phần đỉnh núi bằng taper mềm hơn, tăng level thân núi và thêm cap bo hai tầng để ngọn bớt phẳng/nặng.

## Output hiện tại

```text
File:        output/35_ninh_binh/nha_co_trang_an.glb
Scene:       Trang_An_Heritage_House
Vertices:    731,026
Materials:   37
Primitives:  36
Images:      23 PNG nhúng trong GLB
Textures:    23 texture slots
UV:          TEXCOORD_0 trên 36/36 primitive
Registry:    35-ninh-binh/nha-co-trang-an
```

## Cách kiểm tra nhanh

Project cần Python `>= 3.10` và Pillow nếu muốn sinh lại texture.

```bash
python3 scripts/generate_textures.py
python3 scripts/generate_site.py 35-ninh-binh/nha-co-trang-an
```

Nếu `python3` trên máy là bản cũ, dùng interpreter Python 3.10+ trực tiếp, ví dụ:

```bash
/opt/homebrew/bin/python3.12 scripts/generate_site.py 35-ninh-binh/nha-co-trang-an
```
