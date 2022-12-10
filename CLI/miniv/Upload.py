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

        username = self.__repo_management.get_owner_data()['username']
        repo_name = self.__repo_management.get_repo_config()['name']
        branch_name = self.__user_mgt.get_user_data()['current_branch']

        self.__upload_url = f'{self.__user_mgt.get_user_data()["clone_url"]}/{branch_name}'

        # Check if we have un committed changes on the current directory
        # diffs, new_files = Diff.diff_repo(
        #     self.__config_folder, self.__repo_management, self.__user_mgt)
        # if diffs or len(new_files) != 0:
        #     ph.err("Error, you have uncommitted changes, please commit your changes first!")
        #     return

        '''
        Create commits in the repo config file and in the API
        '''
        new_commits = self.__user_mgt.get_user_data()['new_commits']
        initial_commit = new_commits["0"]["unique_id"]
        print()
        del new_commits["0"]

        for commit_internal_id in new_commits:
            commit_data = new_commits[commit_internal_id]
            if "amend" in commit_data:
                del commit_data["amend"]

                response = self.__apply_commit_on_API(
                    "put",
                    commit_data,
                    self.__repo_management.get_latest_commit('main')['id']
                )

                if response and response.status_code == 200:
                    commit_data = response.json()
                    commit_id = self.__repo_management.get_latest_commit('main')[
                        'id']
                    self.__repo_management.modify_commit(
                        commit_data, commit_id)
                else:
                    raise Exception(
                        'Error, cannot create a put commit request to the API,'
                        f' response code {response.status_code}!')
            else:
                response = self.__apply_commit_on_API("post", commit_data)
                if response and response.status_code == 201:
                    self.__repo_management.create_commit(response.json())
                else:
                    raise Exception(
                        'Error, cannot create a post commit request to the API'
                        f' response code {response.status_code}!')

            '''
            # Now we need to preform a scp command to upload the commit files from a branch 
            '''
            branch_folder = os.path.join(
                self.__config_folder,
                self.__repo_management.get_branch_data(
                    branch_id=commit_data["branch"])['name']
            )

            for file in os.listdir(branch_folder):
                if file.split(".")[0] != initial_commit:
                    try:
                        p = subprocess.run([
                            'scp', '-r',
                            os.path.join(branch_folder, file),
                            f'{self.__upload_url}'
                        ])
                        if p.returncode != 0:
                            raise Exception(
                                "Error, uploading repo data failed!")
                    except subprocess.CalledProcessError as e:
                        print(e)
                        raise Exception("Error, wrong clone URL!")

            # Reset the current configuration
            self.__user_mgt.reset_new_commits(branch_folder)

        ph.ok(" Uploaded changes successfully!")

    def __get_last_commit(self, branch=None):
        branch_name = branch if branch else self.__user_mgt.get_user_data()[
            "current_branch"]
        _, commit_a = self.__user_mgt.get_last_new_commit(
            self.__repo_management.get_branch_data(branch_name)["id"]
        )
        commit_b = self.__repo_management.get_latest_commit(branch_name)
        commit = self.__repo_management.get_largest_commit(commit_a, commit_b)
        return commit

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
