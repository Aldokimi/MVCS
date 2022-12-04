import {
    GET_ALL_BRANCHES_SUCCESS,
    GET_ALL_BRANCHES_FAIL,
    GET_BRANCH_SUCCESS,
    GET_BRANCH_FAIL,
    CREATE_BRANCH_SUCCESS,
    CREATE_BRANCH_FAIL,
    MODIFY_BRANCH_SUCCESS,
    MODIFY_BRANCH_FAIL,
    DELETE_BRANCH_SUCCESS,
    DELETE_BRANCH_FAIL,
} from "../actions/types";

const branches_initialState = { allBranchesProvided: false, branches: null };
const branch_initialState = { oneBranchProvided: false, branch: null };
const create_branch_initialState = { branchCreated: false, created_branch: null};
const modify_branch_initialState = { branchModified: false, modified_branch: null};
const delete_branch_initialState = { branchDeleted: false};

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

const create_branch = (state = create_branch_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case CREATE_BRANCH_SUCCESS:
            return {
                ...state,
                branchCreated: true,
                created_branch: payload.created_branc
            };
        case CREATE_BRANCH_FAIL:
            return {
                ...state,
                branchCreated: false,
                created_branch: null,
            };
        default:
            return state;
    }
}

const modify_branch = (state = modify_branch_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case MODIFY_BRANCH_SUCCESS:
            return {
                ...state,
                branchModified: true,
                modified_branch: payload.modified_branch
            };
        case MODIFY_BRANCH_FAIL:
            return {
                ...state,
                branchModified: false,
                modified_branch: null,
            };
        default:
            return state;
    }
}

const delete_branch = (state = delete_branch_initialState, action) => {
    const { type } = action;

    switch (type) {
        case DELETE_BRANCH_SUCCESS:
            return {
                ...state,
                branchDeleted: true,
            };
        case DELETE_BRANCH_FAIL:
            return {
                ...state,
                branchDeleted: false,
            };
        default:
            return state;
    }
}

// eslint-disable-next-line import/no-anonymous-default-export
export {
    all_branches,
    branch,
    create_branch,
    modify_branch,
    delete_branch,
};