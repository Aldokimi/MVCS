import os
import paramiko
import json
import requests
import base64
import hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes


class UserManagement():
    __user_config = None
    __config_folder = None
    __key__ = hashlib.sha256(b'16-character key').digest()

    def __init__(self, config_folder) -> None:
        self.__config_folder = config_folder
        try:
            with open(os.path.join(self.__config_folder, 'user_config.json'), 'r') as f:
                self.__user_config = json.load(f)
        except:
            raise Exception("Error, cannot open user_config.json")

    def login(self):
        response = requests.post(
            'http://127.0.0.1:8000/api/login/', 
            json = {
                "email": f"{self.__user_config['email']}", 
                "password": f"{self.decrypt_password(self.__user_config['password'])}"
            }
        )
        return response.status_code == 200

    def get_user_data(self):
        return self.__user_config

    @staticmethod
    def encrypt_password(raw):
        BS = AES.block_size
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        raw = base64.b64encode(pad(raw).encode('utf8'))
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key= UserManagement.__key__, mode= AES.MODE_CFB,iv= iv)
        return base64.b64encode(iv + cipher.encrypt(raw))
    
    @staticmethod
    def decrypt_password(enc):
        unpad = lambda s: s[:-ord(s[-1:])]
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(UserManagement.__key__, AES.MODE_CFB, iv)
        return unpad(base64.b64decode(cipher.decrypt(enc[AES.block_size:])).decode('utf8'))

    def fix_path(self, path):
        return str(path.replace('\\','/'))

    def check_ssh(self, host, user, port=20):
        sshClient = paramiko.SSHClient()
        try:    
            sshClient.connect(host, user)
            stdin, stdout, stderr = sshClient.exec_command('exit')
            return True
        except:
            return False

    def add_initial_commit(self, commit):
        try:
            with open(os.path.join(self.__config_folder, 'user_config.json'), 'w') as f:
                self.__user_config['new_commits'] = { 0 : commit}
                json.dump(self.__user_config, f)
        except:
            raise Exception("Error, cannot open repo_config.json")

    def add_new_commit(self, internal_id, commit_data):
        try:
            with open(os.path.join(self.__config_folder, 'user_config.json'), 'w') as f:
                self.__user_config['new_commits'][f"{internal_id}"] = commit_data
                json.dump(self.__user_config, f)
        except:
            raise Exception("Error, cannot open repo_config.json")

    def modify_new_commit(self, last_new_commit_id, commit_data):
        try:
            with open(os.path.join(self.__config_folder, 'user_config.json'), 'w') as f:
                self.__user_config['new_commits'][last_new_commit_id] = commit_data
                json.dump(self.__user_config, f)
        except:
            raise Exception("Error, cannot open repo_config.json")

    def get_last_new_commit(self):
        last_commit = self.__user_config['new_commits']['0']
        commit_internal_id = 0

        for commit in self.__user_config['new_commits']:
            if int(commit) > commit_internal_id:
                last_commit = self.__user_config['new_commits'][commit]
                commit_internal_id = int(commit)

        return (commit_internal_id, last_commit)

    def update_current_branch(self, new_branch):
        try:
            with open(os.path.join(self.__config_folder, 'user_config.json'), 'w') as f:
                self.__user_config['current_branch'] = new_branch
                json.dump(self.__user_config, f)
        except:
            raise Exception("Error, cannot open repo_config.json")

    def is_in_main(self):
        return self.__user_config['current_branch'] == "main"

    def check_for_uncommited_files(self):
        return False
