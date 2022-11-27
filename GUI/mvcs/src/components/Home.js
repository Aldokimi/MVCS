import React, { useState, useEffect } from "react";

import UserService from "../services/user.service";

const Home = () => {
  const [content, setContent] = useState("");

  useEffect(() => {
    UserService.getAllUsers().then(
      (response) => {
        setContent(response.data);
      },
      (error) => {
        const _content =
          (error.response && error.response.data) ||
          error.message ||
          error.toString();

        setContent(_content);
      }
    );
  }, []);

  return (
    <div className="container">
      <header className="jumbotron">
        <h3>Users: </h3>
        {
            Object.keys(content).map((user_key, user_value) => {
                let user = content[`${user_value}`]
                return (<li>{user.username}</li>)
            })
        }
      </header>
    </div>
  );
};

export default Home;