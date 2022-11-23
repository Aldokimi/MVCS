import os
from . import Diff

from helper import RepoManagement as RM
from helper import UserManagement as UM
from helper import print_helper   as ph

class status():
    __repo_management, __config_folder, __user_mgt = None, None, None

    def __init__(self, args) -> None:
        self.__config_folder = os.path.join(os.path.join(os.getcwd()), ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)
        self.__user_mgt = UM.UserManagement(self.__config_folder)

        diff, new_files = Diff.diff_repo(self.__config_folder, self.__repo_management, self.__user_mgt)
        if not diff and len(new_files) == 0:
            ph.ok(" Nothing is changed!")

        if diff:
            print("")
            ph.msg(ph.yellow("Changed files: "))
            for changed_file in diff.keys():
                print("  ➜ ", changed_file)
        
        if new_files:
            print("")
            ph.msg(ph.red("New files: "))
            for file in new_files:
                print("  ➜ ", file)
