import unittest
import os
import json

from deepdiff import DeepDiff

from helper import RepoManagement as RM
from helper import UserManagement as UM

from miniv import Repository
from miniv import Branch
from miniv import Diff
from miniv import Merge


# Test RepoManagement.py
class RepoManagementTestCase(unittest.TestCase):
    def setUp(self):
        base_bath = os.path.join(os.getcwd(), "tests")
        repo_path = os.path.join(base_bath, "data")
        self.__config_folder = os.path.join(repo_path, ".mvcs")
        self.__repo_management = RM.RepoManagement(self.__config_folder)

    def tearDown(self):
        # Read the backup file
        base_bath = os.path.join(os.getcwd(), "tests")
        backup_folder = os.path.join(base_bath, "backup")
        backup_file = os.path.join(backup_folder, "repo_config.json")
        with open(backup_file) as repo_config:
            repo_config_data = json.load(repo_config)
            repo_config_file = os.path.join(
                self.__config_folder, "repo_config.json")
            # Dump the backup data into the repo_config.json
            # since it has been modified by the test cases
            with open(repo_config_file, "w") as outfile:
                json.dump(repo_config_data, outfile)

    def test_get_branch_data(self):
        expected_branch_data = self.__repo_management.get_repo_config(
        )['branches']["230"]

        # Get branch data by name
        output = self.__repo_management.get_branch_data(
            branch_name="main")
        assert output is not None
        diff = DeepDiff(expected_branch_data, output)
        assert len(diff) == 0

        # Get branch data by ID
        output2 = self.__repo_management.get_branch_data(
            branch_id=230)
        assert output2 is not None
        diff2 = DeepDiff(expected_branch_data, output2)
        assert len(diff2) == 0

        # Both get by id and get by name are the same
        diff3 = DeepDiff(output, output2)
        assert len(diff3) == 0

    def test_get_latest_commit(self):
        excepted_commit = self.__repo_management.get_repo_config(
        )['branches']["230"]["commits"]["359"]

        output = self.__repo_management.get_latest_commit("main")
        assert output is not None
        diff = DeepDiff(excepted_commit, output)
        assert len(diff) == 0

    def test_get_commit_by_unique_id(self):
        excepted_commit = self.__repo_management.get_repo_config(
        )['branches']["230"]["commits"]["359"]

        output = self.__repo_management.get_commit_by_unique_id(
            "4945016159ae435e8f857f374ceec33b")
        assert output != {}
        output = output["359"]
        diff = DeepDiff(excepted_commit, output)
        assert len(diff) == 0

    def test_create_commit(self):
        commit_data = {
            "id": 360,
            "date_created": "2022-12-21T23:05:27.514975Z",
            "date_updated": "2022-12-21T22:06:02.696124Z",
            "message": "New commit created",
            "branch": 230,
            "committer": 54,
            "unique_id": "4444444"
        }
        self.__repo_management.create_commit(commit_data)
        output = self.__repo_management.get_commit_by_unique_id(
            "4444444")
        assert output != {}

    def test_modify_commit(self):
        commit_data = {
            "unique_id": "5555555"
        }
        commit_id = 359
        self.__repo_management.modify_commit(commit_data, commit_id)
        output = self.__repo_management.get_commit_by_unique_id(
            "5555555")
        assert output != {}

    def test_delete_commit(self):
        self.__repo_management.delete_commit("main", 359)
        output = self.__repo_management.get_commit_by_unique_id(
            "5555555")
        assert output == {}

    def test_create_branch(self):
        branch_data = {
            "id": 332,
            "name": "test_branch",
            "date_created": "2022-12-23T05:08:50.510737Z",
            "has_locked_files": False,
            "locked_files": "null",
            "repo": 104
        }
        self.__repo_management.create_branch(branch_data)
        output = self.__repo_management.get_branch_data(
            branch_name="test_branch")
        assert output is not None

    def test_rename_branch(self):
        self.__repo_management.rename_branch(
            "pp", "test_branch")
        output = self.__repo_management.get_branch_data(
            branch_name="test_branch")
        assert output is not None

    def test_delete_branch(self):
        branch_data = {"id": 231}
        self.__repo_management.delete_branch(branch_data)
        output = self.__repo_management.get_branch_data(
            branch_name="pp")
        assert output is None


