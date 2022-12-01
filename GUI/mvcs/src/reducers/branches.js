import {
    GET_ALL_BRANCHES_SUCCESS,
    GET_ALL_BRANCHES_FAIL,
    GET_BRANCH_SUCCESS,
    GET_BRANCH_FAIL,
    MODIFY_BRANCH_SUCCESS,
    MODIFY_BRANCH_FAIL,
    DELETE_BRANCH_SUCCESS,
    DELETE_BRANCH_FAIL,
} from "../actions/types";

const branches_initialState = { allBranchesProvided: false, branches: null };
const branch_initialState = { oneBranchProvided: false, branch: null };

const all_branches = (state = branches_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_ALL_BRANCHES_SUCCESS:
            return {
                ...state,
                allBranchesProvided: true,
                branches: payload.branches
            };
        case GET_ALL_BRANCHES_FAIL:
            return {
                ...state,
                allBranchesProvided: false,
                branches: null,
            };
        default:
            return state;
    }
}

const branch = (state = branch_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_BRANCH_SUCCESS:
            return {
                ...state,
                oneBranchProvided: true,
                branch: payload.me_as_user
            };
        case GET_BRANCH_FAIL:
            return {
                ...state,
                oneBranchProvided: false,
                branch: null,
            };
        default:
            return state;
    }
}

// eslint-disable-next-line import/no-anonymous-default-export
export {
    all_branches,
    branch,
};