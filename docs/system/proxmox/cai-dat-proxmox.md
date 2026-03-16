# Cài đặt Proxmox VE

<div class="doc-meta" markdown>
<span>:material-account: **Tác giả:** _Team member_</span>
<span>:material-calendar: **Cập nhật:** _2026-03-11_</span>
</div>

## Yêu cầu phần cứng

| Thành phần | Yêu cầu tối thiểu               | Khuyến nghị                   |
| ---------- | ------------------------------- | ----------------------------- |
| CPU        | 64-bit (Intel EMT64 hoặc AMD64) | Multi-core, hỗ trợ VT-x/AMD-V |
| RAM        | 2 GB                            | ≥ 16 GB                       |
| Ổ cứng     | 32 GB                           | SSD ≥ 256 GB                  |
| NIC        | 1 Gbps                          | 2x 1 Gbps (bonding)           |

## Các bước cài đặt

### Bước 1: Tải ISO

Tải phiên bản mới nhất tại [Proxmox Downloads](https://www.proxmox.com/en/downloads).

### Bước 2: Tạo USB Boot

```bash
# Trên Linux
dd bs=1M conv=fdatasync if=proxmox-ve_*.iso of=/dev/sdX
```

!!! warning "Lưu ý"
    Thay `/dev/sdX` bằng device USB thực tế. Kiểm tra kỹ bằng `lsblk` trước khi chạy.

### Bước 3: Cài đặt

1. Boot từ USB
2. Chọn **Install Proxmox VE**
3. Cấu hình disk, network, timezone
4. Đặt password cho root
5. Hoàn tất cài đặt và reboot

### Bước 4: Truy cập Web Interface

Sau khi reboot, truy cập:

```
https://<IP-address>:8006
```

!!! info "Đăng nhập"
    - **Username:** `root`
    - **Realm:** `Linux PAM`
    - **Password:** password đã đặt khi cài đặt

## Cấu hình sau cài đặt

### Cập nhật repository

```bash
# Disable enterprise repo (nếu không có subscription)
sed -i 's/^deb/#deb/' /etc/apt/sources.list.d/pve-enterprise.list

# Thêm no-subscription repo
echo "deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription" > /etc/apt/sources.list.d/pve-no-subscription.list

# Cập nhật
apt update && apt full-upgrade -y
```

---

!!! example "Ví dụ: Thêm hình ảnh"
    Để chèn screenshot vào tài liệu, đặt file ảnh trong `docs/assets/images/` và sử dụng:
    ```markdown
    ![Mô tả ảnh](../assets/images/ten-file.png)
    ```

!!! example "Ví dụ: Nhúng video"
    Để nhúng video YouTube:
    ```html
    <div class="video-wrapper">
      <iframe src="https://www.youtube.com/embed/VIDEO_ID" allowfullscreen></iframe>
    </div>
    ```
