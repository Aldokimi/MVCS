import os
import shutil
import uuid
import lzma
import tarfile
import requests

from helper import RepoManagement as RM
from helper import UserManagement as UM
from helper import print_helper   as ph

class commit():
    __list, __info, __commit_message, __amend\
         = None, None, None, None
    __repo_management, __config_folder, __user_mgt = None, None, None

    def __init__(self, args) -> None:
        self.__list   = args.list
        self.__info   = args.info
        self.__commit_message = args.create
        self.__amend  = args.amend

        repo_path = os.path.join(os.getcwd())
        self.__config_folder = os.path.join(repo_path, ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)
        self.__user_mgt = UM.UserManagement(self.__config_folder)

        if self.  __list:
            self. __list_commits()
        elif self.__info:
            self. __show_info()
        elif self.__commit_message:
            self. __commit_message_commit()
        elif self.__amend:
            self. __amend_commit()

    def __list_commits(self):
        branch_data = self.__repo_management.get_branch_data("main")
        for commit in branch_data['commits']:
            print(branch_data['commits'][commit])

    def __show_info(self):
        branch_data = self.__repo_management.get_branch_data("main")
        print(branch_data['name'])

    def __create_commit_folder(self):
        '''
        # Collect all files and folders
        '''
        files = []
        for file in os.listdir(os.getcwd()):
            if file != '.mvcs':
                files.append(file)
        '''
        # Compress the files and folders and uploading to the config dir
        '''
        commit_unique_id = uuid.uuid4().hex
        commit_file_name = f'{commit_unique_id}.tar.xz'
        xz_file = lzma.LZMAFile(commit_file_name, mode='w')
        with tarfile.open(mode='w', fileobj=xz_file) as tar_xz_file:
            for file in files:
                tar_xz_file.add(file)
        xz_file.close()

        shutil.copy2(commit_file_name, os.path.join(self.__config_folder, "main"))
        os.remove(commit_file_name)

        return commit_unique_id

    def __apply_commit_on_API(self, method, commit_unique_id, commit_id=None, new_message=None):
        '''
        # Create a commit inside the repo_config.json and in the backend
        '''
        API_end_point = 'http://127.0.0.1:8000/api/commits/' if method == 'post'\
             else 'http://127.0.0.1:8000/api/commits/' + f'{commit_id}/'
        commit_message = self.__repo_management.get_latest_commit('main')['message']
        if method == 'put' and new_message != None:
            commit_message = new_message
    
        data = {
            "message": commit_message,
            "branch" : self.__repo_management.get_branch_data('main')['id'],
            "committer": self.__user_mgt.get_user_data()['id'],
            "unique_id": commit_unique_id
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
        else:
            raise Exception('Error, cannot updated the commit!')

        return response

    def __commit_message_commit(self):
        commit_unique_id = self.__create_commit_folder()
        branch_id = self.__repo_management.get_branch_data(
            self.__user_mgt.get_user_data()['current_branch'])['id']
        committer = self.__repo_management.get_owner_data()['id']

        commit_data = {
            "message": self.__commit_message,
            "branch": int(branch_id),
            "committer": int(committer),
            "unique_id": commit_unique_id
        }

        last_new_commit_id = self.__user_mgt.get_last_new_commit()[0]
        self.__user_mgt.add_new_commit(int(last_new_commit_id) + 1, commit_data)
        # response = self.__apply_commit_on_API("post", commit_unique_id)

        # if response and response.status_code == 201:
        #     self.__repo_management.create_commit(response.json())
        # else:
        #     raise Exception('Error, cannot create a commit request to the API!')

    def __amend_commit(self):
        '''
        To amend a commit we will have to detect the changes,\n
        then changes the API and the CLI storage accordingly
        '''
        ph.warn("Do you want to change the commit message? (Y/n)")
        answer = input("\t\t\t\n")
        new_message = None
        if answer == 'Y' or answer == 'y' or answer == 'Yes' or answer == 'yes':
            new_message = str(input('Enter the new commit message: '))

        commit_unique_id = self.__create_commit_folder()
        branch_id = self.__repo_management.get_branch_data(
            self.__user_mgt.get_user_data()['current_branch'])['id']
        committer = self.__repo_management.get_owner_data()['id']

        commit_data = {
            "amend": True,
            "message": new_message if new_message else\
                self.__user_mgt.get_last_new_commit()[1]['message'],
            "branch": int(branch_id),
            "committer": int(committer),
            "unique_id": commit_unique_id
        }

        last_new_commit_id = self.__user_mgt.get_last_new_commit()[0]

        if len(self.__user_mgt.get_user_data()['new_commits']) == 1:
            self.__user_mgt.add_new_commit(int(last_new_commit_id) + 1, commit_data)
        else:
            self.__user_mgt.modify_new_commit(last_new_commit_id, commit_data)
        # commit_unique_id = self.__create_commit_folder()
        # response = self.__apply_commit_on_API(
        #     "put", 
        #     commit_unique_id, 
        #     self.__repo_management.get_latest_commit('main')['id'],
        #     new_message
        # )
        
        # if response and response.status_code == 200:
        #     commit_data = response.json()
        #     commit_id = self.__repo_management.get_latest_commit('main')['id']
        #     self.__repo_management.modify_commit(commit_data, commit_id)
        # else:
        #     raise Exception('Error, cannot create a commit request to the API!')