# Test UserManagement.py
class UserManagementTestCase(unittest.TestCase):

    def setUp(self):
        base_path = os.path.join(os.getcwd(), "tests")
        repo_path = os.path.join(base_path, "data")
        self.__config_folder = os.path.join(repo_path, ".mvcs")
        self.__user_management = UM.UserManagement(self.__config_folder)

    def test_encrypt_decrypt_password(self):
        password = "password"
        enc = self.__user_management.encrypt_password(password)
        assert password != enc
        dec = self.__user_management.decrypt_password(enc)
        assert password == dec


# Test Repository.py
class RepositoryTestCase(unittest.TestCase):

    def setUp(self):
        self.repository = Repository.repo
        base_path = os.path.join(os.getcwd(), "tests")
        repo_path = os.path.join(base_path, "data")
        self.__config_folder = os.path.join(repo_path, ".mvcs")

    def test_nonempty_tar_fil(self):
        empty_commit_name = "49b245f0cf5b4273bfa04aec4083a859.tar.xz"
        main_branch = os.path.join(self.__config_folder, "main")
        empty_commit_file = os.path.join(main_branch, empty_commit_name)
        assert not self.repository.is_nonempty_tar_file(empty_commit_file)
        nonempty_commit_name = "12a3112b438a4fcc9115fbe0fb458d65.tar.xz"
        nonempty_commit_file = os.path.join(main_branch, nonempty_commit_name)
        assert self.repository.is_nonempty_tar_file(nonempty_commit_file)


# Test Branch.py
class BranTestCase(unittest.TestCase):

    def setUp(self):
        base_path = os.path.join(os.getcwd(), "tests")
        repo_path = os.path.join(base_path, "data")
        self.__config_folder = os.path.join(repo_path, ".mvcs")
        self.__user_management = UM.UserManagement(self.__config_folder)
        self.__repo_management = RM.RepoManagement(self.__config_folder)

    def test_get_last_commit(self):
        commit = Branch.get_last_commit(
            self.__repo_management, self.__user_management, branch="main")
        last_commit_id = 359
        assert commit["id"] == last_commit_id

# Test Diff.py


class DiffTestCase(unittest.TestCase):

    def setUp(self):
        base_path = os.path.join(os.getcwd(), "tests")
        self.__repo_path = os.path.join(base_path, "data")
        self.__config_folder = os.path.join(self.__repo_path, ".mvcs")
        self.__user_management = UM.UserManagement(self.__config_folder)
        self.__repo_management = RM.RepoManagement(self.__config_folder)

    def test_diff_repo(self):
        diffs, new_files = Diff.diff_repo(self.__config_folder,
                                          self.__repo_management, self.__user_management)
        assert diffs is not None
        assert len(new_files) == 1

    def test_preform_diff(self):
        file1 = os.path.join(self.__repo_path, "file.txt")
        file2 = os.path.join(self.__repo_path, "file2.txt")
        diff = Diff.preform_diff(file1, file2, diff_only=True)
        assert len(diff) == 2


# # Test Merge.py
class MergeTestCase(unittest.TestCase):

    def setUp(self):
        base_path = os.path.join(os.getcwd(), "tests")
        self.__repo_path = os.path.join(base_path, "data")

    def test_merge_files(self):
        file1 = os.path.join(self.__repo_path, "file.txt")
        file2 = os.path.join(self.__repo_path, "file2.txt")
        (merge_output, has_conflicts) = Merge.merge.merge_files(file1, file2)
        assert not has_conflicts
