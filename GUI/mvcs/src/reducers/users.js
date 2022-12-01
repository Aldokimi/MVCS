import {
    GET_ALL_USERS_SUCCESS,
    GET_ALL_USERS_FAIL,
    GET_USER_SUCCESS,
    GET_USER_FAIL,
    MODIFY_USER_SUCCESS,
    MODIFY_USER_FAIL,
    DELETE_USER_SUCCESS,
    DELETE_USER_FAIL,
    GET_USER_REPOS_SUCCESS,
    GET_USER_REPOS_FAIL,
    GET_USER_BRANCHES_SUCCESS,
    GET_USER_BRANCHES_FAIL,
    GET_USER_COMMITS_SUCCESS,
    GET_USER_COMMITS_FAIL, 
} from "../actions/types";

const users_initialState = { allUsersProvided: false, users: null };
const user_initialState = { userProvided: false, user: null };
const user_repos_initialState = { allUserReposProvided: false, user_repos: null };
const user_branches_initialState = { allUserBranchesProvided: false, user_branches: null };
const user_commits_initialState = { allUserCommitsProvided: false, user_commits: null };

const all_users = (state = users_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_ALL_USERS_SUCCESS:
            return { ...state, allUsersProvided: true, users: payload.users };
        case GET_ALL_USERS_FAIL:
            return { ...state, allUsersProvided: false, users: null, };
        default:
            return state;
    }
}

const user = (state = user_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_USER_SUCCESS:
            return { ...state, userProvided: true, user: payload.me_as_user };
        case GET_USER_FAIL:
            return { ...state, userProvided: false, user: null, };
        default:
            return state;
    }
}

const user_repos = (state = user_repos_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_USER_REPOS_SUCCESS:
            return { ...state, allUserReposProvided: true, user_repos: payload.user_repos };
        case GET_USER_REPOS_FAIL:
            return { ...state, allUserReposProvided: false, user_repos: null, };
        default:
            return state;
    }
}

const user_branches = (state = user_branches_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_USER_BRANCHES_SUCCESS:
            return { ...state, allUserReposProvided: true, user_branches: payload.user_branches };
        case GET_USER_BRANCHES_FAIL:
            return { ...state, allUserReposProvided: false, user_branches: null, };
        default:
            return state;
    }
}

const user_commits = (state = user_commits_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_USER_COMMITS_SUCCESS:
            return { ...state, allUserReposProvided: true, user_commits: payload.user_commits };
        case GET_USER_COMMITS_FAIL:
            return { ...state, allUserReposProvided: false, user_commits: null, };
        default:
            return state;
    }
}

// eslint-disable-next-line import/no-anonymous-default-export
export {
    all_users,
    user,
    user_repos,
    user_branches,
    user_commits,
};