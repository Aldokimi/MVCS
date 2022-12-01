import {
    GET_ALL_COMMITS_SUCCESS,
    GET_ALL_COMMITS_FAIL,
    GET_COMMIT_SUCCESS,
    GET_COMMIT_FAIL,
    MODIFY_COMMIT_SUCCESS,
    MODIFY_COMMIT_FAIL,
    DELETE_COMMIT_SUCCESS,
    DELETE_COMMIT_FAIL,
} from "../actions/types";

const commits_initialState = { allCommitsProvided: false, commits: null };
const commit_initialState = { oneCommitProvided: false, commit: null };

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

// eslint-disable-next-line import/no-anonymous-default-export
export {
    all_commits,
    commit,
};