import json
import os
import sys
import numpy as np
from ultralytics import YOLO

# Dictionary quy đổi nhãn sang ký tự hiển thị ngắn trên lưới Text
PIECE_SHORT_NAMES = {
    "Quan_Xe_Do": "XeĐ",
    "Quan_Ma_Do": "MãĐ",
    "Quan_Tuo_Do": "VoiĐ",
    "Quan_Si_Do": "SĩĐ",
    "Quan_Tuong_Do": "TưĐ",
    "Quan_Phao_Do": "PhĐ",
    "Quan_Tot_Do": "TốtĐ",
    "Quan_Xe_Den": "Xen",
    "Quan_Ma_Den": "Măn",
    "Quan_Tuo_Den": "Voin",
    "Quan_Si_Den": "Sĩn",
    "Quan_Tuong_Den": "Tưn",
    "Quan_Phao_Den": "Phn",
    "Quan_Tot_Den": "Tốn",
}


class ChessDetector:

    def __init__(self, model_filename="best.pt", conf_threshold=0.6):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(script_dir, model_filename)
        self.conf_threshold = conf_threshold

        if not os.path.exists(self.model_path):
            print(f"[LỖI DETECT] Không tìm thấy file model tại: {self.model_path}")
            sys.exit(1)

        print(f"[DETECT] Đang tải YOLO model từ: {self.model_path}")
        self.model = YOLO(self.model_path)

    def process_frame(self, frame):
        """Chạy YOLO detect, tính tọa độ bàn cờ và trả ra (result, matrix, json)"""
        results = self.model(frame, conf=self.conf_threshold, verbose=False)

        valid_pieces = []
        for r in results:
            for box in r.boxes:
                class_id = int(box.cls[0])
                piece_name = self.model.names[class_id]

                if (
                    piece_name == "ban_co"
                    or float(box.conf[0]) < self.conf_threshold
                ):
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

        board_matrix = [[" .  " for _ in range(9)] for _ in range(10)]
        pieces_detail = []

        if valid_pieces:
            all_cx = [p["cx"] for p in valid_pieces]
            all_cy = [p["cy"] for p in valid_pieces]

            board_left, board_right = min(all_cx), max(all_cx)
            board_top, board_bottom = min(all_cy), max(all_cy)

            board_w = board_right - board_left
            board_h = board_bottom - board_top

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

                short_name = PIECE_SHORT_NAMES.get(p["piece"], p["piece"][:3])
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

        output_data = {
            "total_pieces": len(pieces_detail),
            "board_matrix": board_matrix,
            "pieces_detail": pieces_detail,
        }

        json_output = json.dumps(output_data, ensure_ascii=False, indent=2)
        return results[0], board_matrix, json_output