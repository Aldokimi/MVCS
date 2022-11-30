import { useNavigate } from 'react-router-dom';

const PageNotFound = () => {
    let navigate = useNavigate();

    return (
        <div className="container d-flex flex-column align-items-center py-4 py-xl-5">
            <div className="row gy-4 w-100" style={{ maxWidth: "800px;" }}>
                <div className="col-12">
                    <div className="card">
                        <div className="text-center d-flex flex-column justify-content-center align-items-center p-5">
                            <h4>PAGE NOT FOUND (404)</h4>
                            <p>This page might have been deleted or the URL has changed!</p>
                            <button className="btn btn-primary" type="button" onClick={() => navigate("/")}>
                                Home
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default PageNotFound;