import { combineReducers } from "redux";
import auth from "./auth";
import { all_users, user, user_repos, user_branches, user_commits } from "./users"
import { all_repos, repo } from "./repos";
import { all_branches, branch } from "./branches";
import { all_commits, commit } from "./commits";
import message from "./message";

export default combineReducers({
    auth,
    all_users,
    user,
    user_repos,
    user_branches,
    user_commits,
    all_repos,
    all_branches, 
    branch,
    all_commits, 
    commit,
    repo,
    message,
});