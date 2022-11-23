import os
import shutil
import tarfile

import requests

from . import Repository
from . import Diff

from helper import RepoManagement as RM
from helper import UserManagement as UM
from helper import print_helper   as ph

class branch():
    __list, __create, __delete, __edit\
         = None, None, None, None
    __repo_management, __config_folder, __user_mgt = None, None, None

    def __init__(self, args) -> None:
        self.__list   = args.list
        self.__create = args.create_b
        self.__delete = args.delete_b
        self.__edit   = args.rename_b
        self.__get_current = args.current

        self.__config_folder = os.path.join(os.path.join(os.getcwd()), ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)
        self.__user_mgt = UM.UserManagement(self.__config_folder)

        if self.  __list:
            self. __list_branches()
        elif self.__create:
            self.__create = str(self.__create[0])
            self. __create_branch()
        elif self.__delete:
            self.__delete = str(self.__delete[0])
            self. __delete_branch()
        elif self.__edit:
            self.__edit = str(self.__edit[0])
            self. __edit_branch()
        elif self.__get_current:
            ph.ok("  Current branch is <" + self.__user_mgt.get_user_data()["current_branch"] + ">")
        else:
            ph.err("wrong command")

    def __list_branches(self):
        branches = self.__repo_management.get_repo_config()['branches']
        result = " Those are the current branches: \n"
        for branch in branches:
            branch_name = branches[branch]['name']
            num_commits = len(branches[branch]["commits"])
            result+=f"{branch_name}: has {num_commits} commits\n"
        ph.ok(" " + result[:-1])

    def __create_branch(self):
        # Create the new branch folder
        new_branch_folder = os.path.join(self.__config_folder, self.__create)
        try:
            os.mkdir(new_branch_folder, mode=0o777)
        except Exception as e:
            ph.err(f"Error, there is already a branch with name {self.__create}")
            return
        
        # Copy the last commit from main to the new branch
        last_commit_id = self.__repo_management.get_latest_commit('main')['unique_id']
        try:
            shutil.copy2(
                os.path.join(self.__config_folder, f"main{os.sep}{last_commit_id}.tar.xz"),
                new_branch_folder
            )
        except Exception as e:
            shutil.rmtree(new_branch_folder)
            raise Exception("Error, cannot create a new directory for the branch!")

        # Update the value of the current branch in the 
        self.__user_mgt.update_current_branch(self.__create)

        # Create branch through the API
        branch_data = self.__operate_branch_on_API('post', branch_name=self.__create)

        # Create branch in the repo_config.json and in the API
        if branch_data.status_code == 201:
            self.__repo_management.create_branch(branch_data.json())
        else:
            raise Exception('Error, cannot create a branch in the API side!')

    def __delete_branch(self):

        # Check if the branch is main
        if self.__user_mgt.is_in_main():
            raise Exception("Error, you cannot delete the main branch")

        # Delete the branch folder and its content
        branch_folder = os.path.join(
            self.__config_folder, 
            self.__user_mgt.get_user_data()['current_branch']
        )
        shutil.rmtree(branch_folder)

        # Checkout to the main branch
        checkOut("main", self.__config_folder, self.__repo_management, self.__user_mgt)

        # Delete a branch in the API
        branch_data = self.__repo_management.get_branch_data(
            branch_name=self.__user_mgt.get_user_data()['current_branch']
        )
        if not branch_data:
            raise Exception(
                "Error, couldn't get branch data while renaming the branch!")
        self.__operate_branch_on_API(
            'delete', 
            branch_id=branch_data['id'], 
            branch_name=branch_data['name'],
        )

        # Delete a branch in repo_config.json
        self.__repo_management.delete_branch(branch_data=branch_data)

    def __edit_branch(self):
        branch_data = self.__repo_management.get_branch_data(
            branch_name=self.__user_mgt.get_user_data()['current_branch']
        )
        if not branch_data:
            raise Exception(
                "Error, couldn't get branch data while renaming the branch!")

        # Rename the current branch in the user_config.json
        self.__user_mgt.update_current_branch(self.__edit)

        # Rename a branch in the repo_config.json
        self.__repo_management.rename_branch(branch_data['name'], self.__edit)

        # Rename a branch in the API
        response  = self.__operate_branch_on_API(
            'put', 
            branch_id=branch_data['id'], 
            branch_name=branch_data['name'], 
            new_branch_name=self.__edit
        )
        if response.status_code != 200:
            raise Exception('Error, cannot rename a branch in the API side!')

    def __operate_branch_on_API(self, method, branch_id=None, branch_name=None, new_branch_name=None):
        '''
        Create, delete, or edit a branch inside the repo_config.json and in the API.
        '''
        API_end_point = 'http://127.0.0.1:8000/api/branches/' if method == 'post'\
             else 'http://127.0.0.1:8000/api/branches/' + f'{branch_id}/'
    
        data = {
            "repo": self.__repo_management.get_repo_config()['id'],
            "name": branch_name if not new_branch_name else new_branch_name,
        }
        
        headers={
            "Authorization": f"Bearer {self.__user_mgt.get_user_data()['access_token']}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = None
        if method == 'post':
            response = requests.post(API_end_point, json = data, headers=headers, )
        elif method == 'put':
            response = requests.put(API_end_point, json = data, headers=headers, )
        elif method == 'delete':
            response = requests.delete(API_end_point, json = data, headers=headers, )
        else:
            raise Exception('Error, cannot create a request on branches in the API!')

        return response


def checkOut(branch_name, config_folder, repo_management, user_management):
    if not branch_name:
        raise Exception("Error, branch name is not passed!")

    try:
        # Check if we are checking out to the same branch
        if branch_name == user_management.get_user_data()['current_branch']:
            ph.err('Error, cannot checkout to the same branch')
            return

        # Trying to get the branch, so if the branch doesn't exists and exception will be raised here
        branch_data = repo_management.get_branch_data(branch_name=branch_name)
        if not branch_data:
            raise Exception(
                "Error, couldn't get branch data while renaming the branch!")

        # Check if we have un committed changes on the current directory
        diffs, new_files = Diff.diff_repo(config_folder, repo_management, user_management)
        if diffs or len(new_files) != 0:
            ph.err("Error, you have uncommitted changes, please commit your changes first!")
            return

        # Delete the working dir and update the current branch in the user_config.json
        repo_management.delete_working_directory()
        user_management.update_current_branch(branch_name)
        
        # Move the files from the last commit ot the working directory
        branch_commits = branch_data["commits"]
        if len(branch_commits) != 0:
            last_commit_id = repo_management.get_latest_commit(branch_name)["unique_id"]
            
            branch_data = repo_management.get_branch_data(
                branch_name=user_management.get_user_data()["current_branch"])
            if not branch_data: return
            branch_id = branch_data["id"]

            last_commit_id, last_commit = user_management.get_last_new_commit(branch_id)
            if last_commit_id == 0:
                last_commit_id = repo_management.get_latest_commit(
                    user_management.get_user_data()["current_branch"])["unique_id"]
            else:
                last_commit_id = last_commit["unique_id"]

            branch_folder = os.path.join(config_folder, user_management.get_user_data()["current_branch"])
            commit_folder = os.path.join(branch_folder, f'{last_commit_id}.tar.xz')
            working_dir = config_folder.split('.mvcs')[0]
            
            # Extract the last commit file on main into the working directory
            if Repository.repo.is_nonempty_tar_file(commit_folder):
                try:
                    with tarfile.open(commit_folder) as ccf:
                        ccf.extractall(working_dir)
                except Exception as e:
                    raise Exception(e)

        ph.ok(f" Checked out to {branch_name}!")
    except Exception as e:
        raise Exception(f"{e}")
