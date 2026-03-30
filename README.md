# fastfetch-spin

A slot machine logo randomizer for [fastfetch](https://github.com/fastfetch-cli/fastfetch). Spins through all built-in logos with a animated reel UI, then runs `fastfetch` with the randomly selected logo.

## Requirements

- **Python 3.8+**
- **fastfetch**, must be installed and available on your `PATH`
  - Fedora/RHEL: `sudo dnf install fastfetch`
  - Arch: `sudo pacman -S fastfetch`
  - Ubuntu/Debian: `sudo apt install fastfetch`
  - macOS: `brew install fastfetch`
- A terminal with **ANSI/VT100 escape code support** (virtually all modern terminals)

## Installation

Install directly with pip so it's available system-wide as `fastfetch-spin`:

```bash
pip install --user .
```

Or into a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

After installing, the `fastfetch-spin` command is on your PATH.

## Usage

Just run:

```bash
fastfetch-spin
```

The program will:
1. Query all built-in fastfetch logos via `fastfetch --list-logos`
2. Animate a slot machine reel that slows to a stop on a randomly chosen logo
3. Run `fastfetch --logo <winner>` to display your system info with that logo
4. Print a footer banner showing the selected logo name

Press `Ctrl+C` at any time to exit cleanly.

## Running without installing

The script can also be run directly:

```bash
python fastfetch_spin.py
```

Or make it executable and run it as a script:

```bash
chmod +x fastfetch_spin.py
./fastfetch_spin.py
```
