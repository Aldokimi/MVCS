import React, { useState, useEffect, useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import user_image from '../../assets/user.png';
import { getAllUsers } from "../../actions/users";
import { getAllRepos } from "../../actions/repos";
import { useParams, Navigate, Link } from "react-router-dom";

const User = () => {

    let { username } = useParams();
    const dispatch = useDispatch();
    const { allUsersProvided: dpr, users: all_users } = useSelector(state => state.all_users);
    const { allReposProvided: adpr, repos: all_repos } = useSelector(state => state.all_repos);

    // Users states
    const [ users, setUsers ] = useState({});
    const [ usersDataLoaded, setUsersDataLoaded ] = useState(false);
    const [ usersDataGathered, setUsersDataGathered ] = useState(false);
    const [ targetUser, setTargetUser ] = useState(null);

    // Repositories states
    const [ repos, setRepos ] = useState({});
    const [ reposDataLoaded, setReposDataLoaded ] = useState(false);
    const [ reposDataGathered, setReposDataGathered ] = useState(false);
    const [ numOfContributions, setNumOfContributions ] = useState(0);
    const [ numOfRepos, setNumOfRepos ] = useState(0);

    // Get a username from an id
    const getUsername = useCallback((users_list, id) => {
        var out_user = {};
        Object.keys(users_list).forEach( (key, index) => {
            let user = users_list[key];
            if(user)
                if(user.id === id) out_user = user;
        });
        return out_user.username;
    }, []);


    // Users actions
    useEffect(() => {
        if(!usersDataLoaded){
            dispatch(getAllUsers());
            setUsersDataLoaded(dpr);
        }
    }, [dispatch, usersDataLoaded, dpr]);
    

    useEffect(() => {
        if(usersDataLoaded && !usersDataGathered){
            for (const [key, value] of Object.entries(all_users))
                if(key === "data")
                    setUsers({...users, ...value})
            if(Object.keys(users).length > 0)
                setUsersDataGathered(true);
            
            Object.keys(users).forEach( (key, index) => {
                let user = users[key];
                if(user.username === username){
                    setTargetUser(user);
                }
            });
        }
    }, [usersDataLoaded, usersDataGathered, targetUser, users, all_users, username]);

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

    useEffect(() => {
        if(usersDataGathered && reposDataGathered){
            let repoCnt = 0;
            let contCnt = 0;
            Object.keys(repos).forEach( (key, index) => {
                let repo = repos[key];
                if(repo.owner === targetUser.id)
                    repoCnt++;
                if(repo.contributors.includes(targetUser.id))
                    contCnt++;
            });
            setNumOfRepos(repoCnt);
            setNumOfContributions(contCnt);
        }
    }, [targetUser, repos, usersDataGathered, reposDataGathered]);

    if(usersDataLoaded && usersDataGathered){
        if(targetUser == null){
            return (<Navigate to="/" />);
        }
    }
    
    return ( usersDataLoaded && usersDataGathered ? 
        ( 
        <div id="wrapper">
            <div className="d-flex flex-column" id="content-wrapper">
                <div id="content">
                    <div className="container-fluid">
                        <div className="row mb-3">
                            <div className="col-lg-4">
                                <div className="card mb-3">
                                    <div className="card-body text-center shadow">
                                        <img className="rounded-circle mb-3 mt-4" 
                                             src={targetUser.profile_picture ? targetUser.profile_picture : user_image } 
                                             alt="user_profile_image " width="160" height="160" />
                                    </div>
                                </div>
                                <div className="card shadow mb-4">
                                    <div className="card-header py-3">
                                        <h6 className="text-primary fw-bold m-0">Statistics</h6>
                                    </div>
                                    <div className="card-body">
                                        <h4 className="small fw-bold">Number of Owned Repositories<span className="float-end"> { numOfRepos } </span></h4>
                                        <div className="progress progress-sm mb-3">
                                            <div 
                                                className="progress-bar bg-danger"
                                                aria-valuenow="20" aria-valuemin="0"
                                                aria-valuemax="100" style={{width: `${numOfRepos <= 10 ? numOfRepos * 10 : 100}%`}}> 
                                            </div>
                                        </div>
                                        <h4 className="small fw-bold">Number of Contributions<span className="float-end">{ numOfContributions }</span></h4>
                                        <div className="progress progress-sm mb-3">
                                            <div 
                                                className="progress-bar bg-warning"
                                                aria-valuenow="40" aria-valuemin="0"
                                                aria-valuemax="100" style={{width: `${numOfContributions <= 10 ? numOfContributions * 10 : 100}%`}}>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-lg-8">
                                <div className="row">
                                    <div className="col">
                                        <div className="card shadow mb-3">
                                            <div className="card-header py-3">
                                                <p className="text-primary m-0 fw-bold">User Data</p>
                                            </div>
                                            <div className="card-body">
                                                <div className="row">
                                                    <div className="col">
                                                        <div className="mb-3">
                                                            <label className="form-label" htmlFor="username"><strong>Username</strong></label>
                                                            <h6 className="text-secondary">{ targetUser.username }</h6>
                                                        </div>
                                                    </div>
                                                    <div className="col">
                                                        <div className="mb-3">
                                                            <label className="form-label" htmlFor="email"><strong>Email Address</strong></label>
                                                            <h6 className="text-secondary">{ targetUser.email }</h6>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="row">
                                                    <div className="col">
                                                        <div className="mb-3">
                                                            <label className="form-label" htmlFor="first_name"><strong>First Name</strong></label>
                                                            <h6 
                                                            className="text-secondary">{ 
                                                                targetUser.first_name ? targetUser.first_name : "Not Available" }</h6>
                                                        </div>
                                                    </div>
                                                    <div className="col">
                                                        <div className="mb-3">
                                                            <label className="form-label" htmlFor="last_name"><strong>Last Name</strong></label>
                                                            <h6 
                                                            className="text-secondary">{ 
                                                            targetUser.last_name ? targetUser.first_name : "Not Available" }</h6>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="mb-3"></div>
                                            </div>
                                        </div>
                                        <div className="card shadow">
                                            <div className="card-header py-3">
                                                <p className="text-primary m-0 fw-bold">Repositories</p>
                                            </div>
                                            <div className="card-body">
                                                <div className="row">
                                                    {
                                                        // eslint-disable-next-line array-callback-return
                                                        Object.keys(repos).map( (key, index) => {
                                                            let repo = repos[key];
                                                            if(targetUser.id === repo.owner)
                                                            return(
                                                                <div className="card-body col-4">
                                                                    <h5 className="card-title">{ repo.name }</h5>
                                                                    <p className="card-text">Created at: 
                                                                        <strong>{ repo.date_created.split('T')[0] }</strong>
                                                                    </p>
                                                                    <Link to={`/${targetUser.username}/${repo.name}`} 
                                                                        className="btn btn-primary">
                                                                        Visit
                                                                    </Link>
                                                                </div>
                                                            )
                                                        })
                                                    }
                                                </div>
                                                <div className="mb-3"></div>
                                            </div>
                                        </div>
                                        <div className="card shadow">
                                            <div className="card-header py-3">
                                                <p className="text-primary m-0 fw-bold">Contributions</p>
                                            </div>
                                            <div className="card-body">
                                                <div className="row">
                                                    {
                                                        // eslint-disable-next-line array-callback-return
                                                        Object.keys(repos).map( (key, index) => {
                                                            let repo = repos[key];
                                                            if(repo.contributors.includes(targetUser.id)){
                                                                let owner_username = getUsername(users, repo.owner);
                                                                return(
                                                                    <div className="card-body col-4">
                                                                        <h5 className="card-title">{ repo.name }</h5>
                                                                        <p className="card-text">Repository Owner:  
                                                                            <strong>{ " " + owner_username }</strong>
                                                                        </p>
                                                                        <p className="card-text">Created at: 
                                                                            <strong>{ " " + repo.date_created.split('T')[0] }</strong>
                                                                        </p>
                                                                        <Link to={`/${owner_username}/${repo.name}`} 
                                                                            className="btn btn-primary">
                                                                            Visit
                                                                        </Link>
                                                                    </div>
                                                                )
                                                            }
                                                        })
                                                    }
                                                </div>
                                                <div className="mb-3"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div><a className="border rounded d-inline scroll-to-top" href="#page-top"><i className="fas fa-angle-up"></i></a>
        </div>
        )
        :
        (<div>Loading...</div>)
  );
};

export default User;