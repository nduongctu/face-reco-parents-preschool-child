document.addEventListener('DOMContentLoaded', function() {
    const authForm = document.getElementById('authForm');
    const switchFormLink = document.getElementById('switchForm');
    const formTitle = document.getElementById('formTitle');

    // Xác định endpoint từ thuộc tính data-endpoint của form
    const baseURL = 'http://localhost:8000'; // Địa chỉ cơ sở của API
    const endpoint = baseURL + (formTitle.textContent === 'Login' ? '/token' : '/register');

    // Chuyển đổi giữa các trang đăng nhập và đăng ký
    switchFormLink.addEventListener('click', function(e) {
        e.preventDefault();
        if (formTitle.textContent === 'Login') {
            window.location.href = 'register.html'; // Điều hướng đến trang đăng ký
        } else {
            window.location.href = 'login.html'; // Điều hướng đến trang đăng nhập
        }
    });

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
            if (endpoint.endsWith('/token')) {
                // Đăng nhập thành công
                localStorage.setItem('access_token', data.access_token);
                alert('Đăng nhập thành công!');
                window.location.href = '/template/index.html'; // Điều hướng đến trang chính sau khi đăng nhập
            } else if (endpoint.endsWith('/register')) {
                // Đăng ký thành công
                alert('Đăng ký thành công! Vui lòng đăng nhập.');
                window.location.href = 'login.html'; // Điều hướng đến trang đăng nhập sau khi đăng ký
            }
        })
        .catch(error => {
            console.error('There was an error!', error);
            alert(error.message);
        });
    });
});
