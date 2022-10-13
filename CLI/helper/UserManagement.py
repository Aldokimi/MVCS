import subprocess
import bcrypt
import paramiko


def hash_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)


def fix_path(path):
    return str('/' + path.replace('\\','/'))

def check_ssh(host, user, port=20):
    sshClient = paramiko.SSHClient()
    try:    
        sshClient.connect(host, user)
        stdin, stdout, stderr = sshClient.exec_command('exit')
        return True
    except:
        return False
