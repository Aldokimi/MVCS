import axios from "axios";
// import authHeader from "./auth-header";

const API_URL = "http://localhost:8000/api/";

const getAllUsers = () => {
  return axios.get(API_URL + "users/");
};

// const getUserBoard = () => {
//   return axios.get(API_URL + "user", { headers: authHeader() });
// };

// const getModeratorBoard = () => {
//   return axios.get(API_URL + "mod", { headers: authHeader() });
// };

// const getAdminBoard = () => {
//   return axios.get(API_URL + "admin", { headers: authHeader() });
// };

// eslint-disable-next-line import/no-anonymous-default-export
export default {
  getAllUsers,
//   getUserBoard,
//   getModeratorBoard,
//   getAdminBoard,
};