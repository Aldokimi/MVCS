import {
    GET_ALL_COMMITS_SUCCESS,
    GET_ALL_COMMITS_FAIL,
    GET_COMMIT_SUCCESS,
    GET_COMMIT_FAIL,
    MODIFY_COMMIT_SUCCESS,
    MODIFY_COMMIT_FAIL,
    DELETE_COMMIT_SUCCESS,
    DELETE_COMMIT_FAIL,
    GET_COMMIT_FILE_TREE_SUCCESS,
    GET_COMMIT_FILE_TREE_FAIL,
} from "./types";

import APIService from "../services/api.service";

export const getAllCommits = () => (dispatch) => {
    return APIService.getAllCommits().then(
        (response) => {
            dispatch({
                type: GET_ALL_COMMITS_SUCCESS,
                payload: { commits: response },
            });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();

            dispatch({
                type: GET_ALL_COMMITS_FAIL,
                payload: message,
            });

            return Promise.reject();
        }
    )
}

export const getCommit = (id) => (dispatch) => {
    return APIService.getCommit(id).then(
        (response) => {
            dispatch({
                type: GET_COMMIT_SUCCESS,
                payload: { commit: response },
            });

            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();

            dispatch({
                type: GET_COMMIT_FAIL,
                payload: message,
            });

            return Promise.reject();
        }
    )
}

export const getCommitFileTree = (id) => (dispatch) => {
    return APIService.getCommitFileTree(id).then(
        (response) => {
            dispatch({
                type: GET_COMMIT_FILE_TREE_SUCCESS,
                payload: { commit_file_tree: response },
            });

            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();

            dispatch({
                type: GET_COMMIT_FILE_TREE_FAIL,
                payload: message,
            });

            return Promise.reject();
        }
    )
}

export const modifyCommit = (id, data) => (dispatch) => {
    return APIService.modifyCommit(id, data).then(
        (response) => {
            dispatch({ type: MODIFY_COMMIT_SUCCESS, payload: { modified_commit: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: MODIFY_COMMIT_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}

export const deleteCommit = (id) => (dispatch) => {
    return APIService.deleteCommit(id).then(
        (response) => {
            dispatch({ type: DELETE_COMMIT_SUCCESS, payload: { deleted_commit: response }, });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();
            dispatch({ type: DELETE_COMMIT_FAIL, payload: message, });
            return Promise.reject();
        }
    )
}
