import sys
import os
import argparse
import argcomplete
import traceback

from subprocess import CalledProcessError
from helper import print_helper as ph

import utils.parser as prs

__version__ = '0.1'
SUCCESS = 0
ERRORS_FOUND = 1
INTERNAL_ERROR = 3
NOT_IN_REPO = 4


def build_parser(subcommands):
    parser = argparse.ArgumentParser(
        description=(
            'MVCS: a simple version control system used for small project and in small teams.'),
        formatter_class=argparse.RawDescriptionHelpFormatter)

    if sys.version_info[0] < 3:
        parser.register('action', 'parsers', helpers.AliasedSubParsersAction)

    parser.add_argument('--version', action='version',
                        version=('MiniGit Version: {0}\n'.format(__version__)))
    subparsers = parser.add_subparsers(title='subcommands', dest='subcmd_name')
    subparsers.required = True

    for sub_cmd in subcommands:
        sub_cmd(subparsers)

    return parser


def setup_windows_console():
    if sys.platform == 'win32':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


def print_help(parser):
    print(parser.description)
    print('\ncommands:\n')

    subparsers_actions = [action for action in parser._actions if isinstance(
        action, argparse._SubParsersAction)]

    for subparsers_action in subparsers_actions:
        for choice in subparsers_action._choices_actions:
            print('    {:<19} {}'.format(choice.dest, choice.help))


def main():

    sub_cmds = [
        prs.create_repo_parser,
        prs.status_parser,
        prs.commit_parser,
        prs.branch_parser,
        prs.merge_branches_parser,
        prs.upload_parser,
        prs.update_parser,
        prs.checkout_parser,
        prs.diff_parser,
        prs.undo_parser,
    ]

    parser = build_parser(sub_cmds)
    argcomplete.autocomplete(parser)

    if len(sys.argv) == 1:
        print_help(parser)
        return SUCCESS

    args = parser.parse_args()
    try:

        setup_windows_console()
        return SUCCESS if args.func(args) else ERRORS_FOUND
    except KeyboardInterrupt:
        ph.puts('\n')
        ph.msg('Keyboard interrupt detected, operation aborted')
        return SUCCESS
    except ValueError as e:
        ph.err(e)
        return ERRORS_FOUND
    except CalledProcessError as e:
        ph.err(e.stderr)
        return ERRORS_FOUND
    except:
        ph.err('Some internal error occurred')
        print('\n')
        ph.err_exp(
            ' If you want to help, contact the developer to report bugs and '
            'include the following information:\n\n{1}\n'.format(
                __version__, traceback.format_exc()))
        return INTERNAL_ERROR


if __name__ == "__main__":
    main()
