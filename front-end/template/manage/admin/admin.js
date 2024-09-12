document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('access_token');

    fetch('http://localhost:8000/users/me', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                // Hiển thị thông báo lỗi nếu không có quyền truy cập
                alert('Không có quyền truy cập! Vui lòng đăng nhập lại.');
                // Chuyển hướng về trang đăng nhập sau khi thông báo
                setTimeout(() => {
                    window.location.href = '../auth/login.html';
                }, 3000);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.quyen !== 0) { // Kiểm tra quyền
            alert('Không có quyền truy cập! Vui lòng đăng nhập lại.');
            // Chuyển hướng về trang đăng nhập sau khi thông báo
            setTimeout(() => {
                window.location.href = '../auth/login.html';
            }, 3000);
        }
    })
    .catch(error => {
        console.error('Error fetching user info:', error);
        // Hiển thị thông báo lỗi nếu có lỗi
        alert('Có lỗi xảy ra! Vui lòng đăng nhập lại.');
        // Chuyển hướng về trang đăng nhập sau khi thông báo
        setTimeout(() => {
            window.location.href = '../auth/login.html';
        }, 3000);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');

    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('open');
    });
});