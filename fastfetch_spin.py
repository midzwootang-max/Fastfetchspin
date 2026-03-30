#!/usr/bin/env python3
"""
Fastfetch Logo Randomizer
Spins through logos like a slot machine and reveals one with fastfetch.
"""

import subprocess
import random
import time
import sys
import os
import signal
import re


def get_logos():
    """Parse all built-in fastfetch logo names."""
    result = subprocess.run(["fastfetch", "--list-logos"], capture_output=True, text=True)
    logos = []
    for line in result.stdout.split("\n"):
        line = line.strip()
        # Match lines like: 42) "arch" "archmerge"
        if re.match(r"^\d+\)", line):
            # Find all quoted names, take the first (primary) name
            quoted = re.findall(r'"([^"]+)"', line)
            if quoted:
                logos.append(quoted[0])
    return logos


def write(text):
    sys.stdout.write(text)
    sys.stdout.flush()


def clear():
    write("\033[2J\033[H")


def hide_cursor():
    write("\033[?25l")


def show_cursor():
    write("\033[?25h")


def term_size():
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except Exception:
        return 80, 24


def draw_frame(logo_name, speed_frac, spinning=True):
    """
    Draw the slot machine frame.
    speed_frac: 0.0 = just started (fast), 1.0 = stopped (slow)
    """
    cols, rows = term_size()
    clear()

    box_w = min(64, cols - 4)
    pad = " " * ((cols - box_w) // 2)
    inner = box_w - 2

    # ── Header ──────────────────────────────────────────────────────────────
    header = "F A S T F E T C H   L O G O   S P I N N E R"
    write(f"\033[1;96m{header.center(cols)}\033[0m\n\n")

    # ── Reel window (5 ghost slots + 1 main) ────────────────────────────────
    reel_color = "\033[1;93m" if spinning else "\033[1;92m"
    dim = "\033[2;37m"
    rst = "\033[0m"

    top    = "╔" + "═" * inner + "╗"
    mid    = "╠" + "═" * inner + "╣"
    bot    = "╚" + "═" * inner + "╝"
    blank  = "║" + " " * inner + "║"

    def ghost_row(text):
        truncated = text if len(text) <= inner - 2 else text[: inner - 5] + "..."
        return "║" + truncated.center(inner) + "║"

    # Show 2 ghost rows above/below for depth illusion
    ghost_above = [random.choice(["─ ─ ─", "· · ·", "~ ~ ~"]) for _ in range(2)]
    ghost_below = [random.choice(["─ ─ ─", "· · ·", "~ ~ ~"]) for _ in range(2)]

    write(pad + reel_color + top + rst + "\n")
    for g in ghost_above:
        write(pad + dim + ghost_row(g) + rst + "\n")
    write(pad + reel_color + mid + rst + "\n")

    # Center / active slot
    display = logo_name if len(logo_name) <= inner - 2 else logo_name[: inner - 5] + "..."
    if spinning:
        slot_line = "║" + f"\033[1;97;44m{display.center(inner)}\033[0m" + reel_color + "║"
    else:
        slot_line = "║" + f"\033[1;97;42m{display.center(inner)}\033[0m" + reel_color + "║"
    write(pad + reel_color + slot_line + rst + "\n")

    write(pad + reel_color + mid + rst + "\n")
    for g in ghost_below:
        write(pad + dim + ghost_row(g) + rst + "\n")
    write(pad + reel_color + bot + rst + "\n\n")

    # ── Speed bar ────────────────────────────────────────────────────────────
    bar_w = box_w - 12
    filled = int(bar_w * (1.0 - speed_frac))  # full bar = fast, empty = stopped
    bar = "\033[92m" + "█" * filled + "\033[2;37m" + "░" * (bar_w - filled) + "\033[0m"
    write(pad + f"  Speed  [{bar}]\n\n")

    if not spinning:
        msg = "✓  RESULT LOCKED IN  ✓"
        write(f"\033[1;92m{msg.center(cols)}\033[0m\n\n")
        cmd = f'fastfetch --logo "{logo_name}"'
        write(f"\033[1;93m{cmd.center(cols)}\033[0m\n")


def signal_handler(sig, frame):
    show_cursor()
    write("\n")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    hide_cursor()

    try:
        # ── Load logos ───────────────────────────────────────────────────────
        cols, _ = term_size()
        clear()
        write(f"\033[1;96m{'Loading fastfetch logos...'.center(cols)}\033[0m\n")
        logos = get_logos()

        if not logos:
            write("Error: could not retrieve fastfetch logos.\n")
            return

        write(f"\033[2;37m{f'Found {len(logos)} logos.'.center(cols)}\033[0m\n")
        time.sleep(0.6)

        # ── Pick winner ──────────────────────────────────────────────────────
        winner = random.choice(logos)

        # ── Build spin sequence ──────────────────────────────────────────────
        # 20-40 fast random spins, then a slowing landing sequence, end on winner
        fast_count = random.randint(20, 40)
        slow_count = 12  # frames used to decelerate to the winner

        sequence = [random.choice(logos) for _ in range(fast_count)]

        # Slow-down frames: each one progressively closer in "feel" to winner
        # but still random (except the very last which is the winner)
        for i in range(slow_count - 1):
            sequence.append(random.choice(logos))
        sequence.append(winner)

        total = len(sequence)

        # ── Build delay curve ────────────────────────────────────────────────
        # Fast phase: ~0.045 s/frame
        # Slow phase: ramp from 0.12 → 1.4 s/frame
        delays = []
        for i in range(total):
            if i < fast_count:
                t = i / max(fast_count - 1, 1)
                # Slight decel even in fast phase for realism
                d = 0.045 + t * 0.03
            else:
                t = (i - fast_count) / max(slow_count - 1, 1)
                d = 0.12 + (t ** 1.6) * 1.28
            delays.append(d)

        # ── Animate ──────────────────────────────────────────────────────────
        for i, (logo, delay) in enumerate(zip(sequence, delays)):
            speed_frac = i / (total - 1)
            is_last = i == total - 1
            draw_frame(logo, speed_frac, spinning=not is_last)
            time.sleep(delay)

        # ── Hold on winner briefly ────────────────────────────────────────────
        time.sleep(1.2)

        # ── Run fastfetch ─────────────────────────────────────────────────────
        # Full terminal reset to clear any lingering color/attribute state
        # from the animation before handing off to fastfetch
        write("\033[0m")   # reset attributes
        write("\033c")     # full terminal reset (scroll regions, modes, etc.)
        write("\033[2J\033[H")  # clear screen, cursor to top-left
        sys.stdout.flush()
        show_cursor()
        subprocess.run(["fastfetch", "--logo", winner, "--logo-type", "builtin"])

        # ── Footer banner ─────────────────────────────────────────────────────
        cols, _ = term_size()
        bar = "\033[1;92m" + "═" * cols + "\033[0m"
        write(f"\n{bar}\n")
        label = f"  Selected logo: {winner}  "
        write(f"\033[1;97;42m{label.center(cols)}\033[0m\n")
        write(f"{bar}\n\n")

    finally:
        show_cursor()


if __name__ == "__main__":
    main()
