import json
import cv2
from agent import ChessAgent
from detector import ChessDetector
from scrcpy_window import ScrcpyWindow
from controller import ChessController

class ChessAgentApp:

    def __init__(self):
        # 1. Khởi tạo kết nối Scrcpy
        self.window_handler = ScrcpyWindow(
            window_title="Pixel 6a", auto_start=True
        )

        # 2. Khởi tạo YOLO Detector
        self.detector = ChessDetector(
            model_filename="best.pt", conf_threshold=0.6
        )

        # 3. Khởi tạo LLM AI Agent (Thay 'qwen2.5' bằng tên model bạn đã pull trong Ollama)
        self.ai_agent = ChessAgent(model_name="qwen2.5-coder")
        # Khởi tạo Controller điều khiển Android
        self.controller = ChessController()

        self.previous_matrix = None

    def print_grid(self, matrix):
        """In ma trận đồ họa dạng Text ra Terminal"""
        print(
            "\n   +------+------+------+------+------+------+------+------+------+"
        )
        print(
            "   | Cột0 | Cột1 | Cột2 | Cột3 | Cột4 | Cột5 | Cột6 | Cột7 | Cột8 |"
        )
        print(
            "---+------+------+------+------+------+------+------+------+------+"
        )

        for row_idx, row in enumerate(matrix):
            row_str = f"H{row_idx}|"
            for cell in row:
                row_str += f" {cell} |"
            print(row_str)

            if row_idx == 4:
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

    def run(self):
        print(
            "[MAIN] Hệ thống bắt đầu hoạt động. Nhấn 'q' trên cửa sổ OpenCV để thoát.\n"
        )

        try:
            while True:
                # BƯỚC 1: Lấy Frame từ Scrcpy
                frame = self.window_handler.get_frame()
                if frame is None:
                    continue

                # BƯỚC 2: Detect bàn cờ qua YOLO
                annotated_result, current_matrix, json_data = (
                    self.detector.process_frame(frame)
                )

                # BƯỚC 3: Nếu phát hiện nước đi mới -> Gửi sang Agent Ollama
                if (
                    current_matrix != self.previous_matrix
                    and json.loads(json_data)["total_pieces"] > 0
                ):
                    self.previous_matrix = current_matrix

                    # print(
                    #     "\n================ [ PHÁT HIỆN BÀN CỜ MỚI ] ================"
                    # )
                    # self.print_grid(current_matrix)

                    # Gửi sang Ollama AI Agent để gợi ý nước đi (Ví dụ lượt đi Đỏ)
                    # Trong vòng lặp chính của main.py

                    # 1. Gọi Agent để tính toán nước đi
                    coords, reason = self.ai_agent.analyze_board(current_matrix, side_to_move="Do")

                    # 2. Nếu lấy được tọa độ hợp lệ -> Thực hiện 2 lần TAP
                    if coords:
                        from_row, from_col, to_row, to_col = coords

                        print(
                            f"\n🚀 [TỰ ĐỘNG THỰC THI] Chạm quân tại ({from_row}, {from_col}) -> Di chuyển đến ({to_row}, {to_col})"
                        )

                        # Gọi Controller thực hiện 2 lần Tap
                        self.controller.move_piece(from_row, from_col, to_row, to_col)
                    
                    print(
                        "\n🤖 ================= [ OLLAMA AI PHÂN TÍCH ] ================="
                    )
                
                 

                # Hiển thị frame OpenCV
                cv2.imshow("YOLO Chess Detector", annotated_result.plot())

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        finally:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    app = ChessAgentApp()
    app.run()