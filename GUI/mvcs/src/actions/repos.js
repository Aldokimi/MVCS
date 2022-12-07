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
} from "./types";

import APIService from "../services/api.service";

export const getAllRepos = () => (dispatch) => {
    return APIService.getAllRepos().then(
        (response) => {
            dispatch({ type: GET_ALL_REPOS_SUCCESS, payload: { repos: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: GET_ALL_REPOS_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}

export const getRepo = (id) => (dispatch) => {
    return APIService.getRepo(id).then(
        (response) => {
            dispatch({ type: GET_REPO_SUCCESS, payload: { repo: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: GET_REPO_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}

export const createRepository = (id, data) => (dispatch) => {
    return APIService.createRepository(id, data).then(
        (response) => {
            dispatch({ type: CREATE_REPO_SUCCESS, payload: { created_repo: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: CREATE_REPO_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}

export const modifyRepo = (id, data) => (dispatch) => {
    return APIService.modifyRepository(id, data).then(
        (response) => {
            dispatch({ type: MODIFY_REPO_SUCCESS, payload: { modified_repo: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: MODIFY_REPO_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}

export const deleteRepo = (id) => (dispatch) => {
    return APIService.deleteRepository(id).then(
        (response) => {
            dispatch({ type: DELETE_REPO_SUCCESS, payload: { deleted_repo: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: DELETE_REPO_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}
