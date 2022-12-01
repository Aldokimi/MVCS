import {
    GET_ALL_BRANCHES_SUCCESS,
    GET_ALL_BRANCHES_FAIL,
    GET_BRANCH_SUCCESS,
    GET_BRANCH_FAIL,
    MODIFY_BRANCH_SUCCESS,
    MODIFY_BRANCH_FAIL,
    DELETE_BRANCH_SUCCESS,
    DELETE_BRANCH_FAIL,
} from "./types";

import APIService from "../services/api.service";

export const getAllBranches = () => (dispatch) => {
    return APIService.getAllBranches().then(
        (response) => {
            dispatch({
                type: GET_ALL_BRANCHES_SUCCESS,
                payload: { branches: response },
            });
            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();

            dispatch({
                type: GET_ALL_BRANCHES_FAIL,
                payload: message,
            });

            return Promise.reject();
        }
    )
}

export const getBranch = (id) => (dispatch) => {
    return APIService.getBranch(id).then(
        (response) => {
            dispatch({
                type: GET_BRANCH_SUCCESS,
                payload: { branch: response },
            });

            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data) || error.message || error.toString();

            dispatch({
                type: GET_BRANCH_FAIL,
                payload: message,
            });

            return Promise.reject();
        }
    )
}
