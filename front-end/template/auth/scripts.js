document.addEventListener('DOMContentLoaded', function() {
    const authForm = document.querySelector('.login-form form'); // Chọn form bên trong khung login-form
    const baseURL = 'http://localhost:8000'; // Địa chỉ cơ sở của API
    const endpoint = baseURL + '/token'; // Endpoint dành cho đăng nhập

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
            // Đăng nhập thành công
            localStorage.setItem('access_token', data.access_token);

            // Giải mã token để lấy thông tin vai trò
            const tokenPayload = JSON.parse(atob(data.access_token.split('.')[1]));
            const role = tokenPayload.role;

            // Điều hướng dựa trên vai trò
            if (role === 0) {
                // Admin
                window.location.href = '../manage/admin.html'; // Điều hướng đến trang admin
            } else if (role === 1) {
                // Giáo viên
                window.location.href = '../manage/giaovien.html'; // Điều hướng đến trang giáo viên
            } else if (role === 2) {
                // Người dùng thông thường
                window.location.href = '../manage/user.html'; // Điều hướng đến trang user
            } else {
                // Vai trò không xác định
                alert('Vai trò không xác định! Vui lòng liên hệ với quản trị viên.');
            }

        })
        .catch(error => {
            console.error('There was an error!', error);
            alert(error.message);
        });
    });
});
