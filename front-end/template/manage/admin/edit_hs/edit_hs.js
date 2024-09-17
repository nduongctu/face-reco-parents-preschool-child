document.addEventListener('DOMContentLoaded', async function () {
    const token = localStorage.getItem('access_token');

    if (!token) {
        alert('Token không tồn tại! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../../auth/login.html';
        }, 3000);
        return;
    }

    try {
        const response = await fetch('http://localhost:8000/auth/admin/me', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.detail || 'Không có quyền truy cập hoặc token không hợp lệ! Vui lòng đăng nhập lại.');
            setTimeout(() => {
                window.location.href = '../../../auth/login.html';
            }, 3000);
            return;
        }

        const data = await response.json();
        if (data.quyen !== 0) { // Kiểm tra quyền truy cập
            alert('Không có quyền truy cập! Vui lòng đăng nhập lại.');
            setTimeout(() => {
                window.location.href = '../../../auth/login.html';
            }, 3000);
        }
    } catch (error) {
        console.error('Error fetching user info:', error);
        alert('Có lỗi xảy ra! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../../auth/login.html';
        }, 3000);
    }

    // Lấy ID học sinh từ URL
    const urlParams = new URLSearchParams(window.location.search);
    const studentId = urlParams.get('id');

    if (!studentId) {
        alert('ID học sinh không hợp lệ!');
        window.location.href = 'ql_hocsinh.html'; // Quay lại trang danh sách học sinh nếu không có ID
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/admin/students/${studentId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.detail || 'Không thể tải thông tin học sinh.');
            window.location.href = 'ql_hocsinh.html'; // Quay lại trang danh sách học sinh nếu có lỗi
            return;
        }

        const student = await response.json();

        // Hiển thị thông tin học sinh vào biểu mẫu
        document.getElementById('student-id').value = student.id_hs;
        document.getElementById('ten_hs').value = student.ten_hs;
        document.getElementById('gioitinh_hs').value = student.gioitinh_hs; // Chọn giới tính
        document.getElementById('ngaysinh_hs').value = student.ngaysinh_hs; // Định dạng yyyy-mm-dd

    } catch (error) {
        console.error('Error fetching student data:', error);
        alert('Có lỗi xảy ra khi tải thông tin học sinh.');
    }

    // Xử lý sự kiện gửi biểu mẫu
    document.getElementById('edit-student-form').addEventListener('submit', function (event) {
        event.preventDefault();

        const studentId = document.getElementById('student-id').value;
        const ten_hs = document.getElementById('ten_hs').value;
        const gioitinh_hs = document.getElementById('gioitinh_hs').value;
        const ngaysinh_hs = document.getElementById('ngaysinh_hs').value; // Định dạng yyyy-mm-dd tự động

        fetch(`http://localhost:8000/admin/students/${studentId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ten_hs,
                gioitinh_hs,
                ngaysinh_hs // Định dạng yyyy-mm-dd tự động
            })
        })
            .then(response => {
                if (response.ok) {
                    alert('Cập nhật thành công!');
                    window.location.href = '../ql_hocsinh.html'; // Quay lại trang danh sách học sinh
                } else {
                    return response.json().then(data => {
                        throw new Error(data.detail || 'Có lỗi xảy ra khi cập nhật thông tin.');
                    });
                }
            })
            .catch(error => {
                console.error('Lỗi khi cập nhật:', error);
                alert(error.message);
            });
    });
});
