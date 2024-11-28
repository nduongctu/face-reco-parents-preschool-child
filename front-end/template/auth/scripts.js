document.addEventListener('DOMContentLoaded', function() {
    const authForm = document.querySelector('.login-form form');
    const baseURL = 'http://localhost:8000';
    const endpoint = `${baseURL}/auth/login`;

    authForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                username: username,
                password: password
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.detail || 'An error occurred. Please try again.');
                });
            }
            return response.json();
        })
        .then(data => {
            localStorage.setItem('access_token', data.access_token);

            try {
                const tokenParts = data.access_token.split('.');
                if (tokenParts.length !== 3) {
                    throw new Error('Invalid token format.');
                }
                const payload = JSON.parse(atob(tokenParts[1]));
                const role = payload.quyen;

                switch (role) {
                    case 0:
                        window.location.href = '../manage/admin/ql_giaovien.html';
                        break;
                    case 1:
                        window.location.href = '../manage/giaovien/giaovien.html';
                        break;
                    case 2:
                        window.location.href = '../manage/hocsinh/hocsinh.html';
                        break;
                    default:
                        alert('Vai trò không xác định! Vui lòng liên hệ với quản trị viên.');
                }
            } catch (error) {
                console.error('Error decoding token!', error);
                alert('Có lỗi xảy ra khi giải mã token.');
            }
        })
        .catch(error => {
            console.error('Đã xảy ra lỗi!', error);
            alert(error.message);
        });
    });
});
