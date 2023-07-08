#!/usr/bin/env python3

import curses
from pathlib import Path

INDENT = 2
FILESTRING = "list.txt"
FILENAME = (
    Path(__file__).parent.joinpath(FILESTRING).absolute()
    if not Path(FILESTRING).is_file()
    else Path(FILESTRING)
)

class BulletPoint:
    def __init__(self, text, indentation_level):
        self.text = text
        self.indentation_level = indentation_level


class Cursor:
    def __init__(self, absolute_position, relative_position):
        self.absolute_position = absolute_position
        self.relative_position = relative_position


def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Bullet Note is a simple note taking program",
        add_help=False,
    )
    parser.add_argument(
        "--help",
        "-h",
        action="help",
        help="Show this help message and exit.",
    )
    parser.add_argument(
        "filename",
        type=str,
        nargs="?",
        default=FILENAME,
        help=f"Provide a filename to store the bulleted list in.\
            Default is `{FILENAME}`.",
    )
    parser.add_argument(
        "--indentation-level",
        "-i",
        type=int,
        default=INDENT,
        help=f"Allows specification of indentation level\
            default is `{INDENT}`."
    )
    return parser.parse_args()


def handle_args(args):
    global INDENT, FILENAME
    INDENT = args.indentation_level
    FILENAME = Path(args.filename)


def read_file(filename: Path):
    if not filename.exists():
        with filename.open("w") as f:
            return ""
    with filename.open() as f:
        return f.read()


def validate_file(data):
    return data


def print_bullets(stdscr, bullets):
    raise NotImplementedError


def main(stdscr):
    curses.use_default_colors()
    curses.curs_set(0)

    bullets = validate_file(read_file(FILENAME))
    cursor = Cursor(0, 0)

    while True:
        print_bullets(stdscr, bullets)

    raise NotImplementedError


if __name__ == "__main__":
    handle_args(get_args())
    curses.wrapper(main)
