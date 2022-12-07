import axios from "axios";
import authHeader from "./auth-header";

const API_URL = "http://localhost:8000/api/v1/";

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
  return axios.get(API_URL + `users/${id}/`, { headers: authHeader() });
}

const getRepo = (id) => {
  return axios.get(API_URL + `repos/${id}/`, { headers: authHeader() });
}

const getBranch = (id) => {
  return axios.get(API_URL + `branches/${id}/`, { headers: authHeader() });
}

const getCommit = (id) => {
  return axios.get(API_URL + `commits/${id}/`, { headers: authHeader() });
}

const getReposForUser = (id) => {
  return axios.get(API_URL + `users/${id}/repos`, { headers: authHeader() });
}

const getBranchesForUser = (id) => {
  return axios.get(API_URL + `users/${id}/branches`, { headers: authHeader() });
}

const getCommitsForUser = (id) => {
  return axios.get(API_URL + `users/${id}/commits`, { headers: authHeader() });
}
// POST requests
const createRepository = (data) => {
  return axios.post(API_URL + "repos/", data,  { headers: authHeader() });
}

const createBranch = (data) => {
  return axios.post(API_URL + "repos/", data,  { headers: authHeader() });
}

// PUT requests
const modifyRepository = (id, data) => {
  return axios.put(API_URL + `repos/${id}/`, data, { headers: authHeader() });
}

const modifyBranch = (id, data) => {
  return axios.put(API_URL + `branch/${id}/`, data, { headers: authHeader() });
}

const modifyCommit = (id, data) => {
  return axios.put(API_URL + `commit/${id}/`, data, { headers: authHeader() });
}

const modifyUser = (id, data) => {
  return axios.put(API_URL + `users/${id}/`, data, { headers: authHeader() });
}

// DELETE requests
const deleteUser = (id) => {
  return axios.delete(API_URL + `users/${id}/`, { headers: authHeader() })
}

const deleteRepository = (id) => {
  return axios.delete(API_URL + `repos/${id}/`, { headers: authHeader() })
}

const deleteBranch = (id) => {
  return axios.delete(API_URL + `branches/${id}/`, { headers: authHeader() })
}

const deleteCommit = (id) => {
  return axios.delete(API_URL + `commits/${id}/`, { headers: authHeader() })
}


// eslint-disable-next-line import/no-anonymous-default-export
export default {
  getAllUsers,
  getAllRepos,
  getAllBranches,
  getAllCommits,
  getUser,
  getRepo,
  getBranch,
  getCommit,
  getReposForUser,
  getBranchesForUser,
  getCommitsForUser,
  createRepository,
  createBranch,
  modifyRepository,
  modifyBranch,
  modifyCommit,
  modifyUser,
  deleteUser,
  deleteRepository,
  deleteBranch,
  deleteCommit
};