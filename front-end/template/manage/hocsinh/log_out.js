async function logout() {
    const token = localStorage.getItem('access_token'); // Lấy token từ local storage với key đúng
    if (!token) {
        alert('Không có token, vui lòng đăng nhập lại.');
        return; // Dừng nếu không có token
    }

    try {
        const response = await fetch('http://localhost:8000/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // Sử dụng token đã lấy
            }
        });

        if (!response.ok) {
            const errorData = await response.json(); // Lấy thông tin lỗi từ server
            throw new Error(errorData.detail || 'Đăng xuất thất bại');
        }

        alert('Đăng xuất thành công!');
        localStorage.removeItem('access_token'); // Xóa token khỏi local storage
        window.location.href = '../../auth/login.html'; // Chuyển hướng đến trang đăng nhập
    } catch (error) {
        alert(error.message); // Hiển thị lỗi nếu có
        console.error('Lỗi khi đăng xuất:', error); // Log lỗi ra console để dễ theo dõi
    }
}

// Chờ DOM được tải xong trước khi thêm sự kiện
document.addEventListener('DOMContentLoaded', function () {
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', async function (event) {
            event.preventDefault(); // Ngăn chặn hành vi mặc định của thẻ <a>
            await logout(); // Gọi hàm logout và chờ nó hoàn tất
        });
    } else {
        console.error('Phần tử với ID "logout-button" không tồn tại!');
    }
});
