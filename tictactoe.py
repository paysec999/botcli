#!/usr/bin/env python3
"""
Tic-Tac-Toe CLI
- Mode: 2-players atau vs CPU (minimax)
- Optional: uses `rich` for colored output if available
"""

from typing import List, Optional, Tuple
import random
import sys

# Try optional rich for nicer colored output
try:
    from rich import print
    from rich.console import Console
    console = Console()
    RICH = True
except Exception:
    RICH = False

# Board indexes:
# 0 | 1 | 2
# 3 | 4 | 5
# 6 | 7 | 8

def print_board(board: List[str]) -> None:
    """Print board in a nice format. board is list of 9 strings: 'X','O', or ' '."""
    def c(s: str) -> str:
        if not RICH:
            return s
        if s == 'X':
            return f"[bold cyan]{s}[/]"
        if s == 'O':
            return f"[bold magenta]{s}[/]"
        return s

    lines = []
    for row in range(3):
        i = row * 3
        line = f" {c(board[i])} │ {c(board[i+1])} │ {c(board[i+2])} "
        lines.append(line)
        if row < 2:
            lines.append("───┼───┼───")
    if RICH:
        console.print("\n".join(lines))
    else:
        print("\n".join(lines))

def print_board_with_index(board: List[str]) -> None:
    """Print board showing indices to help user pick position"""
    indices = [str(i) if board[i] == ' ' else board[i] for i in range(9)]
    def c(s: str) -> str:
        if not RICH:
            return s
        if s == 'X':
            return f"[bold cyan]{s}[/]"
        if s == 'O':
            return f"[bold magenta]{s}[/]"
        return s
    lines = []
    for row in range(3):
        i = row * 3
        line = f" {c(indices[i])} │ {c(indices[i+1])} │ {c(indices[i+2])} "
        lines.append(line)
        if row < 2:
            lines.append("───┼───┼───")
    if RICH:
        console.print("\n".join(lines))
    else:
        print("\n".join(lines))

def check_win(board: List[str], player: str) -> bool:
    wins = [
        (0,1,2), (3,4,5), (6,7,8),  # rows
        (0,3,6), (1,4,7), (2,5,8),  # cols
        (0,4,8), (2,4,6)            # diagonals
    ]
    return any(board[a]==board[b]==board[c]==player for a,b,c in wins)

def is_full(board: List[str]) -> bool:
    return all(cell != ' ' for cell in board)

def available_moves(board: List[str]) -> List[int]:
    return [i for i, cell in enumerate(board) if cell == ' ']

# Minimax for optimal CPU play
def minimax(board: List[str], depth: int, is_maximizing: bool, cpu: str, human: str) -> Tuple[int, Optional[int]]:
    """Returns (score, move_index). Score: +1 cpu win, -1 human win, 0 draw."""
    if check_win(board, cpu):
        return (1, None)
    if check_win(board, human):
        return (-1, None)
    if is_full(board):
        return (0, None)

    best_move: Optional[int] = None
    if is_maximizing:
        best_score = -999
        for m in available_moves(board):
            board[m] = cpu
            score, _ = minimax(board, depth+1, False, cpu, human)
            board[m] = ' '
            if score > best_score:
                best_score = score
                best_move = m
            # alpha-beta not implemented but not necessary for 3x3
        return (best_score, best_move)
    else:
        best_score = 999
        for m in available_moves(board):
            board[m] = human
            score, _ = minimax(board, depth+1, True, cpu, human)
            board[m] = ' '
            if score < best_score:
                best_score = score
                best_move = m
        return (best_score, best_move)

def cpu_move(board: List[str], cpu: str, human: str) -> int:
    """Pick best move using minimax. If multiple best, choose random among them."""
    score, move = minimax(board, 0, True, cpu, human)
    if move is None:
        # fallback
        return random.choice(available_moves(board))
    return move

def get_human_move(board: List[str]) -> int:
    while True:
        try:
            inp = input("Pilih posisi (0-8) atau 'q' untuk keluar: ").strip()
            if inp.lower() in ('q','quit','exit'):
                print("Keluar. Terima kasih sudah bermain!")
                sys.exit(0)
            pos = int(inp)
            if pos < 0 or pos > 8:
                print("Nomor harus antara 0 sampai 8.")
                continue
            if board[pos] != ' ':
                print("Posisi sudah terisi. Pilih yang kosong.")
                continue
            return pos
        except ValueError:
            print("Masukkan angka antara 0-8, misal 4 atau 'q' untuk keluar.")

def play_game(vs_cpu: bool, cpu_first: bool=False) -> None:
    board = [' '] * 9
    human = 'X'
    cpu = 'O'
    current = 'X'  # X selalu mulai (standard)
    if vs_cpu and cpu_first:
        current = cpu

    if RICH:
        console.print("[bold underline]Tic-Tac-Toe[/]\n")

    while True:
        if RICH:
            console.print("\n[dim]Board indices (0..8):[/]")
            print_board_with_index(board)
            console.print("\n[dim]Current board:[/]")
            print_board(board)
        else:
            print("\nBoard indices (0..8):")
            print_board_with_index(board)
            print("\nCurrent board:")
            print_board(board)

        # Current player's turn
        if vs_cpu and current == cpu:
            print("\n[CPU turn]" if RICH else "\nCPU turn")
            move = cpu_move(board, cpu, human)
            board[move] = cpu
            if RICH:
                console.print(f"CPU memilih posisi [bold]{move}[/].")
            else:
                print(f"CPU memilih posisi {move}.")
        else:
            if RICH:
                console.print(f"\nGiliran [bold]{current}[/].")
            else:
                print(f"\nGiliran {current}.")
            move = get_human_move(board)
            board[move] = current

        # Check win/draw
        if check_win(board, current):
            if RICH:
                if vs_cpu:
                    if current == human:
                        console.print("\n[bold green]Kamu menang! 🎉[/]")
                    else:
                        console.print("\n[bold red]CPU menang![/]")
                else:
                    console.print(f"\n[bold green]{current} menang! 🎉[/]")
            else:
                if vs_cpu:
                    if current == human:
                        print("\nKamu menang! 🎉")
                    else:
                        print("\nCPU menang!")
                else:
                    print(f"\n{current} menang!")
            print_board(board)
            break

        if is_full(board):
            if RICH:
                console.print("\n[bold yellow]Seri![/]")
            else:
                print("\nSeri!")
            print_board(board)
            break

        # Swap turn
        current = 'O' if current == 'X' else 'X'

def main():
    if RICH:
        console.print("[bold cyan]Selamat datang di Tic-Tac-Toe![/]")
    else:
        print("Selamat datang di Tic-Tac-Toe!")

    while True:
        print("\nPilih mode permainan:")
        print("1) Dua pemain (local)")
        print("2) Lawan CPU (minimax)")
        print("q) Keluar")
        mode = input("Masukkan pilihan (1/2/q): ").strip().lower()
        if mode == '1':
            play_game(vs_cpu=False)
        elif mode == '2':
            # siapa mulai dulu?
            first = input("Siapa mulai? (h)uman / (c)pu / (r)andom [default h]: ").strip().lower()
            if first == 'c':
                cpu_first = True
            elif first == 'r':
                cpu_first = random.choice([True, False])
            else:
                cpu_first = False
            play_game(vs_cpu=True, cpu_first=cpu_first)
        elif mode in ('q','quit','exit'):
            print("Sampai jumpa!")
            break
        else:
            print("Pilihan tidak valid. Coba lagi.")

if __name__ == "__main__":
    main()
