import os
import json

from datetime import datetime

class RepoManagement():

    __repo_config = {}
    __repo_config_file  = ""

    def __init__(self, config_folder):
        '''
        Get the repo config data and store it in a dict.
        '''
        self.__repo_config_file = os.path.join(config_folder, "repo_config.json")
        try:
            with open(self.__repo_config_file, 'r') as f:
                self.__repo_config = json.load(f)
        except:
            raise Exception("Error, cannot open repo_config.json")

    def get_branch_data(self, branch_name):
        '''
        Get a specific branch data.
        '''
        for branch in self.__repo_config['branches']:
            if branch['name'] == branch_name:
                return branch
        raise Exception("Error, there is not branch with name{}!".format(branch_name))

    def get_latest_commit(self, branch_name):
        '''
        Get the latest commit from a specific branch.
        '''
        for branch in self.__repo_config['branches'].values():
            if branch['name'] == branch_name:
                latest_commit = list(branch['commits'].values())[0]
                for commit in branch['commits'].values():
                    t1 = datetime.strptime(latest_commit['date_created'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    t2 = datetime.strptime(commit['date_created'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    if t2 > t1:
                        latest_commit = commit
                return latest_commit

        raise Exception(f"Error, there is not branch with name {branch_name}!")

    def get_owner_data(self):
        return self.__repo_config['owner_data']

    def get_repo_config(self):
        return self.__repo_config

    def get_repo_config_file_path(self):
        return self.__repo_config_file
