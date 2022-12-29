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
} from "../actions/types";

const commits_initialState = { allCommitsProvided: false, commits: null };
const commit_initialState = { oneCommitProvided: false, commit: null };
const commit_file_tree_initialState = { commitFileTreeProvided: false, commit_file_tree: null };
const modify_commit_initialState = { commitModified: false, modified_commit: null};
const delete_commit_initialState = { commitDeleted: false};

const all_commits = (state = commits_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_ALL_COMMITS_SUCCESS:
            return {
                ...state,
                allCommitsProvided: true,
                commits: payload.commits
            };
        case GET_ALL_COMMITS_FAIL:
            return {
                ...state,
                allCommitsProvided: false,
                commits: null,
            };
        default:
            return state;
    }
}

const commit = (state = commit_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_COMMIT_SUCCESS:
            return {
                ...state,
                oneCommitProvided: true,
                commit: payload.commit
            };
        case GET_COMMIT_FAIL:
            return {
                ...state,
                oneCommitProvided: false,
                commit: null,
            };
        default:
            return state;
    }
}

const commit_file_tree = (state = commit_file_tree_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case GET_COMMIT_FILE_TREE_SUCCESS:
            return {
                ...state,
                commitFileTreeProvided: true,
                commit_file_tree: payload.commit_file_tree
            };
        case GET_COMMIT_FILE_TREE_FAIL:
            return {
                ...state,
                commitFileTreeProvided: false,
                commit: null,
            };
        default:
            return state;
    }
}

const modify_commit = (state = modify_commit_initialState, action) => {
    const { type, payload } = action;

    switch (type) {
        case MODIFY_COMMIT_SUCCESS:
            return {
                ...state,
                commitModified: true,
                modified_commit: payload.modified_commit
            };
        case MODIFY_COMMIT_FAIL:
            return {
                ...state,
                commitModified: false,
                modified_commit: null,
            };
        default:
            return state;
    }
}

const delete_commit = (state = delete_commit_initialState, action) => {
    const { type } = action;

    switch (type) {
        case DELETE_COMMIT_SUCCESS:
            return {
                ...state,
                commitDeleted: true,
            };
        case DELETE_COMMIT_FAIL:
            return {
                ...state,
                commitDeleted: false,
            };
        default:
            return state;
    }
}

// eslint-disable-next-line import/no-anonymous-default-export
export {
    all_commits,
    commit,
    modify_commit,
    delete_commit,
    commit_file_tree,
};