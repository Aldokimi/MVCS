from . import core

def create_repo_parser(subparsers):
    desc = 'Create a new local repository, or clone a new one'
    repo_parser = subparsers.add_parser(
        'repository', help=desc, description=desc.capitalize(), aliases=['repo'])
    create_group = repo_parser.add_argument_group('create repository')
    create_group.add_argument(
        '-c', '--create', help='create a new local repository', dest='create',
        metavar='repo')
    create_group.add_argument(
        '-cl', '--clone', help='clone a repository \'miniv --clone URL\' ', dest='clone')
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
    list_group.add_argument( '-l', '--list',help='list commits', action='store_true')
    
    info_group = parser.add_argument_group('commit info')      
    info_group.add_argument('-si', '--show-info', 
                help='Information about the commit with the given number', dest='info', action='store_true')

    create_group = parser.add_argument_group('create commit')
    create_group.add_argument('-c', '--create', help='Commit message', dest='create')

    amend_group = parser.add_argument_group('amend commit')
    amend_group.add_argument('-a', '--amend', help='Amend the previous commit', action='store_true')

    parser.set_defaults(func=core.commits_handler)


def branch_parser(subparsers):
    desc = 'list, create, delete, or edit branches'
    branch_parser = subparsers.add_parser(
        'branch', help=desc, description=desc.capitalize(), aliases=['br'])

    list_group = branch_parser.add_argument_group('list branches')
    list_group.add_argument( '-l', '--list', help='list local branches', action='store_true')
    list_group.add_argument('-r', '--remotes', help='list remote branches in addition to local branches', action='store_true')

    create_group = branch_parser.add_argument_group('create branches')
    create_group.add_argument( '-c', '--create', nargs='+', help='create branch(es)', dest='create_b',metavar='branch')

    delete_group = branch_parser.add_argument_group('delete branches')
    delete_group.add_argument('-d', '--delete', nargs='+', help='delete branch(es)', dest='delete_b', metavar='branch')

    edit_group = branch_parser.add_argument_group('edit branches')
    edit_group.add_argument('-rn', '--rename', nargs='+', 
        help='renames the current branch (miniv branch -rn new_name)'
        'or another specified branch (mg branch -rn branch_name new_name)',
        dest='rename_b'
    )

    branch_parser.set_defaults(func=core.branches_handler)

def merge_branches_parser(subparsers):
    desc = 'Merge two branches'
    parser = subparsers.add_parser('merge', help=desc, description=(
          desc.capitalize() + '. ' + 'Merge the current branch to another branch in the local repository'), aliases=['mrg'])
    parser.add_argument('--branch', help='the branch name that is going to be merged into the current branch', dest="branch")
    parser.set_defaults(func=core.merge_branches)

def upload_parser(subparsers):
    desc = 'Upload the changes to the remote repository'
    parser = subparsers.add_parser( 'upload', help=desc, description=(
          desc.capitalize() + '. ' + 'Upload all the local commits to the remote repository.'), aliases=['up'])
    parser.add_argument('url', help='The repository URL, meaning this is a repository which is not linked to a remote repo'
        'and we are linking it when we pass the repo URL')
    parser.set_defaults(func=core.upload)

def update_parser(subparsers):
    desc = 'Update the current repository with the changes from the remote repository'
    parser = subparsers.add_parser(
        'upload', help=desc, description=(
          desc.capitalize() + '. ' + 'download the changes from the remote repository and apply them on the current branch.'), aliases=['upd'])
    parser.set_defaults(func=core.update)

def checkout_parser(subparsers):
    desc = 'Checkout to another branch'
    parser = subparsers.add_parser('checkout', help=desc, description=(desc.capitalize()), aliases=['ch'])
    parser.add_argument('--to', dest='branch_name', help='The branch destination where to switch to!')
    parser.set_defaults(func=core.checkout)


def diff_parser(subparsers):
    desc = 'Get the difference between two files'
    parser = subparsers.add_parser('diff', help=desc, description=(desc.capitalize()), aliases=['df'])
    parser.set_defaults(func=core.diff)


def undo_parser(subparsers):
    desc = 'Undo a specific commit'
    parser = subparsers.add_parser('undo', help=desc, description=(desc.capitalize()), aliases=['ud'])
    parser.set_defaults(func=core.undo)

