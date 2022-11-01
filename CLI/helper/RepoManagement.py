import os
import json
import shutil

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

    def get_branch_data(self, branch_name=None, branch_id=None):
        '''
        Get a specific branch data.
        '''
        target_branch = None if not branch_id else self.__repo_config['branches'][f'{branch_id}']
        if target_branch:
            return target_branch

        found = False
        for branch in self.__repo_config['branches']:
            branch = self.__repo_config['branches'][branch]
            if branch['name'] == branch_name: 
                found = True
                target_branch = branch
        if found:
            return target_branch
        else:
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

    def create_commit(self, commit_data):
        self.__operate_commit(commit_data['id'], commit_data)

    def modify_commit(self, commit_data, commit_id):
        self.__operate_commit(commit_id, commit_data)

    def delete_commit(self, branch, commit_id):
        try:
            with open(self.__repo_config_file, 'w') as f:
                commits = self.__repo_config['branches'][f'{branch}']['commits']
                del commits[f'{commit_id}']
                self.__repo_config['branches'][f'{branch}']['commits'] = commits
                json.dump(self.__repo_config, f)
        except:
            raise Exception("Error, cannot open repo_config.json")

    def __operate_commit(self, commit_id, commit_data):
        try:
            with open(self.__repo_config_file, 'w') as f:
                branch_id = commit_data['branch']
                self.__repo_config['branches'][f'{branch_id}']['commits'][f'{commit_id}'] = commit_data
                json.dump(self.__repo_config, f)
        except:
            raise Exception("Error, cannot open repo_config.json")

    def create_branch(self, branch_data):
        try:
            with open(self.__repo_config_file, 'w') as f:
                branch_id = branch_data['id']
                self.__repo_config['branches'][f'{branch_id}'] = branch_data
                last_commit = self.get_latest_commit('main')
                last_commit_id = self.get_latest_commit('main')['id']
                self.__repo_config['branches'][f'{branch_id}']['commits'] = {f'{last_commit_id}': last_commit}
                json.dump(self.__repo_config, f)
        except:
            raise Exception("Error, cannot open repo_config.json")

    def rename_branch(self, old_name, new_name):
        try:
            with open(self.__repo_config_file, 'w') as f:
                branch_id = self.get_branch_data(branch_name=old_name)['id']
                self.__repo_config['branches'][f'{branch_id}']['name'] = new_name
                json.dump(self.__repo_config, f)
        except:
            raise Exception("Error, cannot open repo_config.json")

    def delete_branch(self, branch_data):
        try:
            with open(self.__repo_config_file, 'w') as f:
                branch_id = branch_data['id']
                del self.__repo_config['branches'][f'{branch_id}']
                json.dump(self.__repo_config, f)
        except:
            raise Exception("Error, cannot open repo_config.json")

    def delete_working_directory(self):
        for file_name in os.listdir(os.getcwd()):
            if file_name != '.mvcs':
                if os.path.isfile(file_name):
                    os.remove(file_name)
                else:
                    shutil.rmtree(os.path.join(os.getcwd(), file_name))
