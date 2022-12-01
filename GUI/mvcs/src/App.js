import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { Routes, Route, useLocation } from "react-router-dom";
import { clearMessage } from "./actions/message";

import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

import Login from "./components/auth/Login";
import Register from "./components/auth/Register";
import Home from "./components/Home";
import Profile from "./components/user/Profile";
import NavBar from "./components/layout/NavBar"
import Footer from "./components/layout/Footer";
import PageNotFound from "./components/layout/PageNotFound";
import Users from "./components/user/Users";
import User from "./components/user/User";



const App = () => {
  const dispatch = useDispatch();

  let location = useLocation();

  useEffect(() => {
    if (["/login", "/register"].includes(location.pathname)) {
      dispatch(clearMessage()); // clear message when changing location
    }
  }, [dispatch, location]);


  return (
    <div className="page-container">
      <NavBar />
      <div className="content-wrap">
        <div className="container mt-3">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/home" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/users" element={<Users />} />
            <Route path="/:username" element={<User />} />
            <Route path="/*" element={<PageNotFound />} />
          </Routes>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default App;