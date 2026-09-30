# FILE: agent.py
import json
from chess_rules import ChessRules
import ollama


class ChessAgent:

    def __init__(self, model_name="qwen2.5-coder:14b"):
        self.model_name = model_name

    def analyze_board(self, board_matrix, side_to_move="Do"):
        # 1. Tự động tìm tất cả các nước đi ĐÚNG LUẬT bằng Python
        legal_moves = ChessRules.get_all_legal_moves(
            board_matrix, side_to_move
        )

        if not legal_moves:
            print("[AGENT] Không có nước đi nào hợp lệ (Thua / Hòa)!")
            return None, "Không còn nước đi"

        # Định dạng danh sách nước đi để gửi cho LLM
        moves_text = ""
        for idx, m in enumerate(legal_moves):
            moves_text += f"{idx}. {m['description']}\n"

        formatted_board = ""
        for r_idx, row in enumerate(board_matrix):
            formatted_board += f"Hàng {r_idx}: " + " | ".join(row) + "\n"

        # 2. Tạo Prompt ép LLM chọn chỉ số (index) trong danh sách
        prompt = f"""Bạn là Grandmaster Cờ Tướng.
Bàn cờ hiện tại:
{formatted_board}

LƯỢT ĐI: Bên {side_to_move.upper()}

DANH SÁCH CÁC NƯỚC ĐI ĐÚNG LUẬT CÓ THỂ ĐI:
{moves_text}

YÊU CẦU:
- Hãy phân tích và chọn 1 nước đi TỐT NHẤT từ danh sách trên (từ 0 đến {len(legal_moves)-1}).
- Trả về JSON theo đúng định dạng sau:
{{
  "selected_index": <số_thứ_tự_nước_đi_được_chọn>,
  "reason": "<giải thích lý do chọn nước đi này>"
}}
"""

        try:
            print("\n[AGENT] Đang chọn nước đi tối ưu từ danh sách hợp lệ...")
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                format="json",
            )
            content = response["message"]["content"].strip()
            data = json.loads(content)

            selected_idx = int(data["selected_index"])

            # Đảm bảo index nằm trong phạm vi hợp lệ
            if 0 <= selected_idx < len(legal_moves):
                chosen_move = legal_moves[selected_idx]
                from_r, from_c = (
                    chosen_move["from_row"],
                    chosen_move["from_col"],
                )
                to_r, to_c = chosen_move["to_row"], chosen_move["to_col"]

                print(f"✅ [ĐÃ CHỌN]: {chosen_move['description']}")
                print(f"💡 [LÝ DO]: {data.get('reason', '')}")

                return (from_r, from_c, to_r, to_c), data.get("reason", "")
            else:
                # Nếu LLM chọn index ngoài dải, mặc định lấy nước đi đầu tiên (hoặc nước ăn quân)
                print("⚠️ [CẢNH BÁO] Index chọn out of range, tự động lấy nước đi 0")
                chosen_move = legal_moves[0]
                return (
                    chosen_move["from_row"],
                    chosen_move["from_col"],
                    chosen_move["to_row"],
                    chosen_move["to_col"],
                ), "Mặc định"

        except Exception as e:
            print(f"[LỖI AGENT]: {e}")
            # Fallback nếu LLM bị lỗi JSON: Lấy nước đi hợp lệ đầu tiên
            chosen_move = legal_moves[0]
            return (
                chosen_move["from_row"],
                chosen_move["from_col"],
                chosen_move["to_row"],
                chosen_move["to_col"],
            ), "Fallback move"