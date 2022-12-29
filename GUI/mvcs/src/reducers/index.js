import { combineReducers } from "redux";
import auth from "./auth";

import { 
    all_users,
    user,
    user_repos,
    user_branches,
    user_commits,
    modify_user,
    delete_user
} from "./users"

import { 
    all_repos,
    repo,
    create_repo,
    modify_repo,
    delete_repo,
} from "./repos";

import { 
    all_branches,
    branch,
    create_branch,
    modify_branch,
    delete_branch,
} from "./branches";

import { 
    all_commits,
    commit,
    modify_commit,
    delete_commit,
    commit_file_tree,
} from "./commits";

import message from "./message";

export default combineReducers({
    // Auth
    auth,
    // User
    all_users,
    user,
    user_repos,
    user_branches,
    user_commits,
    modify_user,
    delete_user,
    // Repo
    all_repos,
    repo,
    create_repo, 
    modify_repo, 
    delete_repo,
    // Branch
    all_branches, 
    branch,
    create_branch,
    modify_branch,
    delete_branch,
    // Commit
    all_commits, 
    commit,
    modify_commit,
    delete_commit,
    commit_file_tree,
    // Message
    message,
});