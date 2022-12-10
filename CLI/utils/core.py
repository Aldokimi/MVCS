import os

from miniv import Repository, Commit, Branch, Upload,\
    Status, Diff, Merge, Update

from helper import RepoManagement as RM
from helper import UserManagement as UM
from helper import print_helper as PH

IN_REPO = '.mvcs' in os.listdir(os.getcwd())


def create_repo(args):
    '''
    Creating a new repository:
        You have two options:

            * To clone a repository from the remote server, you can use for this `miniv repo --clone clone_url`
            * To create a new repository, for this a new repository will be created locally but you will \
have the option to create this repository remotely as well,\
you can user for this `miniv repo --create name_of_the_new_repo`
    '''
    try:
        Repository.repo(args)
    except Exception as e:
        raise Exception(e)


def status(args):
    if not IN_REPO:
        PH.err("You are not in a MVCS repo!")
        return
    try:
        Status.status(args)
    except Exception as e:
        raise Exception(e)


def commits_handler(args):
    if not IN_REPO:
        PH.err("You are not in a MVCS repo!")
        return
    try:
        Commit.commit(args)
    except Exception as e:
        raise Exception(e)


def branches_handler(args):
    if not IN_REPO:
        PH.err("You are not in a MVCS repo!")
        return
    try:
        Branch.branch(args)
    except Exception as e:
        raise Exception(e)


def merge_branches(args):
    if not IN_REPO:
        PH.err("You are not in a MVCS repo!")
        return
    try:
        Merge.merge(args)
    except Exception as e:
        raise Exception(e)


def upload(args):
    if not IN_REPO:
        PH.err("You are not in a MVCS repo!")
        return
    try:
        Upload.upload(args)
    except Exception as e:
        raise Exception(e)


def update(args):
    if not IN_REPO:
        PH.err("You are not in a MVCS repo!")
        return
    try:
        Update.update(args)
    except Exception as e:
        raise Exception(e)


def checkout(args):
    if not IN_REPO:
        PH.err("You are not in a MVCS repo!")
        return
    repo_config_path = os.path.join(os.path.join(os.getcwd()), ".mvcs")
    repo_management = RM.RepoManagement(repo_config_path)
    user_management = UM.UserManagement(repo_config_path)
    branch_name = str(args.branch_name) if args.branch_name else None
    try:
        Branch.checkOut(
            branch_name, repo_config_path, repo_management, user_management)
    except Exception as e:
        raise Exception(e)


def diff(args):
    if not IN_REPO:
        PH.err("You are not in a MVCS repo!")
        return
    try:
        Diff.diff(args)
    except Exception as e:
        raise Exception(e)


def undo(args):
    if not IN_REPO:
        PH.err("You are not in a MVCS repo!")
        return
    repo_config_path = os.path.join(os.path.join(os.getcwd()), ".mvcs")
    repo_management = RM.RepoManagement(repo_config_path)
    user_management = UM.UserManagement(repo_config_path)
    try:
        Commit.undo(repo_config_path, repo_management, user_management)
    except Exception as e:
        raise Exception(e)
