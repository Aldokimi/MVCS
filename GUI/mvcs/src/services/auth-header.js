export default function authHeader() {
    const user = JSON.parse(localStorage.getItem('user'));

    if (user && user.access) {
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + user.access
        };
    } else {
        return {};
    }
}