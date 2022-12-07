import shutil
import subprocess
import tarfile
import requests
import os
import json

from getpass import getpass
from helper import print_helper as ph
from helper import UserManagement as UM
from helper import RepoManagement as RM

class repo():
    
    __clone_url, __create_request, __config_folder, __UM = None, None, None, None

    def __init__(self, args) -> None:
        self.__clone_url = args.clone
        self.__create_request = args.create
        
        if self.__clone_url or self.__create_request:
            '''
            Create the repo directory and a .mvcs file in the base dir
            '''
            # get the repo name and the repo path
            repo_name = self.__create_request if self.__create_request else self.__clone_url.split('@')[1].rsplit('/', 2)[-2:][1]
            repo_path = os.path.join(os.getcwd(), repo_name)

            # check if the repository is already cloned or there is directory with the same name
            if not os.path.exists(repo_path):
                os.mkdir(repo_path, 0o755)
            else:
                ph.err(f"Error, there is already a directory with the same name <{repo_name}>!")
                return

            # create the config folder path
            self.__config_folder = os.path.join(repo_path, ".mvcs")

            if not os.path.exists(self.__config_folder):
                os.mkdir(self.__config_folder, 0o755)
            else:
                if not os.path.exists(repo_path):
                    shutil.rmtree(repo_path)
                ph.err("Error, there already exists a config directory (you are already in a repository)!")
                return
        else:
            ph.err("Error, wrong input, please clone repository or create a new one!")
            return

        if self.__clone_url:
            try:
                self.clone()
                user = self.__clone_url.split('@')[0]
                if self.__UM.check_ssh(host=user, user=user):
                    ph.err("Error, wrong clone URL, please try check your URL again!")
            except Exception as e:
                if os.path.exists(repo_path):
                    shutil.rmtree(repo_path)
                    print(e)

        elif self.__create_request:
            self.create()

    def login(self):
        '''
        Login user to the web application
        '''
        # Get email and password from consol
        user_data = {}
        ph.msg(ph.green("\nPlease login into your account: "))

        email = str(input("Email: "))
        password = str(getpass(prompt='Password: '))
        
        # Login into the API
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/login/', 
            json = {"email":f"{email}", "password": f"{password}"})

        if response.status_code != 200:
            ph.msg(ph.red("You may entered the password or the email wrong, please try again!"))
            email = str(input("Email: "))
            password = str(getpass(prompt='Password: '))
            response = requests.post(
                'http://127.0.0.1:8000/api/v1/login/', 
                json = {"email":f"{email}", "password": f"{password}"})


        if response.status_code == 200:
            user_data['refresh_token'] = (response.json()['refresh'])
            user_data['access_token']  = (response.json()['access'])
            user_data['current_branch']= "main"
            user_data['email']         = email
            user_data['id']            = response.json()['user_id']
            user_data['password']      = UM.UserManagement.encrypt_password(password).decode("utf-8")
            user_data['clone_url']     = self.__clone_url
        else:
            ph.err("Error, wrong credentials, please try to clone again!")
            return

        return user_data

    def create_user_configuration(self, user_data):
        ''' 
        Save the repo data to repo_config.json with all the user's data. (in the .mvcs dir) 
        '''
        # Creating user_config.json
        user_config_file = os.path.join(self.__config_folder, "user_config.json")
        if not os.path.isfile(user_config_file):
            try:
                with open(user_config_file, 'w+') as f:
                    json.dump(user_data, f)
            except:
                raise Exception("Internal error, couldn't create user_config file!")
        else:
            raise Exception("Error, there exists already user config file!")

    def clone(self):
        '''
        Check if the user has SSH permissions to the server, 
        save the repo data to repo_config.json and, 
        save login data into user_config.json, then 
        with all the user's data. (in the .mvcs dir) \n
        Download the compressed folder of the last commit 
        in the main branch to .mvcs/main/ and decompress it to the base dir and
        decompress the commit folder into the working directory.
        '''
        host      = self.__clone_url.split('@')[1]
        repo_name = host.rsplit('/', 2)[-2:][1]
        repo_owner= host.rsplit('/', 2)[-2:][0]
        host      = host.rsplit(':', 1)[0]

        # Login user
        user_data = self.login()
        # print(user_data)
        self.create_user_configuration(user_data)
        self.__UM = UM.UserManagement(self.__config_folder)

        # Creating repo_config.json
        headers={
            "Authorization": f"Bearer {self.__UM.get_user_data()['access_token']}",
        }

        repo_config_file = os.path.join(self.__config_folder, "repo_config.json")
        if not os.path.isfile(repo_config_file):
            try:
                with open(repo_config_file, 'w+') as f:
                    response = requests.get(f'http://127.0.0.1:8000/api/v1/repos/data/{repo_owner}/{repo_name}/', headers=headers)
                    if response.status_code != 200:
                        raise Exception("Error, requesting repo data failed, please check your clone URL and try again")
                    repo_data = response.json()
                    json.dump(repo_data, f)
            except:
                raise Exception("Internal error, couldn't create repo_config file!")
        else:
            raise Exception("Error, there exists already repository config file!")

        repo_management = RM.RepoManagement(self.__config_folder)
        self.__UM.add_initial_commit(repo_management.get_latest_commit('main'))

        '''
        Download the compressed folder of the last commit 
        in the main branch to .mvcs/main/ and decompress it to the base dir
        '''
        ph.msg(ph.blue("\nDownloading the data: \n"))
        try:
            branches = repo_management.get_repo_config()["branches"]
            for branch_id in branches:
                branch_name = branches[branch_id]["name"]
                p = subprocess.run(
                    [
                        'scp', '-r', 
                        f'{self.__clone_url}/{branch_name}/', 
                        f'{self.__UM.fix_path(self.__config_folder)}'
                    ]
                )
                if p.returncode != 0 :
                    raise Exception("Error, Downloading repo data failed, make sure to upload the ssk key to the MVCShub!")
        except subprocess.CalledProcessError or p.returncode != 0:
            raise Exception("Error, error occurred during downloading the data!")

        '''
        Decompress the commit folder into the working directory.
        '''
        branch_folder = os.path.join(self.__config_folder, 'main')
        commit_folder = os.path.join(branch_folder, os.listdir(branch_folder)[0])
        working_dir = self.__config_folder.split('.mvcs')[0]
        if self.is_nonempty_tar_file(commit_folder):
            try:
                with tarfile.open(commit_folder) as ccf:
                    ccf.extractall(working_dir)
            except:
                raise Exception("Couldn't extract the last commit to main during cloning!")

        ph.ok("    Cloned successfully!")

    @staticmethod
    def is_nonempty_tar_file(archive):
        with tarfile.open(archive, "r") as tar:
            try:
                file_content = tar.getmembers()
                return len(file_content) > 0
            except Exception as exc:
                raise Exception(f"Reading tarfile failed for {archive}")

    def create(self):
        '''
        Create a new repository locally with the possiblity to create it remotely!
        '''
        ph.msg("Do you want to create this repository remotely as well? (Y/n)")
        answer = input()
        if str(answer) == "Y" or str(answer) == "y" or str(answer) == "Yes" or str(answer) == "yes":
            # Login user and create user configuration
            user_data = self.login()
            self.create_user_configuration(user_data)
        os.mkdir(os.path.join(self.__config_folder, "main"))
