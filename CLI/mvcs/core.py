import subprocess
import re
from getpass import getpass
import msvcrt
import requests
import os
import json

import helper

global repo_config_manger 

def create_repo(args):
    clone_url = args.clone
    create_request = args.create

    if clone_url:
        '''
        # Check if the user has SSH permissions to the server 
        '''
        user      = clone_url.split('@')[0]
        host      = clone_url.split('@')[1]
        repo_name = host.rsplit('/', 2)[-2:][0]
        repo_id   = host.rsplit('/', 2)[-2:][1]
        host      = host.rsplit(':', 1)[0]
        user_data = {}
        
        if helper.check_ssh(host):
            raise Exception("Error, wrong clone URL!")

        '''
        # Login user to the web application
        '''
        # Get email and password from consol
        email = str(input("Email: "))
        password = str(getpass(prompt='Password: '))
        
        # Login into the API
        response = requests.post(
            'http://127.0.0.1:8000/api/login/', 
            json = {"email":f"{email}", "password": f"{password}"})

        if response.status_code == 200:
            user_data['refresh_token'] = (response.json()['refresh'])
            user_data['access_token']  = (response.json()['access'])
            user_data['email']         = email
            user_data['password']      = helper.hash_password(password.encode('utf-8')).decode("utf-8")
        else:
            raise Exception("Error, wrong credentials, please try again!")
        
        '''
        # Create a .mvcs file in the base dir
        '''
        try:
            repo_path = os.path.join(os.getcwd(), repo_name)
            if not os.path.exists(repo_path):
                os.mkdir(repo_path, 0o755)
            else:
                raise Exception("Error, there is already a directory with the same repo name!")
            config_folder = os.path.join(repo_path, ".mvcs")
            if not os.path.exists(config_folder):
                os.mkdir(config_folder, 0o755)
            else:
                raise Exception("Error, there already exists a config directory (you are already in a repository)!")
        except:
            raise Exception("Internal error, couldn't create working directory!")

        ''' 
        # Save the repo data to repo_config.json and 
        # save login data into user_config.json
        # with all the user's data. (in the .mvcs dir) 
        '''
        # Creating user_config.json
        user_config_file = os.path.join(config_folder, "user_config.json")
        if not os.path.isfile(user_config_file):
            try:
                with open(user_config_file, 'w+') as f:
                    json.dump(user_data, f)
            except:
                raise Exception("Internal error, couldn't create user_config file!")
        else:
            raise Exception("Error, there exists already user config file!")

        # Creating repo_config.json
        repo_config_file = os.path.join(config_folder, "repo_config.json")
        if not os.path.isfile(repo_config_file):
            try:
                with open(repo_config_file, 'w+') as f:
                    response = requests.get(f'http://127.0.0.1:8000/api/repos/data/{repo_id}/')
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
            subprocess.run(['scp', '-r', f'{clone_url[:-2]}/main/', f'{helper.fix_path(config_folder)}'])
        except subprocess.CalledProcessError:
            raise Exception("Error, wrong clone URL!")

        '''
        TO DO: # Decompress the commit folder into the working directory.
        '''
        repo_config_manger = helper.RepoManagement(config_folder)
    elif create_request:
        pass
    else:
        raise Exception("Error, no request happened")    

def status(args):
    print("status")

def commits_handler(args):
    print(vars(args))

def branches_handler(args):
    print(vars(args))

def merge_branches(args):
    print(vars(args))

def upload(args):
    print(vars(args))

def update(args):
    print(vars(args))

def checkout(args):
    print("checkout")

def diff(args):
    print("diff")

def undo(args):
    print("undo")
