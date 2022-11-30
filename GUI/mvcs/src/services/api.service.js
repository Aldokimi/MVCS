import axios from "axios";
import authHeader from "./auth-header";

const API_URL = "http://localhost:8000/api/";

// GET requests
const getAllUsers = () => {
  return axios.get(API_URL + "users/");
};

const getAllRepos = () => {
  return axios.get(API_URL + "repos/");
};

const getAllBranches = () => {
  return axios.get(API_URL + "branches/");
};

const getAllCommits = () => {
  return axios.get(API_URL + "commits/");
};

// Get with auth
const getUser = (id) => {
  return axios.get(API_URL + `users/${id}`, { headers: authHeader() });
}

const getRepo = (id) => {
  return axios.get(API_URL + `repos/${id}`, { headers: authHeader() });
}


// POST requests
const createRepository = () => {
  return axios.post(API_URL + "repos/", { headers: authHeader() });
}

// PUT requests
const modifyRepository = (id) => {
  return axios.put(API_URL + `repos/${id}`, { headers: authHeader() });
}

const modifyBranch = (id) => {
  return axios.put(API_URL + `branch/${id}`, { headers: authHeader() });
}

const modifyCommit = (id) => {
  return axios.put(API_URL + `commit/${id}`, { headers: authHeader() });
}

const modifyUser = (id) => {
  return axios.put(API_URL + `users/${id}`, { headers: authHeader() });
}

// DELETE requests
const deleteUser = (id) => {
  return axios.delete(API_URL + `users/${id}`, { headers: authHeader() })
}

const deleteRepository = (id) => {
  return axios.delete(API_URL + `repos/${id}`, { headers: authHeader() })
}

const deleteBranch = (id) => {
  return axios.delete(API_URL + `branches/${id}`, { headers: authHeader() })
}

const deleteCommit = (id) => {
  return axios.delete(API_URL + `commits/${id}`, { headers: authHeader() })
}


// eslint-disable-next-line import/no-anonymous-default-export
export default {
  getAllUsers,
  getAllRepos,
  getAllBranches,
  getAllCommits,
  getUser,
  getRepo,
  createRepository,
  modifyRepository,
  modifyBranch,
  modifyCommit,
  modifyUser,
  deleteUser,
  deleteRepository,
  deleteBranch,
  deleteCommit
};