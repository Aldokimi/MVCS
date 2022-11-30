import { combineReducers } from "redux";
import auth from "./auth";
import { all_users, user } from "./users"
import message from "./message";

export default combineReducers({
    auth,
    all_users,
    user,
    message,
});