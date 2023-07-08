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
        if not bullet.strip().startswith("-"):
            raise FileValidationError(f"The bullet on line {index} doesn't start with a `-`")
            # TODO: allow multiline bullets
    return data


def print_bullets(stdscr, bullets):
    raise NotImplementedError


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
    cursor = Cursor(0, 0)

    while True:
        print_bullets(stdscr, bullets)
        try:
            key = stdscr.getch()
        except KeyboardInterrupt:  # exit on ^C
            return quit_program(bullets)
        if key == 27:  # esc
            return quit_program(bullets)
        elif key == 10:  # enter
            raise NotImplementedError
        else:
            continue
        stdscr.refresh()


if __name__ == "__main__":
    handle_args(get_args())
    curses.wrapper(main)
