class ChessRules:
    @staticmethod
    def get_all_legal_moves(board_matrix, side_to_move):
        """Quét toàn bộ bàn cờ và trả về danh sách TẤT CẢ các nước đi hợp lệ."""
        legal_moves = []
        is_red_turn = side_to_move.lower() in ["do", "red"]

        for r1 in range(10):
            for c1 in range(9):
                piece = board_matrix[r1][c1]
                if not piece or piece == ".":
                    continue

                # Chỉ xét quân của bên tới lượt đi
                is_red_piece = "Đ" in piece
                if is_red_turn != is_red_piece:
                    continue

                # Thử đi tới tất cả các ô trên bàn cờ
                for r2 in range(10):
                    for c2 in range(9):
                        if r1 == r2 and c1 == c2:
                            continue
                        is_legal, _ = ChessRules.is_legal_move(
                            board_matrix, r1, c1, r2, c2, side_to_move
                        )
                        if is_legal:
                            target = board_matrix[r2][c2]
                            move_desc = f"{piece} tại ({r1},{c1}) -> ô ({r2},{c2})"
                            if target != ".":
                                move_desc += f" [ĂN QUÂN {target}]"

                            legal_moves.append({
                                "from_row": r1,
                                "from_col": c1,
                                "to_row": r2,
                                "to_col": c2,
                                "description": move_desc,
                            })
        return legal_moves
    @staticmethod
    def is_legal_move(board_matrix, from_r, from_c, to_r, to_c, side_to_move):
        """Kiểm tra nước đi có đúng luật Cờ Tướng hay không"""
        # 1. Kiểm tra nằm trong phạm vi bàn cờ 10x9
        if not (
            0 <= from_r <= 9
            and 0 <= from_c <= 8
            and 0 <= to_r <= 9
            and 0 <= to_c <= 8
        ):
            return False, "Tọa độ nằm ngoài bàn cờ!"

        # 2. Ô bắt đầu phải có quân cờ
        piece = board_matrix[from_r][from_c]
        if piece == "." or not piece:
            return False, f"Ô xuất phát ({from_r}, {from_c}) là ô TRỐNG!"

        # 3. Phải đi đúng quân của lượt hiện tại
        is_red_turn = side_to_move.lower() in ["do", "red"]
        is_red_piece = "Đ" in piece
        if is_red_turn != is_red_piece:
            return (
                False,
                f"Quân [{piece}] tại ({from_r},{from_c}) không thuộc bên {side_to_move}!",
            )

        # 4. Ô đích không được chứa quân đồng minh
        target_piece = board_matrix[to_r][to_c]
        if target_piece != "." and target_piece:
            is_target_red = "Đ" in target_piece
            if is_red_turn == is_target_red:
                return (
                    False,
                    f"Ô đích ({to_r},{to_c}) đã có quân đồng minh [{target_piece}]!",
                )

        # 5. Kiểm tra quy tắc di chuyển từng loại quân cờ
        piece_type = piece[:2]  # Lấy Xe, Mã, Ph, To, Vo, Sĩ, Tư

        if piece_type in ["Xe"]:
            return ChessRules._check_rook(
                board_matrix, from_r, from_c, to_r, to_c
            )
        elif piece_type in ["Mã", "Mă"]:
            return ChessRules._check_knight(
                board_matrix, from_r, from_c, to_r, to_c
            )
        elif piece_type in ["Ph"]:
            return ChessRules._check_cannon(
                board_matrix, from_r, from_c, to_r, to_c
            )
        elif piece_type in ["Tố", "Tố"]:
            return ChessRules._check_pawn(
                from_r, from_c, to_r, to_c, is_red_turn
            )
        elif piece_type in ["Sĩ"]:
            return ChessRules._check_advisor(
                from_r, from_c, to_r, to_c, is_red_turn
            )
        elif piece_type in ["Vo"]:
            return ChessRules._check_elephant(
                board_matrix, from_r, from_c, to_r, to_c, is_red_turn
            )
        elif piece_type in ["Tư"]:
            return ChessRules._check_king(
                from_r, from_c, to_r, to_c, is_red_turn
            )

        return True, "Hợp lệ"

    @staticmethod
    def _check_rook(board, r1, c1, r2, c2):
        """Xe đi thẳng hoặc ngang, không bị cản"""
        if r1 != r2 and c1 != c2:
            return (
                False,
                f"Quân Xe không thể đi chéo từ ({r1},{c1}) đến ({r2},{c2})!",
            )

        # Đếm số quân cản trên đường đi
        obstacles = 0
        if r1 == r2:  # Đi ngang
            step = 1 if c2 > c1 else -1
            for c in range(c1 + step, c2, step):
                if board[r1][c] != ".":
                    obstacles += 1
        else:  # Đi dọc
            step = 1 if r2 > r1 else -1
            for r in range(r1 + step, r2, step):
                if board[r][c1] != ".":
                    obstacles += 1

        if obstacles > 0:
            return False, "Xe bị cản quân trên đường đi!"
        return True, "Nước đi Xe hợp lệ"

    @staticmethod
    def _check_knight(board, r1, c1, r2, c2):
        """Mã đi hình chữ Nhật (2x1), kiểm tra cản chân Mã"""
        dr, dc = abs(r2 - r1), abs(c2 - c1)
        if not ((dr == 2 and dc == 1) or (dr == 1 and dc == 2)):
            return False, "Mã phải đi đường chéo hình chữ Nhật!"

        # Kiểm tra cản chân Mã (Cản khớp)
        block_r = r1 + (1 if r2 > r1 else -1) if dr == 2 else r1
        block_c = c1 + (1 if c2 > c1 else -1) if dc == 2 else c1

        if board[block_r][block_c] != ".":
            return False, f"Mã bị cản chân tại ({block_r}, {block_c})!"
        return True, "Nước đi Mã hợp lệ"

    @staticmethod
    def _check_cannon(board, r1, c1, r2, c2):
        """Pháo đi thẳng, ăn quân phải qua đúng 1 ngòi"""
        if r1 != r2 and c1 != c2:
            return False, "Pháo chỉ đi thẳng hoặc ngang!"

        obstacles = 0
        if r1 == r2:
            step = 1 if c2 > c1 else -1
            for c in range(c1 + step, c2, step):
                if board[r1][c] != ".":
                    obstacles += 1
        else:
            step = 1 if r2 > r1 else -1
            for r in range(r1 + step, r2, step):
                if board[r][c1] != ".":
                    obstacles += 1

        is_capture = board[r2][c2] != "."
        if not is_capture and obstacles != 0:
            return False, "Pháo di chuyển (không ăn quân) phải mở đường trống!"
        if is_capture and obstacles != 1:
            return False, "Pháo ăn quân phải có đúng 1 ngòi!"
        return True, "Nước đi Pháo hợp lệ"

    @staticmethod
    def _check_pawn(r1, c1, r2, c2, is_red):
        """Tốt tiến 1 ô, qua sông được đi ngang"""
        dr = r2 - r1
        dc = abs(c2 - c1)

        # Đỏ đi từ dưới lên (Hàng 9 -> Hàng 0), Đen đi từ trên xuống (Hàng 0 -> Hàng 9)
        forward = -1 if is_red else 1
        has_crossed_river = (r1 <= 4) if is_red else (r1 >= 5)

        if dr == forward and dc == 0:
            return True, "Tốt tiến"
        if has_crossed_river and dr == 0 and dc == 1:
            return True, "Tốt ngang qua sông"

        return False, "Nước đi Tốt không hợp lệ!"

    @staticmethod
    def _check_advisor(r1, c1, r2, c2, is_red):
        """Sĩ đi chéo 1 ô trong Cung"""
        if abs(r2 - r1) != 1 or abs(c2 - c1) != 1:
            return False, "Sĩ chỉ đi chéo 1 ô!"
        palace_rows = [7, 8, 9] if is_red else [0, 1, 2]
        if r2 not in palace_rows or c2 not in [3, 4, 5]:
            return False, "Sĩ không được ra khỏi Cung!"
        return True, "Nước đi Sĩ hợp lệ"

    @staticmethod
    def _check_elephant(board, r1, c1, r2, c2, is_red):
        """Voi đi chéo 2 ô (không qua sông, không bị cản mắt Voi)"""
        if abs(r2 - r1) != 2 or abs(c2 - c1) != 2:
            return False, "Voi phải đi chéo 2 ô!"
        # Không qua sông
        if is_red and r2 < 5:
            return False, "Voi Đỏ không được qua sông!"
        if not is_red and r2 > 4:
            return False, "Voi Đen không được qua sông!"
        # Cản mắt Voi
        mid_r, mid_c = (r1 + r2) // 2, (c1 + c2) // 2
        if board[mid_r][mid_c] != ".":
            return False, "Voi bị cản mắt!"
        return True, "Nước đi Voi hợp lệ"

    @staticmethod
    def _check_king(r1, c1, r2, c2, is_red):
        """Tướng đi ngang/dọc 1 ô trong Cung"""
        if abs(r2 - r1) + abs(c2 - c1) != 1:
            return False, "Tướng chỉ đi 1 ô ngang hoặc dọc!"
        palace_rows = [7, 8, 9] if is_red else [0, 1, 2]
        if r2 not in palace_rows or c2 not in [3, 4, 5]:
            return False, "Tướng không được ra khỏi Cung!"
        return True, "Nước đi Tướng hợp lệ"