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


class Cursor:
    def __init__(self, relative_position: int, current_line: int):
        self.x = relative_position
        self.y = current_line

    def get_nontext_length(self, bullets: list):
        return len(bullets[self.y]) - len(bullets[self.y].lstrip()) + 2

    def right(self, bullets, characters=1):
        characters = ensure_within_bounds(characters, 1, len(bullets[self.y]) - 1)
        if self.x + characters <= len(bullets[self.y]) - 1:
            self.x += characters
            return
        if self.y + 1 >= len(bullets):
            return
        self.y += 1
        self.x = max(self.get_nontext_length(bullets), 0)

    def left(self, bullets, characters=1):
        characters = ensure_within_bounds(characters, 1, len(bullets[self.y]) - 1)
        if self.x - characters >= self.get_nontext_length(bullets):
            self.x -= characters
            return
        if self.y - 1 < 0:
            return
        self.y -= 1
        self.x = len(bullets[self.y]) - 1

    def up(self, bullets, characters=1):
        if self.y - characters < 0:
            return
        self.y -= characters
        self.x = ensure_within_bounds(
            self.x,
            self.get_nontext_length(bullets),
            len(bullets[self.y]),
        )

    def down(self, bullets, characters=1):
        if self.y + characters >= len(bullets):
            return
        self.y += characters
        self.x = ensure_within_bounds(
            self.x,
            self.get_nontext_length(bullets),
            len(bullets[self.y]),
        )


def ensure_within_bounds(counter: int, minimum: int, maximum: int):
    if counter < minimum:
        return minimum
    elif counter > maximum - 1:
        return maximum - 1
    else:
        return counter


def format_bullet(bullet):
    bullet_symbols = [
        "•",
        "◦",
        "▪",
        # "▫",
    ]
    indentation_level = (len(bullet) - len(bullet.lstrip())) // INDENT
    return "".join(
        [
            INDENT * indentation_level * " ",
            bullet_symbols[indentation_level % len(bullet_symbols)],
            " ",
            bullet.strip()[2:],
        ]
    )


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
    return data.split("\n")


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
        stdscr.getmaxyx()[0] - 1, bullets, cursor.y
    )
    for row, bullet in enumerate(bullets_list):
        for col, char in enumerate(format_bullet(bullet)):
            stdscr.addstr(
                row,
                col,
                char,
                curses.A_REVERSE if row == cursor.y and col == cursor.x else 0,
            )


def update_file(filename, bullets, save=AUTOSAVE):
    if not save:
        return 0
    with filename.open("w") as f:
        return f.write("\n".join(bullets))


def quit_program(bullets):
    return update_file(FILENAME, bullets, True)


def add_bullet(bullets, cursor):
    raise NotImplementedError


def main(stdscr):
    curses.use_default_colors()
    curses.curs_set(0)

    bullets = validate_file(read_file(FILENAME))
    cursor = Cursor(2, 0)

    while True:
        print_bullets(stdscr, bullets, cursor)
        try:
            key = stdscr.getch()
        except KeyboardInterrupt:  # exit on ^C
            return quit_program(bullets)
        if key in (27, 3):  # esc | ^C
            return quit_program(bullets)
        elif key == 10:  # enter
            bullets = add_bullet(bullets, cursor)
        elif key == 259:  # up
            cursor.up(bullets)
        elif key == 258:  # down
            cursor.down(bullets)
        elif key == 260:  # left
            cursor.left(bullets)
        elif key == 261:  # right
            cursor.right(bullets)
        else:
            continue
        stdscr.refresh()


if __name__ == "__main__":
    handle_args(get_args())
    curses.wrapper(main)
