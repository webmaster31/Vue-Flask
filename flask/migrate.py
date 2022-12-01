import argparse
import os
import sys

from app.migrations.lib.run import create_migration_file
from app.migrations.lib.run import get_db_version
from app.migrations.lib.run import run_backward_migration_script
from app.migrations.lib.run import run_forward_migration_script

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
MIGRATION_DIR = os.path.join(ROOT_PATH, 'app', 'migrations')
sys.path.append(MIGRATION_DIR)


def get_arg_parser():
    example_text = '''example:
    %(prog)s -c True
    %(prog)s -rf True
    %(prog)s -rb True
    %(prog)s -db True
    '''
    parser = argparse.ArgumentParser(
        prog='python migrate.py',
        epilog=example_text,
        description='Run for Database Migration',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-c", "--create_migration",
        help="create new migration file with predefined template",
        type=bool,
        default=False
    )
    parser.add_argument(
        "-rf", "--run_forward_migration",
        help="Run forward migration",
        type=bool,
        default=False
    )
    parser.add_argument(
        "-rb", "--run_backward_migration",
        help="Run backward migration",
        type=bool,
        default=False
    )
    parser.add_argument(
        "-db", "--get_db_version",
        help="Get db version",
        type=bool,
        default=False
    )
    return parser


def main():
    parser = get_arg_parser()
    parsed = parser.parse_args()
    db_version = get_db_version()
    if parsed.create_migration:
        create_migration_file()
    elif parsed.get_db_version:
        print(f'Current db version: {db_version}')
    elif parsed.run_forward_migration:
        print(f'Current db version: {db_version}')
        run_forward_migration_script(old_db_version=db_version)
    elif parsed.run_backward_migration:
        print(f'Current db version: {db_version}')
        run_backward_migration_script()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
