import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from 'react-router-dom';
import { getAllUsers } from "../../actions/users";

import user_image from '../../assets/user.png';

const Users = () => {
  const dispatch = useDispatch();
  let navigate = useNavigate();
  const { user: current_user } = useSelector((state) => state.auth);
  const { allUsersProvided: dpr, users: all_users } = useSelector(state => state.all_users);
  const [ users, setUsers ] = useState({});
  const [ dataLoaded, setDataLoaded ] = useState(false);
  const [ dataGathered, setDataGathered ] = useState(false);
  const [ searchUsers, setSearchUsers ] = useState({});

  useEffect(() => {
    if(!dataLoaded){
      dispatch(getAllUsers());
      setDataLoaded(dpr)
    }
  }, [dispatch, dataLoaded, dpr]);
  
  if(dataLoaded && !dataGathered){
    for (const [key, value] of Object.entries(all_users))
      if(key === "data")
        setUsers({...users, ...value})
    if(Object.keys(users).length > 0)
      setDataGathered(true);
  }

  // Search engin
  function match(string, substring) {
    var letters = [...string];
    return [...substring].every((x) => {
        var index = letters.indexOf(x);
        if (~index) {
            letters.splice(index, 1);
            return true;
        }
        return false;
    });
  };

  const search = (text) => {
    if(text === ""){
      setSearchUsers({});
      return null;
    }
    let search_elems = {}
    Object.keys(users).forEach( (key, index) => {
      let user = users[key];
      if(match(user.username, text)){
        search_elems[key] = user;
      };
    })
    setSearchUsers(search_elems);
  };

  let display_users = Object.keys(searchUsers).length === 0 ? users : searchUsers;
  
  return ( dataLoaded ? (
    <div className="container">
      <section className="text-center bg-light features-icons">
          <div className="row">
              <div className="col-md-10 col-lg-8 col-xl-7 mx-auto position-relative">
                  <form>
                      <div className="row">
                          <div className="col-12 col-md-11 mb-2 mb-md-0">
                            <input 
                            className="form-control form-control-lg" 
                            type="text" 
                            placeholder="Enter name of the user ..." 
                            onChange={(event)=> search(event.target.value)} />
                          </div>
                      </div>
                  </form>
              </div>
          </div>
      </section>
      <div className="container">
        {
          Object.keys(display_users).map( (key, index) => {
            let user = users[key];
            return (
              <div className="row">
                <div className="col-md-12">
                    <div className="card">
                        <div className="card-body">
                            <h4 className="card-title p-1">{user.username}</h4>
                            <div className="row">
                              <div className="col-md-5">
                                <img 
                                src={user.profile_picture ? user.profile_picture : user_image } alt="none" width={100} height={100}/>
                              </div>
                              <div className="col-md-4">
                                <p>
                                  {user.bio ?  user.bio : "No bio yet ... !" }
                                </p>
                              </div>
                              <div className="col-md-3">
                                <button className="btn btn-primary m-1" type="button" 
                                    onClick={() => navigate(`/${user.username}`)}>Show</button>
                                {
                                  (current_user.user_id === user.id) 
                                  ? <button className="btn btn-primary  m-1" 
                                      type="button" onClick={() => navigate("/profile")}>Profile</button> : ""
                                }
                              </div>
                            </div>
                        </div>
                    </div>
                </div>
              </div>
            )

          })
        }
      </div>
    </div>
    ) 
    : 
    (<div>Loading...</div>)
  );
};

export default Users;