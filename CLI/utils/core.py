from miniv import Repository, Commits

def create_repo(args):
    '''
    Creating a new repository:
        You have two options:

            * To clone a repository from the remote server, you can use for this `miniv repo --lone "clone url"`
            * To create a new repository, for this a new repository will be created locally but you will have\
              the option to create this repository remotely as well, you can user for this `miniv repo --create "name_of_the_new_repo"`
    '''
    try:
        Repository.Create(args)
    except Exception as e:
        raise Exception(e)

def status(args):
    print("status")

def commits_handler(args):
    try:
        Commits.commit(args)
    except Exception as e:
        raise Exception(e)

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
