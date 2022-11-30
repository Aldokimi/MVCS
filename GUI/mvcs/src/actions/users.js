import {
    GET_ALL_USERS_SUCCESS,
    GET_ALL_USERS_FAIL,
    GET_USER_SUCCESS,
    GET_USER_FAIL,
    MODIFY_USER_SUCCESS,
    MODIFY_USER_FAIL,
    DELETE_USER_SUCCESS,
    DELETE_USER_FAIL,
} from "./types";

import APIService from "../services/api.service";

export const getAllUsers = () => (dispatch) => {
    return APIService.getAllUsers().then(
        (response) => {
            dispatch({
                type: GET_ALL_USERS_SUCCESS,
                payload: { users: response },
            });

            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data &&
                error.response.data.error) || error.message || error.toString();

            dispatch({
                type: GET_ALL_USERS_FAIL,
                payload: message,
            });

            return Promise.reject();
        }
    )
}

export const getUser = (id) => (dispatch) => {
    return APIService.getUser(id).then(
        (response) => {
            dispatch({
                type: GET_USER_SUCCESS,
                payload: { me_as_user: response },
            });

            return Promise.resolve();
        },
        (error) => {
            const message = (error.response && error.response.data &&
                error.response.data.error) || error.message || error.toString();

            dispatch({
                type: GET_USER_FAIL,
                payload: message,
            });

            return Promise.reject();
        }
    )
}
