import subprocess
import time
import cv2


class ChessController:

    def __init__(self, device_id=None):
        self.device_id = device_id

        # -------------------------------------------------------------
        # 1. TỌA ĐỘ ĐO TRÊN ẢNH OPENCV (Window Scrcpy)
        # -------------------------------------------------------------
        self.crop_left = 62  # Tâm quân Xe top-left (Hàng 0, Cột 0)
        self.crop_top = 650
        self.crop_right = 1020  # Tâm quân Xe bottom-right (Hàng 9, Cột 8)
        self.crop_bottom = 1730

        # Kích thước khung hình OpenCV thu được
        self.img_w = 1080
        self.img_h = 2400

        # -------------------------------------------------------------
        # 2. ĐỘ PHÂN GIẢI THỰC CỦA ĐIỆN THOẠI (ADB Resolution)
        # -------------------------------------------------------------
        self.phone_w, self.phone_h = self._get_phone_screen_size()

        # Tính tỉ lệ Scale giữa Màn hình điện thoại / Ảnh OpenCV
        self.scale_x = (
            self.phone_w / float(self.img_w) if self.img_w > 0 else 1.0
        )
        self.scale_y = (
            self.phone_h / float(self.img_h) if self.img_h > 0 else 1.0
        )

        print(
            f"[CONTROLLER] Phone Res: {self.phone_w}x{self.phone_h} | Scale X: {self.scale_x:.2f}, Scale Y: {self.scale_y:.2f}"
        )

    def _get_phone_screen_size(self):
        """Lấy độ phân giải thực của điện thoại qua ADB"""
        try:
            cmd = ["adb", "shell", "wm", "size"]
            if self.device_id:
                cmd.insert(1, "-s")
                cmd.insert(2, self.device_id)
            out = subprocess.check_output(cmd, text=True)
            # Dạng chuỗi trả về: "Physical size: 1080x2400"
            size_str = out.split(":")[-1].strip()
            w, h = map(int, size_str.split("x"))
            return w, h
        except Exception:
            return 1080, 2400  # Default fallback

    def set_window_frame_size(self, img_w: int, img_h: int):
        """Cập nhật kích thước ảnh thực tế nhận từ OpenCV/Scrcpy để tự động cân bằng Scale"""
        self.img_w = img_w
        self.img_h = img_h
        self.scale_x = self.phone_w / float(self.img_w)
        self.scale_y = self.phone_h / float(self.img_h)

    def grid_to_phone_xy(self, row: int, col: int):
        """Quy đổi (row, col) -> Tọa độ Pixel chuẩn trên màn hình ĐIỆN THOẠI THỰC"""
        # 1. Tính tọa độ trên ảnh OpenCV
        step_x = (self.crop_right - self.crop_left) / 8.0
        step_y = (self.crop_bottom - self.crop_top) / 9.0

        img_x = self.crop_left + (col * step_x)
        img_y = self.crop_top + (row * step_y)

        # 2. Quy đổi sang tọa độ Màn hình Điện thoại thực (Gửi cho ADB)
        phone_x = int(img_x * self.scale_x)
        phone_y = int(img_y * self.scale_y)

        return phone_x, phone_y

    def _exec_adb_tap(self, x: int, y: int):
        """Gửi lệnh chạm ADB"""
        adb_cmd = ["adb", "shell", "input", "tap", str(x), str(y)]
        if self.device_id:
            adb_cmd.insert(1, "-s")
            adb_cmd.insert(2, self.device_id)
        subprocess.run(adb_cmd, check=True)

    def move_piece(
        self,
        from_row: int,
        from_col: int,
        to_row: int,
        to_col: int,
        delay_between_taps: float = 0.4,
    ):
        """Thực hiện di chuyển quân cờ với độ trễ và tọa độ đã qua Scale"""
        x1, y1 = self.grid_to_phone_xy(from_row, from_col)
        x2, y2 = self.grid_to_phone_xy(to_row, to_col)

        print(
            f"[CONTROLLER] Tap 1: ({from_row},{from_col}) -> ADB Screen ({x1}, {y1})"
        )
        self._exec_adb_tap(x1, y1)

        # Đợi game kích hoạt animation chọn quân
        time.sleep(delay_between_taps)

        print(
            f"[CONTROLLER] Tap 2: ({to_row},{to_col}) -> ADB Screen ({x2}, {y2})"
        )
        self._exec_adb_tap(x2, y2)