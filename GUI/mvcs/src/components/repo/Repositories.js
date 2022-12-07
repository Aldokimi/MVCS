import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from 'react-router-dom';
import { getUser } from "../../actions/users";
import { getAllRepos } from "../../actions/repos";

const Repositories = () => {
    const dispatch = useDispatch();
    let navigate = useNavigate();
    const { user: current_user } = useSelector((state) => state.auth);
    // eslint-disable-next-line no-useless-rename
    const { userProvided: userDataProvided, user: user } = useSelector(state => state.user);
    // eslint-disable-next-line no-useless-rename
    const { allReposProvided: adpr, repos: all_repos } = useSelector(state => state.all_repos);
    // Repositories states
    const [repos, setRepos] = useState({});
    const [reposDataLoaded, setReposDataLoaded] = useState(false);
    const [reposDataGathered, setReposDataGathered] = useState(false);

    // User data 
    const [me_as_user, setMeAsUser] = useState({});
    const [userDataLoaded, setUserDataLoaded] = useState(false);
    const [userDataGathered, setUserDataGathered] = useState(false);
  
    // Users actions
    useEffect(() => {
        if (!userDataLoaded && current_user) {
            dispatch(getUser(current_user.user_id));
            setUserDataLoaded(userDataProvided);
        }
    }, [dispatch, userDataLoaded, userDataProvided, current_user]);

    useEffect(() => {
        if (userDataLoaded && !userDataGathered) {
            for (const [key, value] of Object.entries(user))
                if (key === "data")
                    setMeAsUser({ ...me_as_user, ...value })
            if (Object.keys(me_as_user).length > 0)
                    setUserDataGathered(true);
        }
    }, [userDataLoaded, userDataGathered, current_user, me_as_user, user]);

    // Repos Actions
    useEffect(() => {
        if(!reposDataLoaded){
            dispatch(getAllRepos());
            setReposDataLoaded(adpr);
        }
    }, [dispatch, reposDataLoaded, adpr]);

    useEffect(() => {
        if(reposDataLoaded && !reposDataGathered){
            for (const [key, value] of Object.entries(all_repos)){
                if(key === "data"){
                    setRepos({...repos, ...value})
                }
            }
            if(Object.keys(repos).length > 0){
                setReposDataGathered(true);
            }
        }
    }, [reposDataLoaded, reposDataGathered, repos, all_repos]);

    return ( reposDataGathered ? (
        <div className="container">
            <div className="container">
                <div className="row">  
                    <h2 className="text-success"> Owned Repositories: </h2>
                {
                Object.keys(repos).map( (key, index) => {
                    let repo = repos[key];
                    if(!(current_user.user_id === repo.owner)) return <div></div>
                    return (
                        <div className="col-md-3">
                            <div className="card">
                                <div className="card-body">
                                    <h4 className="card-title p-1">{repo.name}</h4>
                                    <div className="mb-3">
                                        <h6 className="text-success">Date Created: </h6>
                                        <small>{repo.date_created.split('T')[0]}</small>
                                    </div>
                                    <button className="btn btn-primary m-1" type="button"
                                        onClick={() => navigate(`/repositories/${repo.id}`)}>Show</button>
                                </div>
                            </div>
                        </div>
                    )})
                }
                </div>
                <div className="row">  
                    <h2 className="text-success"> Repositories you contributed to: </h2>
                {
                Object.keys(repos).map( (key, index) => {
                    let repo = repos[key];
                    if(!repo.contributors.includes(current_user.user_id)) return <div></div>
                    return (
                        <div className="col-md-3">
                            <div className="card">
                                <div className="card-body">
                                    <h4 className="card-title p-1">{repo.name}</h4>
                                    <div className="mb-3">
                                        <h6 className="text-success">Date Created: </h6>
                                        <small>{repo.date_created.split('T')[0]}</small>
                                    </div>
                                    <button className="btn btn-primary m-1" type="button"
                                        onClick={() => navigate(`/repositories/${repo.id}`)}>Show</button>
                                </div>
                            </div>
                        </div>
                    )})
                }
                </div>
            </div>
        </div>
        )
        :
        (<div>Loading...</div>)
    );
};

export default Repositories;