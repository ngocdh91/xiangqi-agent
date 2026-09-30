import cv2
from scrcpy_window import ScrcpyWindow

# Khởi tạo cửa sổ
window_handler = ScrcpyWindow(window_title="Pixel 6a", auto_start=True)

points = []


def mouse_click(event, x, y, flags, param):
    """Bắt sự kiện click chuột để lấy tọa độ Pixel"""
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(f"👉 Điểm {len(points)}: X = {x}, Y = {y}")

        if len(points) == 4:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]

            left = min(xs)
            right = max(xs)
            top = min(ys)
            bottom = max(ys)

            print("\n==================================================")
            print("🎉 TỌA ĐỘ BÀN CỜ ĐÃ ĐO THÀNH CÔNG! Hãy chép 4 dòng này vào controller.py:")
            print("==================================================")
            print(f"self.board_left = {left}")
            print(f"self.board_top = {top}")
            print(f"self.board_right = {right}")
            print(f"self.board_bottom = {bottom}")
            print("==================================================\n")


print("--- HƯỚNG DẪN ĐO ---")
print("Hãy dùng chuột CLICK LẦN LƯỢT vào 4 điểm tâm quân cờ ở 4 GÓC BÀN CỜ:")
print("1. Tâm quân Xe top-left (Hàng 0, Cột 0)")
print("2. Tâm quân Xe top-right (Hàng 0, Cột 8)")
print("3. Tâm quân Xe bottom-left (Hàng 9, Cột 0)")
print("4. Tâm quân Xe bottom-right (Hàng 9, Cột 8)")

cv2.namedWindow("Do Toa Do Ban Co")
cv2.setMouseCallback("Do Toa Do Ban Co", mouse_click)

while True:
    frame = window_handler.get_frame()
    if frame is not None:
        # Vẽ các điểm đã click lên màn hình
        for p in points:
            cv2.circle(frame, p, 5, (0, 0, 255), -1)

        cv2.imshow("Do Toa Do Ban Co", frame)

    if cv2.waitKey(1) & 0xFF == ord("q") or len(points) >= 4:
        break

cv2.destroyAllWindows()