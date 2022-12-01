/* eslint-disable no-useless-rename */
import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import user_image from '../../assets/user.png';
import { getUser, getUserBranches, getUserCommits, getUserRepos } from "../../actions/users";
import { Navigate } from "react-router-dom";

const Profile = () => {
  // Redux data
  const dispatch = useDispatch();
  const { user: current_user } = useSelector((state) => state.auth);
  const { userProvided: userDataProvided, user: user } = useSelector(state => state.user);
  const { allUserReposProvided: userReposProvided, user_repos: user_repos } = useSelector(state => state.user_repos);
  const { allBranchesProvided: userBranchesProvided, user_branches: user_branches } = useSelector(state => state.user_branches);
  const { allCommitsProvided: userCommitsProvided, user_commits: user_commits } = useSelector(state => state.user_commits);

  // Users states
  const [me_as_user, setMeAsUser] = useState({});
  const [userDataLoaded, setUserDataLoaded] = useState(false);
  const [userDataGathered, setUserDataGathered] = useState(false);

  // Repositories states
  const [repos, setRepos] = useState({});
  const [reposDataLoaded, setReposDataLoaded] = useState(false);
  const [reposDataGathered, setReposDataGathered] = useState(false);
  const [numOfRepos, setNumOfRepos] = useState(0);


  // Branches states
  const [branches, setBranches] = useState({});
  const [branchesDataLoaded, setBranchesDataLoaded] = useState(false);
  const [branchesDataGathered, setBranchesDataGathered] = useState(false);
  const [numOfBranches, setNumOfBranches] = useState(0);

  // Commits states
  const [commits, setCommits] = useState({});
  const [commitsDataLoaded, setCommitsDataLoaded] = useState(false);
  const [commitsDataGathered, setCommitsDataGathered] = useState(false);
  const [numOfCommits, setNumOfCommits] = useState(0);

  // Data Modification
  const [modify, setModify] = useState(false);

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
    if (!reposDataLoaded && userDataProvided) {
      dispatch(getUserRepos(current_user.user_id));
      setReposDataLoaded(userReposProvided);
    }
  }, [dispatch, reposDataLoaded, userReposProvided, current_user, userDataProvided, me_as_user]);

  useEffect(() => {
    if (reposDataLoaded && !reposDataGathered) {
      for (const [key, value] of Object.entries(user_repos)) {
        if (key === "data") {
          setRepos({ ...repos, ...value })
        }
      }
      setReposDataGathered(true);
    }
  }, [reposDataLoaded, reposDataGathered, repos, user_repos]);

  useEffect(() => {
    if (userDataGathered && reposDataGathered) {
      let repoCnt = 0;
      Object.keys(repos).forEach((key, index) => { repoCnt++; });
      setNumOfRepos(repoCnt);
    }
  }, [repos, userDataGathered, reposDataGathered]);

  // Branches Actions
  useEffect(() => {
    if (!branchesDataLoaded && userDataProvided) {
      dispatch(getUserBranches(current_user.user_id));
      setBranchesDataLoaded(userBranchesProvided);
    }
  }, [dispatch, branchesDataLoaded, userBranchesProvided, current_user, userDataProvided]);

  useEffect(() => {
    if (branchesDataLoaded && !branchesDataGathered) {
      for (const [key, value] of Object.entries(user_branches))
        if (key === "data")
          setBranches({ ...branches, ...value })
      setBranchesDataGathered(true);
    }
  }, [branchesDataLoaded, branchesDataGathered, branches, user_branches]);

  useEffect(() => {
    if (userDataGathered && branchesDataGathered) {
      let branchesCnt = 0;
      Object.keys(branches).forEach((key, index) => {branchesCnt++; });
      setNumOfBranches(branchesCnt);
    }
  }, [current_user, branches, userDataGathered, branchesDataGathered]);

  // Commits Actions
  useEffect(() => {
    if (!commitsDataLoaded && userDataProvided) {
      dispatch(getUserCommits(current_user.user_id));
      setCommitsDataLoaded(userCommitsProvided);
    }
  }, [dispatch, commitsDataLoaded, userCommitsProvided, current_user, userDataProvided]);

  useEffect(() => {
    if (commitsDataLoaded && !commitsDataGathered) {
      for (const [key, value] of Object.entries(user_commits))
        if (key === "data")
          setCommits({ ...commits, ...value })
      setCommitsDataGathered(true);
    }
  }, [commitsDataLoaded, commitsDataGathered, commits, user_commits]);

  useEffect(() => {
    if (userDataGathered && commitsDataGathered) {
      let commitsCnt = 0;
      Object.keys(commits).forEach((key, index) => { commitsCnt++; });
      setNumOfCommits(commitsCnt);
    }
  }, [current_user, commits, userDataGathered, commitsDataGathered]);

  if (!current_user) {
    return (<Navigate to="/" />);
  }

  return ( (userDataGathered) ? ( 
    <div id="wrapper">
      <div className="d-flex flex-column" id="content-wrapper">
        <div id="content">
          <div className="container-fluid">
            <h3 className="text-dark mb-4">Profile</h3>
            <div className="row mb-3">
              <div className="col-lg-4">
                <div className="card mb-3">
                  <div className="card-body text-center shadow">
                    <img 
                    className="rounded-circle mb-3 mt-4" 
                    src={me_as_user.profile_picture ? me_as_user.profile_picture : user_image } 
                    alt="img not found" width="160" height="160" />
                    <div className="mb-3">
                      <button className="btn btn-primary btn-sm" type="button">Change Photo</button>
                    </div>
                  </div>
                </div>
                <div className="card shadow mb-4">
                  <div className="card-header py-3">
                    <h6 className="text-primary fw-bold m-0">Statistics</h6>
                  </div>
                  <div className="card-body">
                    <h4 className="small fw-bold">Number of Repositories<span className="float-end">{numOfRepos}</span></h4>
                    <div className="progress progress-sm mb-3">
                      <div className="progress-bar bg-danger" 
                      aria-valuenow="20" aria-valuemin="0" aria-valuemax="100" style={{ width: `${numOfRepos < 10 ? numOfRepos : 100}%` }}>
                        <span className="visually-hidden">20%</span>
                      </div>
                    </div>
                    <h4 className="small fw-bold">Number of Branches<span className="float-end">{numOfBranches}</span></h4>
                    <div className="progress progress-sm mb-3">
                      <div className="progress-bar bg-warning" 
                      aria-valuenow="40" aria-valuemin="0" aria-valuemax="100" style={{ width: `${numOfBranches < 50 ? numOfBranches : 100}%` }}>
                        <span className="visually-hidden">40%</span>
                      </div>
                    </div>
                    <h4 className="small fw-bold">Number of Commits<span className="float-end">{numOfCommits}</span></h4>
                    <div className="progress progress-sm mb-3">
                      <div className="progress-bar bg-primary" 
                      aria-valuenow="60" aria-valuemin="0" aria-valuemax="100" style={{ width: `${numOfCommits < 10 ? numOfCommits : 100}%` }}>
                        <span className="visually-hidden">60%</span>
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
                        <p className="text-primary m-0 fw-bold">User Settings</p>
                      </div>
                      <div className="card-body">
                        <form>
                          <div className="row">
                            <div className="col">
                              <div className="mb-3">
                                <label className="form-label" htmlFor="username"><strong>Username</strong></label>
                                {modify ? 
                                  <input className="form-control" type="text" id="username" 
                                  placeholder={ me_as_user.username } name="username" value={ me_as_user.username } />
                                :
                                  <h6>{ me_as_user.username }</h6>
                                }
                              </div>
                            </div>
                            <div className="col">
                              <div className="mb-3">
                                <label className="form-label" htmlFor="email"><strong>Email Address</strong></label>
                                {console.log(me_as_user)}
                                {modify ? 
                                  <input className="form-control" type="email" id="email" 
                                  placeholder={ me_as_user.email } name="email" value={ me_as_user.email } />
                                  :
                                  <h6>{ me_as_user.email }</h6>
                                }
                              </div>
                            </div>
                          </div>
                          <div className="row">
                            <div className="col">
                              <div className="mb-3">
                                <label className="form-label" htmlFor="first_name"><strong>First Name</strong></label>
                                {modify ? 
                                  <input className="form-control" type="text" id="first_name" 
                                  placeholder={ me_as_user.first_name } name="first_name" value={ me_as_user.first_name } />
                                  :
                                  <h6>{ me_as_user.first_name ? me_as_user.first_name : "Not sat yet" }</h6>
                                }
                              </div>
                            </div>
                            <div className="col">
                              <div className="mb-3">
                                <label className="form-label" htmlFor="last_name"><strong>Last Name</strong></label>
                                {modify ? 
                                  <input className="form-control" type="text" id="last_name" 
                                  placeholder={ me_as_user.last_name } name="last_name" value={ me_as_user.last_name } />
                                  :
                                  <h6>{ me_as_user.last_name ? me_as_user.last_name : "Not sat yet" }</h6>
                                }
                              </div>
                            </div>
                            <div className="col">
                              <div className="mb-3">
                                <label className="form-label" htmlFor="date_of_birth"><strong>Date of Birth</strong></label>
                                {modify ? 
                                  <input className="form-control" type="date" id="date_of_birth" 
                                  placeholder={ me_as_user.data_of_birth } name="date_of_birth" value={ me_as_user.data_of_birth } />
                                  :
                                  <h6>{ me_as_user.data_of_birth ? me_as_user.data_of_birth.split('T')[0] : "Not sat yet" }</h6>
                                }
                              </div>
                            </div>
                          </div>
                          <div className="row">
                            <div className="col-12">
                              <div className="mb-3">
                                <label className="form-label" htmlFor="first_name"><strong>Bio</strong></label>
                                {modify ? 
                                  <textarea className="form-control" rows="4" name="bio" 
                                  placeholder="hello" value={me_as_user.bio}></textarea>
                                  :
                                  <h6>{ me_as_user.bio ? me_as_user.bio : "Not sat yet" }</h6>
                                }
                              </div>
                            </div>
                          </div>
                          <div className="mb-3">
                            { modify ?
                              <button className="btn btn-danger btn-sm" onClick={(e) => {
                                e.preventDefault();
                                setModify(false);
                              }}>Save Settings</button>
                            :
                              <button className="btn btn-primary btn-sm" onClick={(e) => {
                                e.preventDefault();
                                setModify(true);
                              }}>change Settings</button>
                            }
                          </div>
                        </form>
                      </div>
                    </div>
                    <div className="card shadow">
                      <div className="card-header py-3">
                        <p className="text-primary m-0 fw-bold">General Data</p>
                      </div>
                      <div className="card-body">
                        <div className="row">
                          <div className="col">
                            <div className="mb-3">
                              <h6 className="text-success">Date Joined: </h6>
                              <small>{me_as_user.date_joined.split('T')[0]}</small>
                            </div>
                          </div>
                          <div className="col">
                            <div className="mb-3">
                              <h6 className="text-success">Last Login: </h6>
                              <small>{me_as_user.last_login.split('T')[0]}</small>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="card shadow mb-5">
              <div className="card-header py-3">
                <p className="text-primary m-0 fw-bold">Public Key Setting</p>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-12">
                    <form>
                      <div className="mb-3">
                        <label className="form-label" htmlFor="signature"><strong>Signature</strong>
                          <br />
                        </label><textarea className="form-control" id="signature" rows="4" name="signature"></textarea>
                      </div>
                      <div className="mb-3"><button className="btn btn-primary btn-sm" type="submit">Save Settings</button></div>
                    </form>
                  </div>
                  <div className="mb-6">
                    <div className="form-check form-switch">
                      <p className="text-danger">* You need to upload your public key so you can clone the repositories and use the MVCS cli application. </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div><a className="border rounded d-inline scroll-to-top" href="#page-top"><i className="fas fa-angle-up"></i></a>
    </div>) 
    :
    (<div>Loading...</div>)
  );
};

export default Profile;