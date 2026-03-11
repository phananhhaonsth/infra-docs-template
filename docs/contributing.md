# :material-pencil: Hướng dẫn đóng góp tài liệu

Trang này hướng dẫn cách viết và đóng góp tài liệu vào hệ thống Team Operations Docs.

---

## Quy trình đóng góp

### 1. Clone repository

```bash
git clone https://github.com/your-org/team-docs.git
cd team-docs
```

### 2. Cài đặt môi trường local (tùy chọn)

Để xem trước tài liệu trên máy local:

```bash
pip install -r requirements.txt
mkdocs serve
```

Truy cập `http://127.0.0.1:8000` để xem trang web local.

### 3. Tạo tài liệu mới

1. Vào thư mục tương ứng trong `docs/` (ví dụ: `docs/proxmox/`)
2. Tạo file `.md` mới (ví dụ: `cau-hinh-cluster.md`)
3. Viết nội dung (xem hướng dẫn Markdown bên dưới)

### 4. Cập nhật navigation

Thêm trang mới vào `nav` trong file `mkdocs.yml`:

```yaml
nav:
  - Proxmox:
    - proxmox/index.md
    - Cài đặt Proxmox: proxmox/cai-dat-proxmox.md
    - Cấu hình Cluster: proxmox/cau-hinh-cluster.md  # ← thêm dòng này
```

### 5. Commit & Push

```bash
git add .
git commit -m "docs: thêm hướng dẫn cấu hình cluster Proxmox"
git push origin main
```

!!! success "Tự động deploy"
    Sau khi push lên `main`, GitHub Actions sẽ tự động build và deploy trang web.

---

## Hướng dẫn viết Markdown

### Template tài liệu

Mỗi tài liệu nên bắt đầu với format sau:

```markdown
# Tiêu đề tài liệu

<div class="doc-meta" markdown>
<span>:material-account: **Tác giả:** _Tên bạn_</span>
<span>:material-calendar: **Cập nhật:** _YYYY-MM-DD_</span>
</div>

## Giới thiệu

Mô tả ngắn gọn về nội dung tài liệu.

## Nội dung chính

...
```

### Chèn hình ảnh

Đặt hình ảnh vào `docs/assets/images/` hoặc trong thư mục cùng cấp:

```markdown
![Mô tả hình ảnh](../assets/images/screenshot.png)
```

!!! tip "Hình ảnh có thể phóng to"
    Plugin glightbox cho phép người đọc click vào ảnh để xem phóng to.

### Nhúng video

#### Video từ YouTube

```html
<div class="video-wrapper">
  <iframe src="https://www.youtube.com/embed/VIDEO_ID" allowfullscreen></iframe>
</div>
```

#### Video local

```html
<video controls width="100%">
  <source src="../assets/videos/demo.mp4" type="video/mp4">
</video>
```

### Khối cảnh báo (Admonitions)

```markdown
!!! note "Ghi chú"
    Nội dung ghi chú.

!!! warning "Cảnh báo"
    Nội dung cảnh báo.

!!! tip "Mẹo"
    Nội dung mẹo.

!!! danger "Nguy hiểm"
    Nội dung cảnh báo nguy hiểm.

!!! example "Ví dụ"
    Nội dung ví dụ.
```

Kết quả:

!!! note "Ghi chú"
    Đây là ghi chú mẫu.

!!! warning "Cảnh báo"
    Đây là cảnh báo mẫu.

!!! tip "Mẹo"
    Đây là mẹo mẫu.

### Code blocks

````markdown
```bash
# Lệnh bash
echo "Hello World"
```

```python
# Code Python
print("Hello World")
```

```cisco
! Cisco IOS config
interface GigabitEthernet0/1
  switchport mode access
  switchport access vlan 10
```
````

### Bảng (Table)

```markdown
| Cột 1     | Cột 2     | Cột 3     |
| --------- | --------- | --------- |
| Dữ liệu 1 | Dữ liệu 2 | Dữ liệu 3 |
```

### Tabs

```markdown
=== "Tab 1"
    Nội dung tab 1

=== "Tab 2"
    Nội dung tab 2
```

=== "Ví dụ Tab 1"
    Đây là nội dung tab 1.

=== "Ví dụ Tab 2"
    Đây là nội dung tab 2.

### Phím tắt

```markdown
++ctrl+c++ để copy, ++ctrl+v++ để paste
```

Kết quả: ++ctrl+c++ để copy, ++ctrl+v++ để paste

---

## Thêm danh mục mới

Để thêm một danh mục hoàn toàn mới:

1. Tạo thư mục trong `docs/` (ví dụ: `docs/vpn/`)
2. Tạo file `index.md` trong thư mục đó
3. Thêm vào `nav` trong `mkdocs.yml`:

```yaml
nav:
  # ... existing categories ...
  - VPN:
    - vpn/index.md
    - Cấu hình OpenVPN: vpn/cau-hinh-openvpn.md
```

---

## Quy ước đặt tên file

| Loại          | Quy ước              | Ví dụ                   |
| ------------- | -------------------- | ----------------------- |
| Thư mục       | `kebab-case`         | `switch-core/`          |
| File tài liệu | `kebab-case.md`      | `cai-dat-proxmox.md`    |
| Hình ảnh      | `kebab-case.png/jpg` | `proxmox-dashboard.png` |

!!! warning "Lưu ý"
    - Không dùng dấu tiếng Việt trong tên file
    - Không dùng khoảng trắng, dùng dấu gạch ngang `-`
    - Tên file nên mô tả ngắn gọn nội dung
