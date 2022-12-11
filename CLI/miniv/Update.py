import json
import os
import subprocess

import requests

from helper import RepoManagement as RM
from helper import UserManagement as UM
from helper import print_helper as ph
from . import Commit


class update():
    __repo_management, __config_folder, __user_mgt = None, None, None

    def __init__(self, args) -> None:
        self.__config_folder = os.path.join(os.path.join(os.getcwd()), ".mvcs")
        try:
            self.__repo_management = RM.RepoManagement(self.__config_folder)
            self.__user_mgt = UM.UserManagement(self.__config_folder)
        except:
            ph.err(" You are not in a mvcs repository!")
            return

        # Get all repo data
        repo_name = self.__repo_management.get_repo_config()["name"]
        repo_owner = self.__repo_management.get_owner_data()["username"]
        headers = {
            "Authorization": f"Bearer {self.__user_mgt.get_user_data()['access_token']}",
        }
        response = requests.get(
            f'http://127.0.0.1:8000/api/v1/repos/data/{repo_owner}/{repo_name}/', headers=headers, )
        if response.status_code != 200:
            raise Exception("Error, requesting repo data failed")

        repo_data = json.loads(response.text)

        # Check for the new commits and branches and update them
        current_branches = self.__repo_management.get_repo_config()["branches"]
        new_branches = {
            k: v for k, v in repo_data["branches"].items() if k not in current_branches}

        clone_url = self.__user_mgt.get_user_data()["clone_url"]
        current_branch = self.__user_mgt.get_user_data()["current_branch"]

        for branch_id in current_branches:
            if branch_id in repo_data["branches"]:
                commits = current_branches[branch_id]["commits"]

                new_commits = {
                    k: v for k, v in repo_data["branches"][branch_id]["commits"].items()
                    if k not in commits
                }

                # Update the commits in the repo_config.json
                self.__repo_management.update_commits(new_commits, branch_id)

                # Download the commits into their branch
                for _, commit in new_commits.items():
                    try:
                        branch_name = repo_data["branches"][branch_id]["name"]
                        commit_unique_id = commit["unique_id"]
                        compressed_file = f'{branch_name}/{commit_unique_id}.tar.xz'
                        p = subprocess.run([
                            'scp',
                            f'{clone_url}/{current_branches[branch_id]["name"]}/{compressed_file}'
                            f'{self.__config_folder}/{current_branch}',
                        ])
                        if p.returncode != 0:
                            raise Exception(
                                "Error, Downloading repo data failed!")
                    except subprocess.CalledProcessError or p.returncode != 0:
                        raise Exception("Error, wrong clone URL!")

        # Download the new branch
        for branch_id in new_branches:
            try:
                branch_name = new_branches[branch_id]["name"]
                print(branch_name)
                p = subprocess.run(
                    [
                        'scp', '-r',
                        f'{clone_url}/{branch_name}/',
                        f'{self.__config_folder}'
                    ]
                )
                if p.returncode != 0:
                    raise Exception("Error, Downloading repo data failed!")
            except subprocess.CalledProcessError or p.returncode != 0:
                raise Exception("Error, wrong clone URL!")

        # Update the branches in the repo config
        branches = {**current_branches, **new_branches}
        self.__repo_management.update_branches(branches)

        # Extract the last commit to the working directory
        Commit.update_repository(
            self.__config_folder,
            self.__repo_management,
            self.__user_mgt,
            self.__get_last_commit()
        )

        ph.ok(" Updated the repository successfully!")

    def __get_last_commit(self):
        branch_name = self.__user_mgt.get_user_data()["current_branch"]
        _, commit_a = self.__user_mgt.get_last_new_commit(
            self.__repo_management.get_branch_data(branch_name)["id"]
        )
        commit_b = self.__repo_management.get_latest_commit(branch_name)
        commit = self.__repo_management.get_largest_commit(commit_a, commit_b)
        return commit
