import shutil
import subprocess
import tarfile
import requests
import os
import json
import requests

from getpass import getpass
from helper import print_helper as ph
from helper import UserManagement as UM

class Create():
    
    __clone_url, __create_request, __config_folder, __UM = None, None, None, None

    def __init__(self, args) -> None:
        self.__clone_url = args.clone
        self.__create_request = args.create
        
        if self.__clone_url or self.__create_request:
            '''
            # Create the repo directory and a .mvcs file in the base dir
            '''
            repo_name = self.__create_request if self.__create_request else self.__clone_url.split('@')[1].rsplit('/', 2)[-2:][1]
            repo_path = os.path.join(os.getcwd(), repo_name)
            if not os.path.exists(repo_path):
                os.mkdir(repo_path, 0o755)
            else:
                if os.path.exists(repo_path):
                    shutil.rmtree(repo_path)
                raise Exception("Error, there is already a directory with the same repo name!")
            self.__config_folder = os.path.join(repo_path, ".mvcs")
            if not os.path.exists(self.__config_folder):
                os.mkdir(self.__config_folder, 0o755)
            else:
                if not os.path.exists(repo_path):
                    shutil.rmtree(repo_path)
                raise Exception("Error, there already exists a config directory (you are already in a repository)!")
            self.__UM = UM.UserManagement(self.__config_folder)
        else:
            raise Exception("Error: Wrong input, please clone repository or create a new one!")

        if self.__clone_url:
            self.clone()
        elif self.__create_request:
            self.create()

    def login(self):
        '''
        Login user to the web application
        '''
        # Get email and password from consol
        user_data = {}
        ph.msg("Please login into your account: ")
        email = str(input("Email: "))
        password = str(getpass(prompt='Password: '))
        
        # Login into the API
        response = requests.post(
            'http://127.0.0.1:8000/api/login/', 
            json = {"email":f"{email}", "password": f"{password}"})

        if response.status_code == 200:
            user_data['refresh_token'] = (response.json()['refresh'])
            user_data['access_token']  = (response.json()['access'])
            user_data['current_branch']= "main"
            user_data['email']         = email
            user_data['id']            = response.json()['user_id']
            user_data['password']      = self.__UM.encrypt_password(password).decode("utf-8")
        else:
            raise Exception("Error, wrong credentials, please try again!")

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
        # Check if the user has SSH permissions to the server 
        '''
        user      = self.__clone_url.split('@')[0]
        host      = self.__clone_url.split('@')[1]
        repo_name = host.rsplit('/', 2)[-2:][1]
        host      = host.rsplit(':', 1)[0]
        
        if self.__UM.check_ssh(host=user, user=user):
            raise Exception("Error, wrong clone URL!")

        # Login user
        user_data = self.login()
        
        ''' 
        # Save the repo data to repo_config.json and 
        # save login data into user_config.json
        # with all the user's data. (in the .mvcs dir) 
        '''
        self.create_user_configuration(user_data)

        # Creating repo_config.json
        repo_config_file = os.path.join(self.__config_folder, "repo_config.json")
        if not os.path.isfile(repo_config_file):
            try:
                with open(repo_config_file, 'w+') as f:
                    response = requests.get(f'http://127.0.0.1:8000/api/repos/data/{repo_name}/')
                    if response.status_code != 200:
                        raise Exception("Error, requesting repo data failed, please check your clone URL and try again")
                    repo_data = response.json()
                    json.dump(repo_data, f)
            except:
                raise Exception("Internal error, couldn't create repo_config file!")
        else:
            raise Exception("Error, there exists already repository config file!")

        '''
        # Download the compressed folder of the last commit 
        # in the main branch to .mvcs/main/ and decompress it to the base dir
        '''
        try:
            print(self.__clone_url[:-2])
            p = subprocess.run(['scp', '-r', f'{self.__clone_url}/main/', f'{self.__UM.fix_path(self.__config_folder)}'])
            if p.returncode != 0 :
                raise Exception("Error, Downloading repo data failed!")
        except subprocess.CalledProcessError or p.returncode != 0:
            raise Exception("Error, wrong clone URL!")

        '''
        # Decompress the commit folder into the working directory.
        '''
        branch_folder = os.path.join(self.__config_folder, 'main')
        commit_folder = os.path.join(branch_folder, os.listdir(branch_folder)[0])
        working_dir = self.__config_folder.split('.mvcs')[0]
        
        with tarfile.open(commit_folder) as ccf:
            ccf.extractall(working_dir)
            try:
                path = os.path.join(working_dir, os.listdir(working_dir)[1])
                for filename in os.listdir(path):
                    shutil.move(os.path.join(path, filename), os.path.join(working_dir, filename))
                os.rmdir(path)
            except Exception:
                raise Exception("Error happened during downloading the repo!")

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
