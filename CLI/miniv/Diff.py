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

        self.__file1 = args.file1

        self.__config_folder = os.path.join(os.path.join(os.getcwd()), ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)
        self.__user_mgt = UM.UserManagement(self.__config_folder)

        if args.diff_repo:
            self.__print_diff_repo()
            return 
            
        if self.__file1:
            self.__file1 = str(self.__file1)
        else:
            raise Exception('Error during running diff, wrong arguments!')

        self.__file2 = self.__get_file2()
        if self.__file2:
            self.__file1 = os.path.join(self.__config_folder.split('.mvcs')[0], self.__file1)
            diff = self.__preform_diff(self.__file1, self.__file2)
            if len(diff) == 0:
                ph.warn("This file is not changed, of file doesn't exist")
            else:
                ph.ok(''.join(diff))
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

        if Repository.is_nonempty_tar_file(commit_file):
            with tarfile.open(commit_file) as ccf:
                ccf.extractall(test_dir)
                try:
                    path = os.path.join(test_dir, os.listdir(test_dir)[1])
                    for filename in os.listdir(path):
                        shutil.move(os.path.join(path, filename), os.path.join(test_dir, filename))
                    os.rmdir(path)
                except Exception:
                    raise Exception("Error happened during decompressing the files of the merge branch!")
        else:
            return None

        for file in os.listdir(test_dir):
            if file == self.__file1:
                return os.path.join(test_dir, file)
        return None

    def __preform_diff(self, file1, file2):
        try:
            with open(file2) as old, open(file1) as new:
                old_lines = old.readlines()
                new_lines = new.readlines()
                
                d = difflib.Differ()
                diff = d.compare(old_lines, new_lines)
                diff_list = list(diff)
                
                i, composed_text = 0, []
                while i < len(diff_list):
                    diff_line = diff_list[i]
                    if diff_line[:2] != "  ":
                        composed_text.append(diff_line[2:])
                    i+=1
                # ph.ok(''.join(composed_text))
                return composed_text
        except Exception as e:
            return []

    def __print_diff_repo(self):
        diffs, new_files = self.diff_repo()
        if len(new_files) != 0:
            ph.msg("You have new new files: \n")
            for new_file in new_files:
                ph.ok(f"+++ {new_file}\n")

        if diffs:
            for file, diff  in diffs:
                ph.ok(f"+++ {file}: \n\n {diff}")
        else:
            ph.warn("There are no changes in the repository!")

    def diff_repo(self):
        has_new_change = False
        # Create a test directory
        unique_test_name = uuid.uuid4().hex
        test_dir = os.path.join(self.__config_folder, unique_test_name)
        os.mkdir(test_dir, 0o777)

        # Decompress the latest commit from the specified branch to a test directory
        working_dir = self.__config_folder.split('.mvcs')[0]
        last_commit_id = self.__repo_management.get_latest_commit(self.__branch)["unique_id"]
        branch_dir = os.path.join(self.__config_folder, self.__branch)
        commit_file = os.path.join(branch_dir, f"{last_commit_id}.tar.xz")

        if Repository.is_nonempty_tar_file(commit_file):
            with tarfile.open(commit_file) as ccf:
                ccf.extractall(test_dir)
                try:
                    path = os.path.join(test_dir, os.listdir(test_dir)[1])
                    for filename in os.listdir(path):
                        shutil.move(os.path.join(path, filename), os.path.join(test_dir, filename))
                    os.rmdir(path)
                except Exception:
                    raise Exception("Error happened during decompressing the files of the merge branch!")

        # Store the files of the branch and the working directory
        test_branch = self.__repo_management.path_to_list(test_dir)
        working_branch = self.__repo_management.path_to_list(working_dir)

        # Get new and common files
        new_files = [item for item in test_branch if item not in working_branch]
        common_files = [item for item in test_branch if item not in new_files]

        if len(new_files) != 0: has_new_change = True

        diffs = {}
        for file in common_files:
            new = os.path.join(working_dir, file)
            old = os.path.join(test_dir, file)
            diff = self.__preform_diff(new, old)
            if len(diff) != 0:
                diffs[file] = "".join(diff)
                has_new_change = True
        
        if has_new_change:
            return diffs, new_files
        else:
            return None