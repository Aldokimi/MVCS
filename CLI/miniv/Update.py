import os
import subprocess

import requests

from helper import RepoManagement as RM
from helper import UserManagement as UM
from helper import print_helper   as ph
from Commit import update_repository

class update():
    __repo_management, __config_folder, __user_mgt = None, None, None

    def __init__(self, args) -> None:
        self.__config_folder = os.path.join(os.path.join(os.getcwd()), ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)
        self.__user_mgt = UM.UserManagement(self.__config_folder)

        # Get all repo data
        repo_name = self.__repo_management.get_repo_config()["name"]
        repo_owner= self.__repo_management.get_owner_data()["name"]
        repo_data = requests.get(f'http://127.0.0.1:8000/api/repos/data/{repo_owner}/{repo_name}/')
        if repo_data.status_code != 200:
            raise Exception("Error, requesting repo data failed")

        # Check for the new commits and branches and update them
        current_branches = self.__repo_management.get_repo_config()["branches"]
        new_branches = { k : v for k,v in repo_data["branches"].items() if k not in current_branches }

        for branch_id in current_branches:
            if branch_id in repo_data["branches"]:
                commits = current_branches[branch_id]["commits"]
                
                new_commits = { 
                    k : v for k,v in repo_data["branches"][branch_id]["commits"].items() 
                        if k not in commits 
                }
                self.__repo_management.update_commits(new_commits, branch_id)

                # Download the commits into their branch
                for _, commit in commits.items():
                    try:
                        compressed_file = f'{repo_data["branches"][branch_id]["name"]}/{commit["unique_id"]}.tar.xz'
                        current_branch = self.__user_mgt.get_user_data()["current_branch"]
                        p = subprocess.run([
                            'scp', 
                            '-r',
                            f'{self.__user_mgt.get_user_data["clone_url"]}/{current_branch}/{compressed_file}'
                            f'{self.__config_folder}/{current_branch}',
                        ])
                        if p.returncode != 0 :
                            raise Exception("Error, Downloading repo data failed!")
                    except subprocess.CalledProcessError or p.returncode != 0:
                        raise Exception("Error, wrong clone URL!")

        # Download the new branch
        for branch_id in new_branches:
            try:
                branch_name = new_branches[branch_id]["name"]
                p = subprocess.run([
                    'scp', 
                    '-r',
                    f'{self.__user_mgt.get_user_data["clone_url"]}/{branch_name}'
                    f'{self.__config_folder}',
                ])
                if p.returncode != 0 :
                    raise Exception("Error, Downloading repo data failed!")
            except subprocess.CalledProcessError or p.returncode != 0:
                raise Exception("Error, wrong clone URL!")


        # Update the branches in the repo config
        branches = dict(current_branches.items() + new_branches.items())
        self.__repo_management.update_branches(branches)

        # Extract the last commit to the working directory
        update_repository(
            self.__config_folder, 
            self.__repo_management, 
            self.__user_mgt, 
            self.__get_last_commit
        )

    def __get_last_commit(self):
        (commit_internal_id, _) = self.__repo_management.get_latest_commit()
        if commit_internal_id == 0:
            return None
        return self.__repo_management.get_latest_commit(self.__user_mgt.get_user_data()["current_branch"])
