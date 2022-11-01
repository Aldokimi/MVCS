import os

from helper import RepoManagement as RM
from helper import UserManagement as UM
from helper import print_helper   as ph

class diff():
    __repo_management, __config_folder, __user_mgt = None, None, None
    __file1, __file2 = None, None
    def __init__(self, args) -> None:

        self.__file1 = args.file1
        self.__file2 = args.file2

        self.__config_folder = os.path.join(os.path.join(os.getcwd()), ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)
        self.__user_mgt = UM.UserManagement(self.__config_folder)

        if not self.__file1:
            raise Exception('Error during running diff, wrong arguments!')

        if not self.__file2:
            self.__file2 = self.__get_file2()

        self.__preform_diff()

    def __get_file2(self):
        pass

    def __preform_diff(self):
        pass
            