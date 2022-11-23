import difflib
import os
import shutil
import tarfile
import uuid

from . import Repository

from helper import RepoManagement as RM
from helper import UserManagement as UM
from helper import print_helper   as ph

class diff():
    __repo_management, __config_folder, __user_mgt = None, None, None
    __file1, __file2 = None, None
    def __init__(self, args) -> None:

        if args.file1: self.__file1 = args.file1

        self.__config_folder = os.path.join(os.path.join(os.getcwd()), ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)
        self.__user_mgt = UM.UserManagement(self.__config_folder)

        if args.diff_repo:
            self.__print_diff_repo()
            return 
            
        if self.__file1:
            self.__file1 = str(self.__file1)
            test_dir, self.__file2 = self.__get_file2()
        else:
            raise Exception('Error during running diff, wrong arguments!')

        if self.__file2:
            self.__file1 = os.path.join(self.__config_folder.split('.mvcs')[0], self.__file1)
            diff = preform_diff(self.__file1, self.__file2, diff_only=True)
            if not diff:
                ph.ok(" This file is not changed, or file doesn't exist")
            else:
                ph.warn(" You have some changes one the file(s): ")
                ph.msg("\n  ➜  " + ''.join(diff))
            
            shutil.rmtree(test_dir)
        else:
            ph.err(f"Error, there is not file with name {self.__file1}")

    def __get_file2(self):
        # Create a test directory to extract the last commit to
        unique_test_name = uuid.uuid4().hex
        test_dir = os.path.join(self.__config_folder, unique_test_name)
        os.mkdir(test_dir, 0o777)

        # Decompress the latest commit from the specified branch to a test directory
        last_commit_id = self.__repo_management.get_latest_commit(
            self.__user_mgt.get_user_data()["current_branch"])["unique_id"]
        branch_dir = os.path.join(
            self.__config_folder, self.__user_mgt.get_user_data()["current_branch"])
        commit_file = os.path.join(
            branch_dir, f"{last_commit_id}.tar.xz")

        if Repository.repo.is_nonempty_tar_file(commit_file):
            try:
                with tarfile.open(commit_file) as ccf:
                    ccf.extractall(test_dir)
            except Exception as e:
                raise Exception(e)
        else:
            shutil.rmtree(test_dir)
            return None

        for file in os.listdir(test_dir):
            if file == self.__file1:
                return test_dir, os.path.join(test_dir, file)

        shutil.rmtree(test_dir)
        return None

    def __print_diff_repo(self):
        diffs, new_files = diff_repo(self.__config_folder, self.__repo_management, self.__user_mgt)
        if len(new_files) != 0:
            ph.warn(" You have new new files: ")
            for new_file in new_files:
                ph.msg(f"\n  ➜  {new_file}\n")
        if diffs:
            ph.warn(" You have some changed files: ")
            for file, diff  in diffs.items():
                ph.msg(f"\n  ➜  {file} : \n\t {diff}")
        else:
            ph.warn("There are no changes in the repository!")

def diff_repo(config_folder, repo_management, user_mgt):
    has_new_change = False
    working_dir = config_folder.split('.mvcs')[0]
    working_branch_list = repo_management.path_to_list(working_dir)
    # Create a test directory
    unique_test_name = uuid.uuid4().hex
    test_dir = os.path.join(config_folder, unique_test_name)
    os.mkdir(test_dir, 0o777)

    # Get the commit ID
    if len(user_mgt.get_user_data()["new_commits"]) == 1:
        branch_data = repo_management.get_branch_data(
                branch_name = user_mgt.get_user_data()["current_branch"])
        if not branch_data:
            raise Exception(
                "Error, couldn't get branch data while renaming the branch!")
        if len(branch_data["commits"]) == 0:
                return None, new_files
        else:
            last_commit_id = repo_management.get_latest_commit(
                user_mgt.get_user_data()["current_branch"])["unique_id"]
    else:
        branch_data = repo_management.get_branch_data(
            branch_name=user_mgt.get_user_data()["current_branch"])
        if not branch_data:
            raise Exception(
                "Error, couldn't get branch data while renaming the branch!")
        branch_id = branch_data["id"]
        last_commit_id, last_commit = user_mgt.get_last_new_commit(branch_id)
        if last_commit_id == 0:
            last_commit_id = repo_management.get_latest_commit(
                user_mgt.get_user_data()["current_branch"])["unique_id"]
        else:
            last_commit_id = last_commit["unique_id"]

    branch_dir = os.path.join(
        config_folder, user_mgt.get_user_data()["current_branch"])
    commit_file = os.path.join(
        branch_dir, f"{last_commit_id}.tar.xz")

    # Extract commit to the test directory    
    if Repository.repo.is_nonempty_tar_file(commit_file):
        with tarfile.open(commit_file) as ccf:
            ccf.extractall(test_dir)

    test_branch_list = [item.split(os.sep)[1] for item in repo_management.path_to_list(test_dir)]

    # print(test_branch_list)
    new_files = [item for item in working_branch_list if\
        item not in test_branch_list and ".mvcs" not in item
    ]

    # Get new and common files
    common_files = [item for item in working_branch_list if item not in new_files]

    if len(new_files) != 0: has_new_change = True

    diffs = {}
    # print(test_branch_list, working_branch_list)
    for file in common_files:
        if not ".mvcs" in file:
            new = os.path.join(working_dir, file)
            old = os.path.join(test_dir, file)
            diff = preform_diff(new, old)
            if len(diff) != 0:
                diffs[file] = "".join(diff)
                has_new_change = True
    
    if has_new_change:
        shutil.rmtree(test_dir)
        return diffs, new_files
    else:
        shutil.rmtree(test_dir)
        return None, new_files

def preform_diff(file1, file2, diff_only=False):
    try:
        with open(file2) as old, open(file1) as new:
            old_lines = old.readlines()
            new_lines = new.readlines()
            
            d = difflib.Differ()
            diff = d.compare(old_lines, new_lines)
            diff_list = list(diff)
            
            if diff_only: return diff_list
            
            i, composed_text = 0, []
            while i < len(diff_list):
                diff_line = diff_list[i]
                if diff_line[:2] != "  ":
                    composed_text.append(diff_line[2:])
                i+=1
            return composed_text
    except Exception as e:
        return []
