document.addEventListener('DOMContentLoaded', function () {
    const token = localStorage.getItem('access_token');

    if (!token) {
        alert('Token không tồn tại! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../../auth/login.html';
        }, 3000);
        return;
    }

    document.getElementById('add-student-form').addEventListener('submit', function (event) {
        event.preventDefault();

        const ten_hs = document.getElementById('ten_hs').value;
        const gioitinh_hs = document.getElementById('gioitinh_hs').value;
        const ngaysinh_hs = document.getElementById('ngaysinh_hs').value;

        // Kiểm tra độ dài số điện thoại và địa chỉ đã được loại bỏ

        fetch('http://localhost:8000/admin/students', { // Cập nhật URL API cho học sinh
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ten_hs,
                gioitinh_hs,
                ngaysinh_hs
            })
        })
        .then(response => {
            if (response.ok) {
                alert('Thêm học sinh thành công!');
                window.location.href = '../ql_hocsinh.html'; // Chuyển hướng đến trang quản lý học sinh
            } else {
                return response.json().then(data => {
                    throw new Error(data.detail || 'Có lỗi xảy ra khi thêm học sinh.');
                });
            }
        })
        .catch(error => {
            console.error('Lỗi khi thêm học sinh:', error);
            alert(error.message);
        });
    });

    // Hàm hỗ trợ xử lý ngày sinh đã được loại bỏ
});
