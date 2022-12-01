import {
    GET_ALL_REPOS_SUCCESS,
    GET_ALL_REPOS_FAIL,
    GET_REPO_SUCCESS,
    GET_REPO_FAIL,
    MODIFY_REPO_SUCCESS,
    MODIFY_REPO_FAIL,
    DELETE_REPO_SUCCESS,
    DELETE_REPO_FAIL,
} from "../actions/types";

const repos_initialState = { allReposProvided: false, repos: null };
const repo_initialState = { oneRepoDataProvided: false, repo: null };

const all_repos = (state = repos_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_ALL_REPOS_SUCCESS:
            return {
                ...state,
                allReposProvided: true,
                repos: payload.repos
            };
        case GET_ALL_REPOS_FAIL:
            return {
                ...state,
                allReposProvided: false,
                repos: null,
            };
        default:
            return state;
    }
}

const repo = (state = repo_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_REPO_SUCCESS:
            return {
                ...state,
                oneRepoDataProvided: true,
                repo: payload.me_as_user
            };
        case GET_REPO_FAIL:
            return {
                ...state,
                oneRepoDataProvided: false,
                repo: null,
            };
        default:
            return state;
    }
}

// eslint-disable-next-line import/no-anonymous-default-export
export {
    all_repos,
    repo,
};