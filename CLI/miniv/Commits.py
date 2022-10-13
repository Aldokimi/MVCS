import os

from helper import RepoManagement as RM

class commit():
    __list, __info, __create, __amend = None, None, None, None
    __repo_management, __config_folder = None, None

    def __init__(self, args) -> None:
        self.__list   = args.list
        self.__info   = args.info
        self.__create = args.create
        self.__amend  = args.amend

        repo_path = os.path.join(os.getcwd())
        self.__config_folder = os.path.join(repo_path, ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)

        if self.  __list:
            self. __list_commits()
        elif self.__info:
            self. __show_info()
        elif self.__create:
            self. __create_commit()
        elif self.__amend:
            self. __amend_commit()

    def __list_commits(self):
        print(self.__repo_management.get_branch_data("main"))

    def __show_info(self):
        pass

    def __create_commit(self):
        pass

    def __amend_commit(self):
        pass