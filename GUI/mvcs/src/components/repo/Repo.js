/* eslint-disable no-useless-rename */
import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getUserBranches, getUserCommits } from "../../actions/users";
import { useParams, Navigate, Link } from "react-router-dom";
import { getRepo } from "../../actions/repos";

const Repo = () => {
    const dispatch = useDispatch();
    let { repo_id } = useParams();

    
    const { user: current_user } = useSelector((state) => state.auth);
    const { oneRepoDataProvided: repoDataProvided, repo: repo } = useSelector(state => state.repo);
    const { allUserBranchesProvided: userBranchesProvided, user_branches: user_branches } = useSelector(state => state.user_branches);
    const { allUserCommitsProvided: userCommitsProvided, user_commits: user_commits } = useSelector(state => state.user_commits);

    const [dropdown, setDropdown] = useState(false);
    const toggleOpen = () => setDropdown(!dropdown);

    const [current_branch, setCurrentBranch] = useState(null);

    // Repo states
    const [my_repo, setMyRepo] = useState([]);
    const [repoDataLoaded, setRepoDataLoaded] = useState(false);
    const [repoDataGathered, setRepoDataGathered] = useState(false);

    // Branches states
    const [branches, setBranches] = useState([]);
    const [branchesDataLoaded, setBranchesDataLoaded] = useState(false);
    const [branchesDataGathered, setBranchesDataGathered] = useState(false);
    const [numOfBranches, setNumOfBranches] = useState(0);

    // Commits states
    const [commits, setCommits] = useState([]);
    const [commitsDataLoaded, setCommitsDataLoaded] = useState(false);
    const [commitsDataGathered, setCommitsDataGathered] = useState(false);
    const [numOfCommits, setNumOfCommits] = useState(0);

    // Users actions
    useEffect(() => {
        if (!repoDataLoaded) {
            dispatch(getRepo(repo_id));
            setRepoDataLoaded(repoDataProvided);
        }
    }, [dispatch, repoDataLoaded, repoDataProvided, repo_id]);

    useEffect(() => {
        if (repoDataLoaded && !repoDataGathered) {
            for (const [key, value] of Object.entries(repo))
                if (key === "data")
                    setMyRepo({ ...my_repo, ...value })
            if (Object.keys(my_repo).length > 0)
                setRepoDataGathered(true);
        }
    }, [repoDataLoaded, repoDataGathered, my_repo, repo]);

    // Branches Actions
    useEffect(() => {
        if (!branchesDataLoaded && repoDataProvided) {
            dispatch(getUserBranches(current_user.user_id));
            setBranchesDataLoaded(userBranchesProvided);
        }
    }, [dispatch, branchesDataLoaded, userBranchesProvided, current_user, repoDataProvided]);

    useEffect(() => {
        if (branchesDataLoaded && !branchesDataGathered) {
            for (const [key, value] of Object.entries(user_branches)){
                if (key === "data"){
                    setBranches({ ...branches, ...value })
                }
            }
            setBranchesDataGathered(true);
        }
    }, [branchesDataLoaded, branchesDataGathered, branches, user_branches]);

    useEffect(() => {
        if (repoDataGathered && branchesDataGathered) 
            setNumOfBranches(Object.keys(branches).length);
    }, [branches, repoDataGathered, branchesDataGathered]);

    // Commits Actions
    useEffect(() => {
        if (!commitsDataLoaded && repoDataProvided) {
            dispatch(getUserCommits(current_user.user_id));
            setCommitsDataLoaded(userCommitsProvided);
        }
    }, [dispatch, commitsDataLoaded, userCommitsProvided, current_user, repoDataProvided]);

    useEffect(() => {
        if (commitsDataLoaded && !commitsDataGathered) {
            for (const [key, value] of Object.entries(user_commits))
                if (key === "data")
                    setCommits({ ...commits, ...value })
            setCommitsDataGathered(true);
        }
    }, [commitsDataLoaded, commitsDataGathered, commits, user_commits]);

    useEffect(() => {
        if (repoDataGathered && commitsDataGathered){
            setNumOfCommits(Object.keys(commits).length);
        }
    }, [commits, repoDataGathered, commitsDataGathered]);


    if (!current_user) {
        return (<Navigate to="/" />);
    }

    return( true ?
        ( 
        <div className="container-fluid">
            <nav className="navbar navbar-dark navbar-expand-md bg-dark py-3">
                <div className="container">
                    <div className="collapse navbar-collapse flex-grow-0 order-md-first" id="navcol-6">
                        <div className="dropdown">
                            <button className="btn btn-primary dropdown-toggle" type="button" 
                                    data-bs-toggle="dropdown" aria-expanded="false" aria-haspopup="true"
                                    onClick={toggleOpen} >
                                {current_branch ? current_branch.name  : "Choose Branch"}
                            </button>          
                            <ul className={`dropdown-menu ${dropdown ? 'show' : ''}`} aria-labelledby="dropdownMenuButton">
                                {
                                    // eslint-disable-next-line array-callback-return
                                    Object.keys(branches).map( (key, index) => {
                                        let branch = branches[key][0];
                                        if(branch && branch.repo === my_repo.id)
                                            return (
                                                <li><div className="text-center"
                                                onClick={() => {setCurrentBranch(branch)}}
                                                onMouseLeave={(e) => {
                                                    e.target.style.border = '';
                                                }} onMouseOver={(e) => {
                                                    e.target.style.cursor = 'pointer';
                                                    e.target.style.border = '0.1rem outset pink';
                                                }}>
                                                {branch.name}
                                                </div></li>
                                            )
                                        }
                                    )
                                }
                            </ul>
                        </div>
                    </div>
                        <p className="text-light">{numOfBranches} <strong>Branches</strong> in the repo</p>
                        <p className="text-light">{numOfCommits}  <strong>Commits</strong> in the repo</p>
                    <div className="d-none d-md-block">
                        <Link className="btn btn-light me-2" role="button" href="#"> Branch setting </Link>
                        <Link className="btn btn-primary" role="button" href="#"> Add Branch </Link>
                    </div>
                </div>
            </nav>
                
            <div className="row">
                <div className="col-md-8">
                    <div className="row">
                        <div className="col-md-12">
                            {
                                // eslint-disable-next-line array-callback-return
                                Object.keys(commits).map( (key, index) => {
                                    let commit = commits[key][0];
                                    // console.log(current_branch.id ,commit.branch )
                                    // if(current_branch && current_branch.id === commit.branch){
                                        return (
                                            <div className="d-none d-md-block border border-dark text-center">
                                                <div className="mt-3">
                                                    <p> <strong> Date Created: </strong>{commit.date_created.split('T')[0]}</p>
                                                    <p> <strong> Commit File: </strong>{commit.unique_id}.tar.xz</p>
                                                </div>
                                                <Link className="btn btn-dark m-3" role="button" href="#"> Download Commit </Link>
                                                <Link className="btn btn-dark m-3" role="button" href="#"> Commit Setting </Link>
                                                <Link className="btn btn-primary"   role="button" href="#"> Show Files Tree </Link>
                                            </div>
                                        )
                                    // }
                                })
                            }
                        </div>
                    </div>
                </div>
                <div className="col-md-4">

                </div>
            </div>
        </div>
        )
        :
        (<div>Loading...</div>)
  );
};

export default Repo;