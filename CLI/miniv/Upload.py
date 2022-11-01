import os
import subprocess

from helper import RepoManagement as RM
from helper import UserManagement as UM
from helper import print_helper   as ph

class upload():
    __repo_management, __config_folder, __user_mgt = None, None, None

    def __init__(self, args) -> None:
        self.__config_folder = os.path.join(os.path.join(os.getcwd()), ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)
        self.__user_mgt = UM.UserManagement(self.__config_folder)

        username = self.__repo_management.get_owner_data()['username']
        repo_name = self.__repo_management.get_repo_config()['name']
        branch_name = self.__user_mgt.get_user_data()['current_branch']

        self.__upload_url = f'mvcs@172.31.238.112:~/{username}/{repo_name}/{branch_name}'

        '''
        # Now we need to preform a scp command to upload the commit files from a branch 
        '''
        branch_folder = os.path.join(self.__config_folder, self.__user_mgt.get_user_data()['current_branch'])
        for file in os.listdir(branch_folder):
            try:
                print(self.__upload_url[:-2])
                p = subprocess.run(['scp', os.path.join(branch_folder, file), f'{self.__upload_url}/'])
                if p.returncode != 0 :
                    raise Exception("Error, uploading repo data failed!")
            except subprocess.CalledProcessError or p.returncode != 0:
                raise Exception("Error, wrong clone URL!")
