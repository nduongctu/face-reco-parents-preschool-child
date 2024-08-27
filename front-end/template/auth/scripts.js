document.addEventListener('DOMContentLoaded', function() {
    const authForm = document.querySelector('.login-form form');
    const baseURL = 'http://localhost:8000';
    const endpoint = baseURL + '/token';

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
                const payload = atob(tokenParts[1]);
                const tokenPayload = JSON.parse(payload);
                const role = tokenPayload.quyen;

                if (role === 0) {
                    window.location.href = '../manage/admin.html';
                } else if (role === 1) {
                    window.location.href = '../manage/giaovien.html';
                } else if (role === 2) {
                    window.location.href = '../manage/hocsinh.html';
                } else {
                    alert('Vai trò không xác định! Vui lòng liên hệ với quản trị viên.');
                }
            } catch (error) {
                console.error('Error decoding token!', error);
                alert('Có lỗi xảy ra khi giải mã token.');
            }
        })
        .catch(error => {
            console.error('There was an error!', error);
            alert(error.message);
        });
    });
});
