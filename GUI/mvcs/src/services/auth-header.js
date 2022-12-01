export default function authHeader() {
    const user = JSON.parse(localStorage.getItem('user'));

    if (user && user.access) {
        return {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': 'Bearer ' + user.access
        };
    } else {
        return {};
    }
}