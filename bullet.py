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
AUTOSAVE = True


class FileValidationError(Exception):
    pass


class Bullet:
    def __init__(self, text, indentation_level=None):
        """
        Create new Bullet with given text and indentation level. If indentation_level is None, automatically detect indentation level.
        """
        self.text = text.strip()[2:]
        self.indentation_level = indentation_level or self.detect_indentation_level(
            text
        )

    def detect_indentation_level(self, raw_text: str) -> int:
        return (len(raw_text) - len(raw_text.lstrip())) // INDENT

    def format(self):
        bullet_symbols = [
            "•",
            "◦",
            "▪",
            # "▫",
        ]
        return f"{INDENT * self.indentation_level * ' '}{bullet_symbols[self.indentation_level % len(bullet_symbols)]} {self.text}"


class Cursor:
    def __init__(self, absolute_position, relative_position, current_line):
        self.absolute_position = absolute_position
        self.x = relative_position
        self.y = current_line


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
        "--autosave",
        "-a",
        action="store_true",
        default=AUTOSAVE,
        help="Boolean: determines if file is saved on every\
            action or only once at the program termination.",
    )
    parser.add_argument(
        "--indentation-level",
        "-i",
        type=int,
        default=INDENT,
        help=f"Allows specification of indentation level\
            default is `{INDENT}`.",
    )
    return parser.parse_args()


def handle_args(args):
    global INDENT, FILENAME, AUTOSAVE
    INDENT = args.indentation_level
    FILENAME = Path(args.filename)
    AUTOSAVE = args.autosave


def read_file(filename: Path):
    if not filename.exists():
        with filename.open("w") as f:
            return ""
    with filename.open() as f:
        return f.read()


def validate_file(data: str):
    for index, bullet in enumerate(data.split("\n"), start=1):
        if not bullet:
            continue
        if not bullet.strip().startswith("-"):
            raise FileValidationError(
                f"The bullet on line {index} doesn't start with a `-`"
            )
            # TODO: allow multiline bullets
    return data


def make_printable_sublist(height: int, lst: list, cursor: int):
    if len(lst) < height:
        return lst, cursor
    start = max(0, cursor - height // 2)
    end = min(len(lst), start + height)
    if end - start < height:
        if start == 0:
            end = min(len(lst), height)
        else:
            start = max(0, end - height)
    sublist = lst[start:end]
    cursor -= start
    return sublist, cursor


def print_bullets(stdscr, bullets, cursor: Cursor):
    bullets_list, _ = make_printable_sublist(
        stdscr.getmaxyx()[0] - 1, bullets.split("\n"), cursor.y
    )
    for i, v in enumerate(bullets_list):
        stdscr.addstr(i, 0, Bullet(v).format())


def update_file(filename, bullets, save=AUTOSAVE):
    if not save:
        return 0
    with filename.open("w") as f:
        return f.write(bullets)


def quit_program(bullets):
    return update_file(FILENAME, bullets, True)


def main(stdscr):
    curses.use_default_colors()
    curses.curs_set(0)

    bullets = validate_file(read_file(FILENAME))
    cursor = Cursor(0, 0, 0)

    while True:
        print_bullets(stdscr, bullets, cursor)
        try:
            key = stdscr.getch()
        except KeyboardInterrupt:  # exit on ^C
            return quit_program(bullets)
        if key in (27, 3):  # esc | ^C
            return quit_program(bullets)
        elif key == 10:  # enter
            raise NotImplementedError
        else:
            continue
        stdscr.refresh()


if __name__ == "__main__":
    handle_args(get_args())
    curses.wrapper(main)
