document.addEventListener('DOMContentLoaded', async function () {
    const token = localStorage.getItem('access_token');

    // Kiểm tra sự tồn tại của token
    if (!token) {
        alert('Token không tồn tại! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../auth/login.html';
        }, 3000);
        return;
    }

    // Lấy thông tin tài khoản
    const accountInfo = await fetchAccountInfo(token);
    document.getElementById('ten_tk').value = accountInfo.taikhoan; // Đưa tên tài khoản vào ô input

    // Xử lý sự kiện submit form
    document.getElementById('change-password-form').addEventListener('submit', async function (e) {
        e.preventDefault();

        const newPassword = document.getElementById('matkhau_moi').value;
        const confirmNewPassword = document.getElementById('nhaplai_matkhau_moi').value;

        // Kiểm tra mật khẩu
        if (newPassword !== confirmNewPassword) {
            document.getElementById('password_error').style.display = 'block';
            return;
        }

        // Tạo payload cho việc cập nhật
        const payload = {
            matkhau: newPassword,
        };

        try {
            const response = await fetch(`http://localhost:8000/admin/accounts/username/${accountInfo.taikhoan}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorData = await response.json();
                alert(errorData.detail || 'Có lỗi xảy ra khi cập nhật tài khoản.');
                return;
            }

            alert('Cập nhật mật khẩu thành công!');
            // Có thể thêm logic để chuyển hướng hoặc làm gì đó khác
        } catch (error) {
            console.error('Lỗi khi cập nhật:', error);
            alert('Có lỗi xảy ra khi cập nhật tài khoản.');
        }
    });
});

// Hàm để lấy thông tin tài khoản từ API
async function fetchAccountInfo(token) {
    try {
        const response = await fetch('http://localhost:8000/auth/admin/me', {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('Không thể lấy thông tin tài khoản');
        }

        return await response.json();
    } catch (error) {
        console.error(error);
        alert('Có lỗi xảy ra khi lấy thông tin tài khoản.');
    }
}