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
} from "./types";

import APIService from "../services/api.service";

export const getAllUsers = () => (dispatch) => {
    return APIService.getAllUsers().then(
        (response) => {
            dispatch({ type: GET_ALL_USERS_SUCCESS, payload: { users: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: GET_ALL_USERS_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}

export const getUser = (id) => (dispatch) => {
    return APIService.getUser(id).then(
        (response) => {
            dispatch({ type: GET_USER_SUCCESS, payload: { me_as_user: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: GET_USER_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}

export const getUserRepos = (id) => (dispatch) => {
    return APIService.getReposForUser(id).then(
        (response) => {
            dispatch({ type: GET_USER_REPOS_SUCCESS, payload: { user_repos: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: GET_USER_REPOS_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}

export const getUserBranches = (id) => (dispatch) => {
    return APIService.getBranchesForUser(id).then(
        (response) => {
            dispatch({ type: GET_USER_BRANCHES_SUCCESS, payload: { user_branches: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: GET_USER_BRANCHES_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}

export const getUserCommits = (id) => (dispatch) => {
    return APIService.getCommitsForUser(id).then(
        (response) => {
            dispatch({ type: GET_USER_COMMITS_SUCCESS, payload: { user_commits: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: GET_USER_COMMITS_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}

export const modifyUser = (id, data) => (dispatch) => {
    return APIService.modifyUser(id, data).then(
        (response) => {
            dispatch({ type: MODIFY_USER_SUCCESS, payload: { modified_user: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: MODIFY_USER_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}

export const deleteUser = (id) => (dispatch) => {
    return APIService.deleteUser(id).then(
        (response) => {
            dispatch({ type: DELETE_USER_SUCCESS, payload: { deleted_user: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: DELETE_USER_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}
