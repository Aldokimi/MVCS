import {
    GET_ALL_REPOS_SUCCESS,
    GET_ALL_REPOS_FAIL,
    GET_REPO_SUCCESS,
    GET_REPO_FAIL,
    CREATE_REPO_SUCCESS,
    CREATE_REPO_FAIL,
    MODIFY_REPO_SUCCESS,
    MODIFY_REPO_FAIL,
    DELETE_REPO_SUCCESS,
    DELETE_REPO_FAIL,
} from "../actions/types";

const repos_initialState = { allReposProvided: false, repos: null };
const repo_initialState = { oneRepoDataProvided: false, repo: null };
const create_repo_initialState = { repoCreated: false, created_repo: null};
const modify_repo_initialState = { repoModified: false, modified_repo: null};
const delete_repo_initialState = { repoDeleted: false};

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
                repo: payload.repo
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

const create_repo = (state = create_repo_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case CREATE_REPO_SUCCESS:
            return {
                ...state,
                repoCreated: true,
                created_repo: payload.created_repo
            };
        case CREATE_REPO_FAIL:
            return {
                ...state,
                repoCreated: false,
                created_repo: null,
            };
        default:
            return state;
    }
}

const modify_repo = (state = modify_repo_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case MODIFY_REPO_SUCCESS:
            return {
                ...state,
                repoModified: true,
                modified_repo: payload.modified_repo
            };
        case MODIFY_REPO_FAIL:
            return {
                ...state,
                repoModified: false,
                modified_repo: null,
            };
        default:
            return state;
    }
}

const delete_repo = (state = delete_repo_initialState, action) => {
    const { type } = action;

    switch (type) {
        case DELETE_REPO_SUCCESS:
            return {
                ...state,
                repoDeleted: true,
            };
        case DELETE_REPO_FAIL:
            return {
                ...state,
                repoDeleted: false,
            };
        default:
            return state;
    }
}

// eslint-disable-next-line import/no-anonymous-default-export
export {
    all_repos,
    repo,
    create_repo,
    modify_repo,
    delete_repo,
};