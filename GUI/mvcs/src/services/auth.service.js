import axios from "axios";

const API_URL = "http://localhost:8000/api/";

const register = async (username, email, password, password2) => {
    return await axios.post(API_URL + "register/", {
        username,
        email,
        password,
        password2,
    });
};

const login = async (email, password) => {
    const response = await axios
        .post(API_URL + "login/", {
            email,
            password,
        });
    if (response.data.access) {
        localStorage.setItem("user", JSON.stringify(response.data));
    }
    return response.data;
};

const logout = () => {
    localStorage.removeItem("user");
    return axios.post(API_URL + "register/", {})
};

// eslint-disable-next-line import/no-anonymous-default-export
export default { register, login, logout };