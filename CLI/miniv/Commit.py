import os
import shutil
import uuid
import lzma
import tarfile
from . import Repository
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

def undo(config_folder, repo_management, user_management):
    if len(user_management.get_user_data()["new_commits"]) == 1:
        ## Remove the last commit remotely
        # Delete the commit from the API
        last_commit = repo_management.get_latest_commit(
                user_management.get_user_data()["current_branch"]
            )
        API_end_point = 'http://127.0.0.1:8000/api/commits/' + f'{last_commit["id"]}/'
        
        headers={
            "Authorization": f"Bearer {user_management.get_user_data()['access_token']}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        commit_data = {
            "message": last_commit["message"],
            "branch": last_commit["id"],
            "committer": last_commit["committer"],
            "unique_id": last_commit["unique_id"]
        }

        response = requests.delete(API_end_point, json = commit_data, headers=headers, )
        if response.status_code == 204:
            # Delete the commit form configuration
            current_branch = user_management.get_user_data()["current_branch"]
            repo_management.delete_commit(current_branch, last_commit["id"])
        else:
            raise Exception("Error, couldn't delete the commit from the API")

        # Update the repository
        update_repository(config_folder, repo_management, user_management)
    else:
        ## Remove the last commit locally
        # Delete the commit from the configuration
        (internal_id, commit_data) = user_management.get_last_new_commit()
        user_management.delete_new_commit(internal_id)
        commit_unique_id = commit_data["unique_id"]
        commit_file_name = os.path.join(
            config_folder, 
            user_management.get_user_data()["current_branch"] + f"/{commit_unique_id}.tar.xz"
        )
        os.remove(commit_file_name)

        # Update the repository
        update_repository(config_folder, repo_management, user_management)

def update_repository(config_folder, repo_management, user_management, get_last_commit=None):
    # Delete the working directory
    repo_management.delete_working_directory()

    # Extract the last commit 
    if not get_last_commit:
        commit_data = user_management.get_last_new_commit()[1]
    else:
        commit_date = get_last_commit()
    commit_unique_id = commit_data["unique_id"]
    commit_file_name = os.path.join(
        config_folder, 
        user_management.get_user_data()["current_branch"] + f"/{commit_unique_id}.tar.xz"
    )
    working_dir = config_folder.split('.mvcs')[0]
    if Repository.repo.is_nonempty_tar_file(commit_file_name):
        with tarfile.open(commit_file_name) as ccf:
            ccf.extractall(working_dir)
            try:
                path = os.path.join(working_dir, os.listdir(working_dir)[1])
                for filename in os.listdir(path):
                    shutil.move(os.path.join(path, filename), os.path.join(working_dir, filename))
                os.rmdir(path)
            except Exception:
                raise Exception("Error happened during downloading the repo!")
