
import difflib
import os
import shutil
import tarfile
import uuid

from . import Repository

from helper import RepoManagement as RM
from helper import UserManagement as UM
from helper import print_helper   as ph


class merge():
    __branch = None
    __repo_management, __config_folder, __user_mgt = None, None, None

    def __init__(self, args) -> None:
        self.__branch   = args.branch

        self.__config_folder = os.path.join(os.path.join(os.getcwd()), ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)
        self.__user_mgt = UM.UserManagement(self.__config_folder)

        if self.__branch:
            self.__branch = str(self.__branch[0])
            self.__merge_branches()
    
    def __merge_branches(self):
        if self.__user_mgt.get_user_data()["current_branch"] == self.__branch:
            ph.err("You cannot merge with the same branch, please choose another branch!")
        else:
            # First we need to decompress the last commit from the specified branch into a test directory (this directory will be called new)
            # Then we need to store the new files in a list and compare them to the current branch's files:
            #       * The additional files from the new directory will be copied to a new directory 
            #       * The additional files from the current branch will be kept
            # Then we will merge the similar files into the new directory
            # Finally the working directory will be replaced with the new directory

            # Create a new directory
            unique_test_name = uuid.uuid4().hex
            test_dir = os.path.join(self.__config_folder, unique_test_name)
            os.mkdir(test_dir, 0o777)

            # Decompress the latest commit from the specified branch to a test directory
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

            # Store the files of the the merge branch, e.g:
            merge_branch = self.__repo_management.path_to_list(test_dir)

            # Store the working directory
            working_directory = self.__repo_management.path_to_list(self.__config_folder.split('.mvcs')[0])

            # Get additional files from the new directory of the merge branch
            new_files = [item for item in merge_branch if item not in working_directory]

            # Create the new directory and copy the additional files to the new directory
            new_directory = os.path.join(self.__config_folder, f"{unique_test_name}_new")
            os.mkdir(new_directory, 0o777)
            for new_file in new_files:
                file_to_move = os.path.join(test_dir, new_file)
                new_dir = ""
                new_files_path_list = os.path.normpath(file_to_move)
                new_files_path_list = new_files_path_list.split(os.sep)
                for i in new_files_path_list[:-1]:
                    new_dir = os.path.join(new_dir, i)
                    if not os.path.isdir(new_dir):
                        os.mkdir(new_dir, 0o777)
                shutil.move(file_to_move, new_directory)

            # Merge the common files into a new file inside the new directory
            common_files = [item.split(f'{test_dir}{os.sep}')[1] for item in merge_branch if item not in new_files]
            for file in common_files:
                new_file = os.path.join(test_dir, file)
                old_file = os.path.join(working_directory, file)
                merge_result = self.merge_files(old_file, new_file)
                merge_file = os.path.join(new_directory, file)
                new_dir = ""
                new_files_path_list = os.path.normpath(merge_file)
                new_files_path_list = new_files_path_list.split(os.sep)
                for i in new_files_path_list[:-1]:
                    new_dir = os.path.join(new_dir, i)
                    if not os.path.isdir(new_dir):
                        os.mkdir(new_dir, 0o777)

                with open(merge_file, 'w') as _merged_file:
                    _merged_file.write(merge_result)

            # Replace the working directory with the new directory
            self.__repo_management.delete_working_directory()
            shutil.copytree(new_dir, self.__config_folder.split('.mvcs')[0], dirs_exist_ok=True) 
        
    def merge_files(self, old_file, new_file):
        try:
            with open(old_file) as old, open(new_file) as new:
                old_lines = old.readlines()
                new_lines = new.readlines()
                
                d = difflib.Differ()
                diff = d.compare(old_lines, new_lines)
                # print("\n".join(diff))

                diff_list = list(diff)
                # Now we have the list we can apply the set of rules

                # The first 2 characters are the main key:
                # [+ ] if the upper and the lower are empty we add this and we continue
                # [+ ] and we have a sequence of + and - the we have a conflict and we surround the + and 1
                # [- ] alone, we continue
                # [  ] we just add it
                i, composed_text, has_conflicts = 0, [], False
                while i < len(diff_list):
                    diff_line = diff_list[i]
                    if diff_line[:2] == "  ":
                        composed_text.append(diff_line[2:])
                        i+=1
                    else:
                        pluses, minuses = [], []
                        pluses.append(diff_line[2:]) if diff_line[:2] == "+ " else minuses.append(diff_line[2:])
                        i+=1

                        # Check the sequence of changes
                        end_of_loop = False
                        while i < len(diff_list) and not end_of_loop:
                            diff_line = diff_list[i]
                            # print(diff_line)
                            if diff_line[:2] == "+ ":
                                pluses.append(diff_line[2:])
                            elif diff_line[:2] == "- ":
                                minuses.append(diff_line[2:])
                            elif diff_line[:2] == "? ":
                                composed_text += pluses
                                end_of_loop = True
                            else:
                                end_of_loop = True
                                if (len(pluses) == 0 or len(minuses) == 0):
                                    composed_text += pluses
                                else:
                                    has_conflicts = True
                                    composed_text += self.__conflict_text(pluses, minuses)
                                composed_text.append(diff_line[2:])
                            i+=1

                        if not end_of_loop:
                            if (len(pluses) == 0 or len(minuses) == 0):
                                composed_text += pluses
                            else:
                                has_conflicts = True
                                composed_text += self.__conflict_text(pluses, minuses)

                print(''.join(composed_text))
                return (''.join(composed_text), has_conflicts)
        except Exception as e: 
            raise Exception("Error, cannot open comparison files: \n{}".format(e))

    def __conflict_text(self, pluses, minuses):
        composed_text = []
        new_changes_line = "\n>>>>>>>>>>>>>>>>> New changes +++\n"
        composed_text.append(new_changes_line)
        composed_text += pluses
        middle_line = "\n================= +++\n"
        composed_text.append(middle_line)
        composed_text += minuses
        old_changes_line = "\n<<<<<<<<<<<<<<<<< Old changes ---\n"
        composed_text.append(old_changes_line)
        return composed_text