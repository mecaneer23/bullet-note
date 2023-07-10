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
        return get_whitespace_len(bullets[self.y]) + 2

    def right(self, bullets, characters=1):
        characters = clamp(characters, 1, len(bullets[self.y]) - 1)
        if self.x + characters <= len(bullets[self.y]) - 1:
            self.x += characters
            return
        if self.y + 1 >= len(bullets):
            return
        self.y += 1
        self.x = max(self.get_nontext_length(bullets), 0)

    def left(self, bullets, characters=1):
        characters = clamp(characters, 1, len(bullets[self.y]) - 1)
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
        self.x = clamp(
            self.x,
            self.get_nontext_length(bullets),
            len(bullets[self.y]),
        )

    def down(self, bullets, characters=1):
        if self.y + characters >= len(bullets):
            return
        self.y += characters
        self.x = clamp(
            self.x,
            self.get_nontext_length(bullets),
            len(bullets[self.y]),
        )


def get_whitespace_len(bullet):
    return len(bullet) - len(bullet.lstrip())


def clamp(counter: int, minimum: int, maximum: int):
    return min(max(counter, minimum), maximum - 1)


def format_bullet(bullet: str):
    symbols = [
        "•",
        "◦",
        "▪",
        # "▫",
    ]
    return bullet.replace(
        "-",
        symbols[(len(bullet) - len(bullet.lstrip())) // INDENT % len(symbols)],
        1,
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


def add_bullet(bullets: list, cursor):
    bullets.insert(
        cursor.y + 1,
        bullets[cursor.y][: get_whitespace_len(bullets[cursor.y]) + 2] + " ",
    )
    cursor.y += 1
    return bullets


def indent(bullets: list, cursor):
    bullets[cursor.y] = " " * INDENT + bullets[cursor.y]
    cursor.x += INDENT
    return bullets


def dedent(bullets: list, cursor):
    if get_whitespace_len(bullets[cursor.y]) > 0:
        bullets[cursor.y] = bullets[cursor.y][INDENT:]
        cursor.x -= INDENT
    return bullets


def delete(bullets: list, cursor):
    bullets.pop(cursor.y)
    cursor.y -= 1
    return bullets


def main(stdscr):
    curses.use_default_colors()
    curses.curs_set(0)

    bullets = validate_file(read_file(FILENAME))
    cursor = Cursor(get_whitespace_len(bullets[0]) + 2, 0)

    while True:
        print_bullets(stdscr, bullets, cursor)
        try:
            key = stdscr.getch()
        except KeyboardInterrupt:  # exit on ^C
            return quit_program(bullets)
        if key in (27, 3):  # esc | ^C
            return quit_program(bullets)
        elif key == 353:  # shift + tab
            bullets = dedent(bullets, cursor)
            stdscr.clear()
        elif key == 10:  # enter
            bullets = add_bullet(bullets, cursor)
            stdscr.clear()
        elif key == 9:  # tab
            bullets = indent(bullets, cursor)
            stdscr.clear()
        elif key == 4:  # ^D
            bullets = delete(bullets, cursor)
            stdscr.clear()
        elif key == 259:  # up
            cursor.up(bullets)
        elif key == 258:  # down
            cursor.down(bullets)
        elif key == 260:  # left
            cursor.left(bullets)
        elif key == 261:  # right
            cursor.right(bullets)
        elif key in (8, 127, 263):  # backspace
            if cursor.x <= 0:
                continue
            current_row = list(bullets[cursor.y])
            current_row.pop(cursor.x - 1)
            bullets[cursor.y] = "".join(current_row)
            cursor.x -= 1
            stdscr.clear()
        else:  # typable characters (basically alphanum)
            current_row = list(bullets[cursor.y])
            current_row.insert(cursor.x, chr(key))
            bullets[cursor.y] = "".join(current_row)
            if cursor.x < len(bullets[cursor.y]):
                cursor.x += 1
            stdscr.clear()
        stdscr.refresh()


if __name__ == "__main__":
    handle_args(get_args())
    curses.wrapper(main)
