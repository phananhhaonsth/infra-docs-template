# Quản lý Virtual Machine (VM)

<div class="doc-meta" markdown>
<span>:material-account: **Tác giả:** _Team member_</span>
<span>:material-calendar: **Cập nhật:** _2026-03-11_</span>
</div>

## Tạo VM mới

### Qua Web Interface

1. Đăng nhập Proxmox Web UI tại `https://<IP>:8006`
2. Click **Create VM** (góc trên bên phải)
3. Cấu hình các tab:

=== "General"
    - **Node:** chọn node
    - **VM ID:** auto hoặc nhập thủ công
    - **Name:** đặt tên VM

=== "OS"
    - **ISO image:** chọn ISO đã upload
    - **Type:** Linux / Windows

=== "System"
    - **BIOS:** OVMF (UEFI) hoặc SeaBIOS
    - **Machine:** q35 (khuyến nghị)

=== "Disks"
    - **Storage:** chọn storage pool
    - **Disk size:** tùy nhu cầu

=== "CPU"
    - **Cores:** số core phân bổ
    - **Type:** host (hiệu năng tốt nhất)

=== "Memory"
    - **Memory (MiB):** RAM phân bổ

### Qua Command Line

```bash
# Tạo VM với qm
qm create 100 \
  --name my-vm \
  --memory 4096 \
  --cores 2 \
  --net0 virtio,bridge=vmbr0 \
  --scsihw virtio-scsi-pci \
  --scsi0 local-lvm:32 \
  --ide2 local:iso/ubuntu-22.04.iso,media=cdrom \
  --boot c --bootdisk scsi0
```

## Quản lý VM

### Các thao tác cơ bản

| Thao tác    | Web UI             | Command Line         |
| ----------- | ------------------ | -------------------- |
| Start VM    | Click **Start**    | `qm start <vmid>`    |
| Stop VM     | Click **Stop**     | `qm stop <vmid>`     |
| Shutdown VM | Click **Shutdown** | `qm shutdown <vmid>` |
| Restart VM  | Click **Reboot**   | `qm reboot <vmid>`   |
| Delete VM   | Click **Remove**   | `qm destroy <vmid>`  |

### Snapshot

```bash
# Tạo snapshot
qm snapshot <vmid> <snapname> --description "Mô tả"

# Restore snapshot
qm rollback <vmid> <snapname>

# Xóa snapshot
qm delsnapshot <vmid> <snapname>
```

!!! warning "Lưu ý về Snapshot"
    Snapshot tiêu tốn tài nguyên storage. Không nên giữ quá nhiều snapshot cùng lúc. Thực hiện backup định kỳ thay vì dựa hoàn toàn vào snapshot.

## Backup & Restore

### Cấu hình backup tự động

1. Vào **Datacenter** → **Backup**
2. Click **Add** để tạo backup job
3. Cấu hình schedule, storage, và mode (snapshot/suspend/stop)

### Backup thủ công

```bash
# Backup VM
vzdump <vmid> --storage <storage> --mode snapshot --compress zstd

# Restore VM
qmrestore <backup-file> <vmid> --storage <storage>
```
