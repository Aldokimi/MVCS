import datetime
import os
import shutil
import uuid
import lzma
import tarfile

from . import Diff
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
        if not branch_data:
            raise Exception(
                "Error, couldn't get branch data while renaming the branch!")
        commits = "  All commits in this branch are:\n"
        for commit in branch_data['commits']:
            commits += f"ID: {branch_data['commits'][commit]['id']},     "\
                f"Unique ID: {branch_data['commits'][commit]['unique_id']}\n"
        ph.ok(" " + commits[:-1])

    def __show_info(self):
        branch_data = self.__repo_management.get_branch_data("main")
        if not branch_data:
            raise Exception(
                "Error, couldn't get branch data while renaming the branch!")
        commit = branch_data['commits'][self.__info]
        info =f"     Info of the commit with ID {self.__info}\n"
        for (k, v) in commit.items():
            branch_data = self.__repo_management.get_branch_data(branch_id=v)
            if not branch_data:
                raise Exception(
                    "Error, couldn't get branch data while renaming the branch!")
            if k == "branch":
                info+=f"{k}:     {branch_data['name']}\n"
            else:
                info+=f"{k}:  {v}\n"
        ph.ok(" " + info)

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

        shutil.copy2(
            commit_file_name, 
            os.path.join(
                self.__config_folder, 
                self.__user_mgt.get_user_data()["current_branch"]
            ))
            
        os.chmod(os.path.join(
                self.__config_folder, 
                f'{self.__user_mgt.get_user_data()["current_branch"]}/{commit_file_name}'
            ), 0o777)
        os.remove(commit_file_name)

        return commit_unique_id

    def __commit_message_commit(self):
        # Check if we have un committed changes on the current directory
        diffs, new_files = Diff.diff_repo(
            self.__config_folder, self.__repo_management, self.__user_mgt)
        if not diffs and len(new_files) == 0:
            ph.err("You have nothing changed to commit!")
            return

        commit_unique_id = self.__create_commit_folder()
        branch_data = self.__repo_management.get_branch_data(
            self.__user_mgt.get_user_data()['current_branch'])

        if not branch_data:
            raise Exception(
                "Error, couldn't get branch data while renaming the branch!")
                
        branch_id = branch_data['id']
        committer = self.__repo_management.get_owner_data()['id']

        commit_data = {
            "message": self.__commit_message,
            "branch": int(branch_id),
            "committer": int(committer),
            "unique_id": commit_unique_id,
            "date_created": str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        }

        last_new_commit_id = self.__user_mgt.get_last_new_commit()[0]
        self.__user_mgt.add_new_commit(int(last_new_commit_id) + 1, commit_data)
        ph.ok(" " + "Created commit successfully!")

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
        branch_data = self.__repo_management.get_branch_data(
            self.__user_mgt.get_user_data()['current_branch'])
        if not branch_data:
            raise Exception(
                "Error, couldn't get branch data while renaming the branch!")
        branch_id = branch_data['id']
        committer = self.__repo_management.get_owner_data()['id']

        commit_data = {
            "amend": True,
            "message": new_message if new_message else\
                self.__user_mgt.get_last_new_commit(branch_data["id"])[1]['message'],
            "branch": int(branch_id),
            "committer": int(committer),
            "unique_id": commit_unique_id,
            "date_updated": str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        }

        last_new_commit_id = self.__user_mgt.get_last_new_commit(
            branch_id=self.__repo_management.get_branch_data(
                branch_name=self.__user_mgt.get_user_data()["current_branch"])["id"]
        )[0]

        if len(self.__user_mgt.get_user_data()['new_commits']) == 1:
            self.__user_mgt.add_new_commit(int(last_new_commit_id) + 1, commit_data)
        else:
            self.__user_mgt.modify_new_commit(last_new_commit_id, commit_data)
        
        ph.ok(" Amended commit successfully!")

def undo(config_folder, repo_management, user_management):
    if len(user_management.get_user_data()["new_commits"]) == 1:
        ph.warn(
            "You don't have any commits in the current branch,"
            " do you want to delete the last commit remotely? (Y/n)"
        )
        answer = input("\t\t\t\n")
        if answer == 'Y' or answer == 'y' or answer == 'Yes' or answer == 'yes':
            ## Remove the last commit remotely
            # Delete the commit from the API
            last_commit = repo_management.get_latest_commit(
                    user_management.get_user_data()["current_branch"]
                )
            API_end_point = 'http://127.0.0.1:8000/api/v1/commits/' + f'{last_commit["id"]}/'
            
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
        branch_data = repo_management.get_branch_data(
            branch_name=user_management.get_user_data()["current_branch"])
        if not branch_data:
            raise Exception(
                "Error, couldn't get branch data while renaming the branch!")
        (internal_id, commit_data) = user_management.get_last_new_commit(
            branch_id=branch_data["id"]
        )
        user_management.delete_new_commit(internal_id)
        commit_unique_id = commit_data["unique_id"]
        commit_file_name = os.path.join(
            config_folder, 
            user_management.get_user_data()["current_branch"] + f"/{commit_unique_id}.tar.xz"
        )
        os.remove(commit_file_name)

        # Update the repository
        update_repository(config_folder, repo_management, user_management)

def update_repository(config_folder, repo_management, user_management, last_commit=None):
    # Delete the working directory
    repo_management.delete_working_directory()
    commit_data = None

    # Extract the last commit 
    if not last_commit:
        branch_data = repo_management.get_branch_data(
            branch_name=user_management.get_user_data()["current_branch"])
        if not branch_data:
            raise Exception(
                "Error, couldn't get branch data while renaming the branch!")
        commit_data = user_management.get_last_new_commit(
            branch_id=branch_data["id"]
        )[1]
    else:
        commit_data = last_commit

    commit_unique_id = commit_data["unique_id"]
    commit_file_name = os.path.join(
        config_folder, 
        user_management.get_user_data()["current_branch"] + f"/{commit_unique_id}.tar.xz"
    )
    working_dir = config_folder.split('.mvcs')[0]
    if Repository.repo.is_nonempty_tar_file(commit_file_name):
        try:
            with tarfile.open(commit_file_name) as ccf:
                ccf.extractall(working_dir)
        except Exception as e:
            raise Exception(e)
