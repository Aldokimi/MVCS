import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import user_image from '../../assets/user.png';
import { getAllUsers } from "../../actions/users";
import { useParams, Navigate } from "react-router-dom";

const User = () => {

    let { username } = useParams();
    const dispatch = useDispatch();
    const { dataProvided: dpr, users: all_users } = useSelector(state => state.all_users);
    const [ users, setUsers ] = useState({});
    const [ dataLoaded, setDataLoaded ] = useState(false);
    const [ dataGathered, setDataGathered ] = useState(false);
    const [ targetUser, setTargetUser ] = useState(null);

    useEffect(() => {
        if(!dataLoaded){
            dispatch(getAllUsers());
            setDataLoaded(dpr)
        }
    }, [dispatch, dataLoaded, dpr]);
    

    useEffect(() => {
        if(dataLoaded && !dataGathered){
            for (const [key, value] of Object.entries(all_users))
                if(key === "data")
                    setUsers({...users, ...value})
            if(Object.keys(users).length > 0)
                setDataGathered(true);
            
            Object.keys(users).forEach( (key, index) => {
                let user = users[key];
                if(user.username === username){
                    setTargetUser(user);
                }
            });
        }
    }, [dataLoaded, dataGathered, targetUser, users, all_users, username]);

    if(dataLoaded && dataGathered){
        if(targetUser == null){
            return (<Navigate to="/" />);
        }
    }

    return ( dataLoaded && dataGathered ? 
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
                                        <h4 className="small fw-bold">Server migration<span className="float-end">20%</span></h4>
                                        <div className="progress progress-sm mb-3">
                                            <div className="progress-bar bg-danger" aria-valuenow="20" aria-valuemin="0" aria-valuemax="100" style={{width: "20%"}}><span className="visually-hidden">20%</span></div>
                                        </div>
                                        <h4 className="small fw-bold">Sales tracking<span className="float-end">40%</span></h4>
                                        <div className="progress progress-sm mb-3">
                                            <div className="progress-bar bg-warning" aria-valuenow="40" aria-valuemin="0" aria-valuemax="100" style={{width: "40%"}}><span className="visually-hidden">40%</span></div>
                                        </div>
                                        <h4 className="small fw-bold">Customer Database<span className="float-end">60%</span></h4>
                                        <div className="progress progress-sm mb-3">
                                            <div className="progress-bar bg-primary" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100" style={{width: "60%"}}><span className="visually-hidden">60%</span></div>
                                        </div>
                                        <h4 className="small fw-bold">Payout Details<span className="float-end">80%</span></h4>
                                        <div className="progress progress-sm mb-3">
                                            <div className="progress-bar bg-info" aria-valuenow="80" aria-valuemin="0" aria-valuemax="100" style={{width: "80%"}}><span className="visually-hidden">80%</span></div>
                                        </div>
                                        <h4 className="small fw-bold">Account setup<span className="float-end">Complete!</span></h4>
                                        <div className="progress progress-sm mb-3">
                                            <div className="progress-bar bg-success" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style={{width: "100%"}}><span className="visually-hidden">100%</span></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-lg-8">
                                <div className="row mb-3 d-none">
                                    <div className="col">
                                        <div className="card text-white bg-primary shadow">
                                            <div className="card-body">
                                                <div className="row mb-2">
                                                    <div className="col">
                                                        <p className="m-0">Peformance</p>
                                                        <p className="m-0"><strong>65.2%</strong></p>
                                                    </div>
                                                    <div className="col-auto"><i className="fas fa-rocket fa-2x"></i></div>
                                                </div>
                                                <p className="text-white-50 small m-0"><i className="fas fa-arrow-up"></i>&nbsp;5% since last month</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="col">
                                        <div className="card text-white bg-success shadow">
                                            <div className="card-body">
                                                <div className="row mb-2">
                                                    <div className="col">
                                                        <p className="m-0">Peformance</p>
                                                        <p className="m-0"><strong>65.2%</strong></p>
                                                    </div>
                                                    <div className="col-auto"><i className="fas fa-rocket fa-2x"></i></div>
                                                </div>
                                                <p className="text-white-50 small m-0"><i className="fas fa-arrow-up"></i>&nbsp;5% since last month</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
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
                                                            <h6 className="text-secondary">{ targetUser.first_name ? targetUser.first_name : "Not Available" }</h6>
                                                        </div>
                                                    </div>
                                                    <div className="col">
                                                        <div className="mb-3">
                                                            <label className="form-label" htmlFor="last_name"><strong>Last Name</strong></label>
                                                            <h6 className="text-secondary">{ targetUser.last_name ? targetUser.first_name : "Not Available" }</h6>
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
                                                    <div className="col-4">
                                                        <div className="mb-3"><label className="form-label" htmlFor="city"><strong>City</strong></label></div>
                                                    </div>
                                                    <div className="col-4">
                                                        <div className="mb-3"><label className="form-label" htmlFor="country"><strong>Country</strong></label></div>
                                                    </div>
                                                    <div className="col-4">
                                                        <div className="mb-3"><label className="form-label" htmlFor="country"><strong>Country</strong></label></div>
                                                    </div>
                                                    <div className="col-4">
                                                        <div className="mb-3"><label className="form-label" htmlFor="country"><strong>Country</strong></label></div>
                                                    </div>
                                                    <div className="col-4">
                                                        <div className="mb-3"><label className="form-label" htmlFor="country"><strong>Country</strong></label></div>
                                                    </div>
                                                </div>
                                                <div className="mb-3"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="card shadow mb-5">
                            <div className="card-body"></div>
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