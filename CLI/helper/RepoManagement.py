import os
import json
import shutil

from . import print_helper as ph
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
            ph.err("Error, there is not branch with name {}!".format(branch_name))
            return None

    def get_latest_commit(self, branch_name):
        '''
        Get the latest commit from a specific branch.
        '''
        for branch in self.__repo_config['branches'].values():
            if branch['name'] == branch_name:
                if len(branch['commits']) == 0:
                    return None
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
                branch_data = self.get_branch_data(branch)
                if not branch_data:
                    raise Exception(
                        "Error, couldn't get branch data while renaming the branch!")
                commits = self.__repo_config['branches'][f'{branch_data["id"]}']['commits']
                del commits[f'{commit_id}']
                self.__repo_config['branches'][f'{branch_data["id"]}']['commits'] = commits
                json.dump(self.__repo_config, f)
        except:
            raise Exception("Error, cannot open repo_config.json")
    
    def update_commits(self, new_commits, branch_id):
        try:
            with open(self.__repo_config_file, 'w') as f:
                commits = dict(self.get_repo_config()["branches"][f"{branch_id}"]["commits"])
                commits.update(new_commits)
                self.__repo_config['branches'][f"{branch_id}"]["commits"] = commits
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
                branch_data = self.get_branch_data(branch_name=old_name)
                if not branch_data:
                    raise Exception(
                        "Error, couldn't get branch data while renaming the branch!")
                branch_id = branch_data['id']
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
    
    def update_branches(self, new_branches):
        try:
            with open(self.__repo_config_file, 'w') as f:
                branches = dict(self.get_repo_config()["branches"])
                branches.update(new_branches)
                self.__repo_config['branches'] = branches
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

    def path_to_list(self, path):
        result = []
        try:
            for current_path, _, files in os.walk(path):
                for file in files:
                    new_item = os.path.join(current_path, file)
                    result.append(new_item.split(f'{path}')[1])
        except Exception as e:
            raise Exception(f"Error, wrong path, {e}")
        return result

    def get_largest_commit(self, commit1, commit2):
        t1 = datetime.strptime(commit1['date_created'], '%Y-%m-%dT%H:%M:%S.%fZ')
        t2 = datetime.strptime(commit2['date_created'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if t2 > t1:
            return commit2
        return commit1