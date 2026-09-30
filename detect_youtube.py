import json
import os
import sys
import cv2
import numpy as np
import pygetwindow as gw
from mss import mss
from ultralytics import YOLO

# 1. Khởi tạo Model
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "best.pt")

if not os.path.exists(MODEL_PATH):
    print(f"[LỖI] Không tìm thấy file best.pt tại: {MODEL_PATH}")
    sys.exit(1)

model = YOLO(MODEL_PATH)

# Tìm cửa sổ scrcpy
windows = gw.getWindowsWithTitle("Pixel 6a")
if not windows:
    print("[LỖI] Chưa mở scrcpy!")
    sys.exit(1)

scrcpy_window = windows[0]
previous_board_matrix = None

# Bảng quy đổi tên nhãn YOLO sang ký tự viết tắt 2 ký tự hiển thị trên lưới
# Bạn có thể chỉnh lại cho khớp chính xác với tên nhãn trong best.pt của bạn
PIECE_SHORT_NAMES = {
    "Quan_Xe_Do": "XeĐ",
    "Quan_Ma_Do": "MãĐ",
    "Quan_Tuo_Do": "VoiĐ",  # Tượng/Voi Đỏ
    "Quan_Si_Do": "SĩĐ",
    "Quan_Tuong_Do": "TưĐ",
    "Quan_Phao_Do": "PhĐ",
    "Quan_Tot_Do": "TốtĐ",
    "Quan_Xe_Den": "Xen",
    "Quan_Ma_Den": "Măn",
    "Quan_Tuo_Den": "Voin",  # Tượng/Voi Đen
    "Quan_Si_Den": "Sĩn",
    "Quan_Tuong_Den": "Tưn",
    "Quan_Phao_Den": "Phn",
    "Quan_Tot_Den": "Tốn",
}


def parse_yolo_to_board_matrix(results):
    """Lọc nhãn nhiễu, căn chỉnh viền tự động và đưa về ma trận 10 hàng x 9 cột"""
    board_matrix = [[" .  " for _ in range(9)] for _ in range(10)]
    valid_pieces = []

    for r in results:
        for box in r.boxes:
            class_id = int(box.cls[0])
            piece_name = model.names[class_id]

            # Bỏ qua nhãn 'ban_co' hoặc confidence quá thấp
            if piece_name == "ban_co" or float(box.conf[0]) < 0.6:
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            valid_pieces.append(
                {
                    "piece": piece_name,
                    "cx": cx,
                    "cy": cy,
                    "confidence": round(float(box.conf[0]), 2),
                }
            )

    if not valid_pieces:
        return board_matrix, []

    # Tự động định vị viền bàn cờ dựa vào tọa độ các quân biên
    all_cx = [p["cx"] for p in valid_pieces]
    all_cy = [p["cy"] for p in valid_pieces]

    board_left, board_right = min(all_cx), max(all_cx)
    board_top, board_bottom = min(all_cy), max(all_cy)

    board_w = board_right - board_left
    board_h = board_bottom - board_top

    pieces_detail = []
    for p in valid_pieces:
        col = (
            int(round((p["cx"] - board_left) / (board_w / 8)))
            if board_w > 0
            else 0
        )
        row = (
            int(round((p["cy"] - board_top) / (board_h / 9)))
            if board_h > 0
            else 0
        )

        col = int(np.clip(col, 0, 8))
        row = int(np.clip(row, 0, 9))

        # Lấy tên viết tắt hiển thị cho đẹp
        short_name = PIECE_SHORT_NAMES.get(p["piece"], p["piece"][:3])
        # Format canh lề 4 ký tự cho đều ô
        board_matrix[row][col] = f"{short_name:^4}"

        pieces_detail.append(
            {
                "piece": p["piece"],
                "row": row,
                "col": col,
                "bbox_center": [round(p["cx"], 1), round(p["cy"], 1)],
                "confidence": p["confidence"],
            }
        )

    return board_matrix, pieces_detail


def print_visual_grid(matrix):
    """In ma trận ra dạng lưới đồ họa bằng ký tự dễ đọc trên Terminal"""
    print("\n   +------+------+------+------+------+------+------+------+------+")
    print("   | Cột0 | Cột1 | Cột2 | Cột3 | Cột4 | Cột5 | Cột6 | Cột7 | Cột8 |")
    print("---+------+------+------+------+------+------+------+------+------+")

    for row_idx, row in enumerate(matrix):
        row_str = f"H{row_idx}|"
        for cell in row:
            row_str += f" {cell} |"
        print(row_str)

        if row_idx == 4:
            # Vẽ Sông phân cách giữa Hàng 4 và Hàng 5
            print(
                "---+==========================================================+"
            )
            print(
                "   |~~~~~~~~~~~~~~~~~~~~~~~ S Ô N G ~~~~~~~~~~~~~~~~~~~~~~~~~~|"
            )
            print(
                "---+==========================================================+"
            )
        else:
            print(
                "---+------+------+------+------+------+------+------+------+------+"
            )


# --- VÒNG LẶP CHẠY THỜI GIAN THỰC ---
sct = mss()
print("Đang lắng nghe bàn cờ... Lưới đồ họa sẽ xuất hiện khi có nước đi!\n")

try:
    while True:
        if scrcpy_window.isMinimized:
            continue

        bbox = {
            "top": max(0, scrcpy_window.top),
            "left": max(0, scrcpy_window.left),
            "width": scrcpy_window.width,
            "height": scrcpy_window.height,
        }

        if bbox["width"] <= 0 or bbox["height"] <= 0:
            continue

        sct_img = sct.grab(bbox)
        frame = np.array(sct_img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        results = model(frame, conf=0.5, verbose=False)
        current_board_matrix, pieces_list = parse_yolo_to_board_matrix(results)

        # Kiểm tra sự thay đổi trạng thái
        if current_board_matrix != previous_board_matrix and len(pieces_list) > 0:
            previous_board_matrix = current_board_matrix

            print(
                "\n==================== [ TRẠNG THÁI BÀN CỜ ] ===================="
            )
            print_visual_grid(current_board_matrix)
            print(f"Tổng số quân cờ quét được: {len(pieces_list)}")

        # Hiển thị cửa sổ OpenCV
        annotated_frame = results[0].plot()
        cv2.imshow("YOLO Detect Co Tuong", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cv2.destroyAllWindows()