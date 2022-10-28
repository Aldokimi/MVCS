import os
import tarfile
import uuid

from helper import RepoManagement as RM
from helper import UserManagement as UM
from helper import print_helper   as ph

class status():
    __repo_management, __config_folder, __user_mgt = None, None, None

    def __init__(self, args) -> None:
        self.__branch   = args.branch

        self.__config_folder = os.path.join(os.path.join(os.getcwd()), ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)
        self.__user_mgt = UM.UserManagement(self.__config_folder)

        '''
        # Now we need to check for every file in the working directory 
        # if there is a difference between it and the files inside the last commit in the main
        '''

         # Move the files from the last commit ot the working directory
        commit_folder = self.__repo_management.get_latest_commit(self.__user_mgt.get_user_data()['current_branch'])
        working_dir = self.__config_folder.split('.mvcs')[0]

        # Create a test path
        test_path = os.path.join(self.__config_folder, f'test_status_folder_{uuid.uuid4().hex}')
        os.mkdir(test_path, mode=0o755)

        # Extract the last commit file on main into the working directory
        with tarfile.open(commit_folder) as ccf:
            ccf.extractall(test_path)
            
            try:
                # Check if the extraction was successful
                last_commit_id = self.__repo_management.get_latest_commit('main')['unique_id']
                extract_commit_folder = os.path.join(test_path, last_commit_id)
                if not os.path.exists(extract_commit_folder):
                    raise Exception("Error, couldn't extract the last commit into the test directory!")

                # Compare all the files in the test directory and the working directory 
                for filename in zip(
                    os.listdir(extract_commit_folder), 
                    filter(lambda file: file != ".mvcs", os.listdir(working_dir))
                ):
                    pass

            except Exception:
                raise Exception("Error happened during extracting the repo!")
