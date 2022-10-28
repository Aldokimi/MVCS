import os
import tarfile
import uuid

from helper import RepoManagement as RM
from helper import UserManagement as UM
from helper import print_helper   as ph

class upload():
    __repo_management, __config_folder, __user_mgt = None, None, None

    def __init__(self, args) -> None:
        self.__branch   = args.branch

        self.__config_folder = os.path.join(os.path.join(os.getcwd()), ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)
        self.__user_mgt = UM.UserManagement(self.__config_folder)

        '''
        # Now we need to preform a scp command to upload the commit files from a branch 
        '''
