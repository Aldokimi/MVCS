import os
import subprocess
import requests

from . import Diff

from helper import RepoManagement as RM
from helper import UserManagement as UM
from helper import print_helper as ph


class upload():
    __repo_management, __config_folder, __user_mgt = None, None, None

    def __init__(self, args) -> None:
        self.__config_folder = os.path.join(os.path.join(os.getcwd()), ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)
        self.__user_mgt = UM.UserManagement(self.__config_folder)
        self.__upload_url = f'{self.__user_mgt.get_user_data()["clone_url"]}'
        self.__upload_branches = {}

        # Check if we have SSH connection
        user = self.__upload_url.split('@')[0]
        host = self.__upload_url.split('@')[1].rsplit(':', 1)[0]
        if not self.__user_mgt.check_ssh(host=host, user=user, port=8008):
            ph.err("You don't have SSH authority to upload to this repository!")
            return

        # Check if we have un committed changes on the current directory
        diffs, new_files = Diff.diff_repo(
            self.__config_folder, self.__repo_management, self.__user_mgt)
        if diffs or len(new_files) != 0:
            ph.err(
                "Error, you have uncommitted changes, please commit your changes first!")
            return

        # Create commits in the repo config file and in the API
        new_commits = self.__user_mgt.get_user_data()['new_commits']
        del new_commits["0"]

        for commit_internal_id in new_commits:
            commit_data = new_commits[commit_internal_id]

            # Add the commit to the upload branches
            branch = self.__repo_management.get_branch_data(
                branch_id=commit_data["branch"])
            branch_name = branch["name"]

            if not branch_name in self.__upload_branches:
                self.__upload_branches[branch_name] = []
            self.__upload_branches[branch_name].append(commit_data)

            if "amend" in commit_data:
                del commit_data["amend"]

                response = self.__apply_commit_on_API(
                    "put",
                    commit_data,
                    self.__repo_management.get_latest_commit(
                        branch_name=branch_name)['id']
                )

                if response and response.status_code == 200:
                    commit_id = self.__repo_management.get_latest_commit(
                        branch_name=branch_name)['id']
                    commit_data = response.json()
                    self.__repo_management.modify_commit(
                        commit_data, commit_id)
                else:
                    raise Exception(
                        'Error, cannot create a put commit request to the API,'
                        f' response code {response.status_code}!')

            else:  # If this is a normal commit and not amend commit
                response = self.__apply_commit_on_API("post", commit_data)
                if response and response.status_code == 201:
                    self.__repo_management.create_commit(response.json())
                else:
                    raise Exception(
                        'Error, cannot create a post commit request to the API'
                        f' response code {response.status_code}!')

        # Preform a scp command to upload the commit files from a branch 
        for branch_name, commits in self.__upload_branches.items():
            branch_folder = os.path.join(self.__config_folder, branch_name)
            for commit in commits:
                commit_file = os.path.join(
                    branch_folder, f'{commit["unique_id"]}.tar.xz')
                try:
                    p = subprocess.run([
                        'scp', '-P', '8008', commit_file,
                        f'{self.__upload_url}/{branch_name}/'
                    ])
                    if p.returncode != 0:
                        raise Exception(
                            "Error, uploading repo data failed!")
                except subprocess.CalledProcessError:
                    raise Exception("Error, wrong clone URL!")

        # Reset the current configuration
        self.__user_mgt.reset_new_commits(branch_folder)

        ph.ok(" Uploaded changes successfully!")

    def __apply_commit_on_API(self, method, commit_data, commit_id=None):
        '''
        Create a commit inside the repo_config.json and in the backend
        '''
        API_end_point = 'http://127.0.0.1:8000/api/v1/commits/' if method == 'post'\
            else 'http://127.0.0.1:8000/api/v1/commits/' + f'{commit_id}/'

        headers = {
            "Authorization": f"Bearer {self.__user_mgt.get_user_data()['access_token']}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = None
        if method == 'post':
            response = requests.post(
                API_end_point, json=commit_data, headers=headers, )
        elif method == 'put':
            response = requests.put(
                API_end_point, json=commit_data, headers=headers, )
        else:
            raise Exception(
                f'Error, cannot updated the commit, response code {response.status_code}!')

        return response
