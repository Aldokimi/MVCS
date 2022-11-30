import {
    GET_ALL_USERS_SUCCESS,
    GET_ALL_USERS_FAIL,
    GET_USER_SUCCESS,
    GET_USER_FAIL,
    MODIFY_USER_SUCCESS,
    MODIFY_USER_FAIL,
    DELETE_USER_SUCCESS,
    DELETE_USER_FAIL,
} from "../actions/types";

const users_initialState = { dataProvided: false, users: null };
const user_initialState = { oneDataProvided: false, user: null };

const all_users = (state = users_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_ALL_USERS_SUCCESS:
            return {
                ...state,
                dataProvided: true,
                users: payload.users
            };
        case GET_ALL_USERS_FAIL:
            return {
                ...state,
                dataProvided: false,
                users: null,
            };
        default:
            return state;
    }
}

const user = (state = user_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_USER_SUCCESS:
            return {
                ...state,
                dataProvided: false,
                users: payload.me_as_user
            };
        case GET_USER_FAIL:
            return {
                ...state,
                dataProvided: false,
                users: null,
            };
        default:
            return state;
    }
}

// eslint-disable-next-line import/no-anonymous-default-export
export {
    all_users,
    user,
};