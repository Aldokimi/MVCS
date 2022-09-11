
def create_repo_parser(subparsers):
    desc = 'Create a new local repository, or clone a new one'
    repo_parser = subparsers.add_parser(
        'create-repo', help=desc, description=desc.capitalize(), aliases=['crepo'])

    repo_parser.set_defaults(func=core.create_repo)

def status_parser(subparsers):
    desc = 'Show the status of the repository'
    parser = subparsers.add_parser(
      'status', help=desc, description=desc.capitalize(), aliases=['st'])
    parser.set_defaults(func=core.status)


def commit_parser(subparsers):
    desc = 'list, create, or edit commits'
    parser = subparsers.add_parser(
        'commit', help=desc, description=desc.capitalize(), aliases=['cm'])

    list_group = parser.add_argument_group('list commits')
    list_group.add_argument( '-l', '--list',help='list commits',action='store_true')
    
    info_group = parser.add_argument_group('commit info')      
    info_group.add_argument('-si', '--show-info', help='Information about the commit with the given number', dest='commit')

    create_group = parser.add_argument_group('create commit')
    create_group.add_argument('-c', '--create', help='Commit message', dest='create')

    amend_group = parser.add_argument_group('amend commit')
    amend_group.add_argument('-a', '--amend', help='Amend the previous commit', dest='amend')

    parser.set_defaults(func=core.commits_handler)


def branch_parser(subparsers):
    desc = 'list, create, delete, or edit branches'
    branch_parser = subparsers.add_parser(
        'branch', help=desc, description=desc.capitalize(), aliases=['br'])

    list_group = branch_parser.add_argument_group('list branches')
    list_group.add_argument(
        '-l', '--list',
        help='list local branches',
        action='store_true')
    list_group.add_argument(
        '-r', '--remotes',
        help='list remote branches in addition to local branches',
        action='store_true')

    create_group = branch_parser.add_argument_group('create branches')
    create_group.add_argument(
        '-c', '--create', nargs='+', help='create branch(es)', dest='create_b',
        metavar='branch')

    delete_group = branch_parser.add_argument_group('delete branches')
    delete_group.add_argument(
        '-d', '--delete', nargs='+', help='delete branch(es)', dest='delete_b',
        metavar='branch')

    edit_group = branch_parser.add_argument_group('edit branches')
    edit_group.add_argument(
        '-rn', '--rename-branch', nargs='+',
        help='renames the current branch (mg branch -rn new_name) '
        'or another specified branch (mg branch -rn branch_name new_name)',
        dest='rename_b'
    )

    branch_parser.set_defaults(func=core.branches_handler)

def merge_branches_parser(subparsers):
    desc = 'Merge two branches'
    parser = subparsers.add_parser(
        'merge', help=desc, description=(
          desc.capitalize() + '. ' + 'Merge the current branch to another branch in the local repository'), aliases=['mrg'])
    parser.add_argument('-m', '--merge', help='Specify a branch name to merge', dest='branch_name')
    parser.set_defaults(func=core.merge_branches)

def upload_parser(subparsers):
    desc = 'Upload the changes to the remote repo'
    parser = subparsers.add_parser(
        'upload', help=desc, description=(
          desc.capitalize() + '. ' + 'Upload all the local commits to the remote repository.'), aliases=['up'])
    parser.set_defaults(func=core.upload)

def checkout_parser(subparsers):
    desc = 'Checkout to another branch'
    parser = subparsers.add_parser(
        'checkout', help=desc, description=(
          desc.capitalize()), aliases=['ch'])
    parser.set_defaults(func=core.checkout)


def diff_parser(subparsers):
    desc = 'Get the difference between two files'
    parser = subparsers.add_parser(
        'diff', help=desc, description=(
          desc.capitalize()), aliases=['df'])
    parser.set_defaults(func=core.diff)


def undo_parser(subparsers):
    desc = 'Undo a specific commit'
    parser = subparsers.add_parser(
        'diff', help=desc, description=(
          desc.capitalize()), aliases=['ud'])
    parser.set_defaults(func=core.undo)

