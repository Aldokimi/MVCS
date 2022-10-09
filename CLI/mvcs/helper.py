from datetime import datetime
import sys
import bcrypt
import os
import json
import socket

from tabulate import tabulate # requirements

'''
# Print Helper functionalities
'''

DISABLE_COLOR = False

# Colored strings
RED = '\033[31m'
RED_BOLD = '\033[1;31m'
GREEN = '\033[32m'
GREEN_BOLD = '\033[1;32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
CLEAR = '\033[0m'

# Colors setting

def should_color():
    return not DISABLE_COLOR and sys.stdout.isatty()

def _color(color_code, text):
    return '{0}{1}{2}'.format(color_code, text, CLEAR) if should_color() else text

def red(text):
    return _color(RED, text)

def green(text):
    return _color(GREEN, text)

def yellow(text):
    return _color(YELLOW, text)

def blue(text):
    return _color(BLUE, text)

def magenta(text):
    return _color(MAGENTA, text)

def cyan(text):
    return _color(CYAN, text)


# Text coloring and formatting
def puts(text='', newline=True, stream=sys.stdout.write, border=False):
    if newline:
        text = text + '\n'
    if border:
        table = [[text]]
        output = tabulate(table, tablefmt='grid')
        stream(output)
    else:
        stream(text)

def ok(text):
    puts(green('✔ {0}'.format(text)), border=True)

def warn(text):
    puts(yellow('! {0}'.format(text)), border=True)

def err(text):
    puts(red('✘ {0}'.format(text)), stream=sys.stderr.write, border=True)

def exp(text, stream=sys.stdout.write):
    puts('  ➜ {0}'.format(text), stream=stream)

def err_exp(text):
    exp(text, stream=sys.stderr.write)

def msg(text, stream=sys.stdout.write):
    puts(text, stream=stream)

def color_text(text, color, text1='', text2='', border=False):
    if color == "RED":
        puts(text1 + red('{0}'.format(text)) + text2, border=border)
    elif color == "GREEN":
        puts(text1 + green('{0}'.format(text)) + text2, border=border)
    elif color == "YELLOW":
        puts(text1 + yellow('{0}'.format(text)) + text2, border=border)
    elif color == "BLUE":
        puts(text1 + blue('{0}'.format(text)) + text2, border=border)
    elif color == "MAGENTA":
        puts(text1 + magenta('{0}'.format(text)) + text2, border=border)
    elif color == "CYAN":
        puts(text1 + cyan('{0}'.format(text)) + text2, border=border)


'''
# User management helpers
'''

def hash_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)


def fix_path(path):
    return str('/' + path.replace('\\','/'))

def check_ssh(server_ip, port=20):
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.connect((server_ip, port))
    except:
        return False
    else:
        test_socket.close()
    return True

'''
# Repository management helper
'''

class RepoManagement():

    __repo_config = {}
    __repo_config_file  = ""

    def __init__(self, config_folder):
        '''
        Get the repo config data and store it in a dict.
        '''
        repo_config_file = os.path.join(config_folder, "repo_config.json")
        self.__repo_config_file = repo_config_file
        try:
            with open(repo_config_file, 'r') as f:
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
