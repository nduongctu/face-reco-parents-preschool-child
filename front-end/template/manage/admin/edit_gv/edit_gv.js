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

    // Lấy ID giáo viên từ URL
    const urlParams = new URLSearchParams(window.location.search);
    const teacherId = urlParams.get('id');

    if (!teacherId) {
        alert('ID giáo viên không hợp lệ!');
        window.location.href = 'ql_giaovien.html'; // Quay lại trang danh sách giáo viên nếu không có ID
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/admin/teachers/${teacherId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.detail || 'Không thể tải thông tin giáo viên.');
            window.location.href = 'ql_giaovien.html'; // Quay lại trang danh sách giáo viên nếu có lỗi
            return;
        }

        const teacher = await response.json();

        // Hiển thị thông tin giáo viên vào biểu mẫu
        document.getElementById('teacher-id').value = teacher.id_gv;
        document.getElementById('ten_gv').value = teacher.ten_gv;
        document.getElementById('gioitinh_gv').value = teacher.gioitinh_gv; // Chọn giới tính
        document.getElementById('ngaysinh_gv').value = teacher.ngaysinh_gv; // Định dạng yyyy-mm-dd
        document.getElementById('sdt_gv').value = teacher.sdt_gv;
        document.getElementById('diachi_gv').value = teacher.diachi_gv;

    } catch (error) {
        console.error('Error fetching teacher data:', error);
        alert('Có lỗi xảy ra khi tải thông tin giáo viên.');
    }

    // Xử lý sự kiện gửi biểu mẫu
    document.getElementById('edit-teacher-form').addEventListener('submit', function (event) {
        event.preventDefault();

        const teacherId = document.getElementById('teacher-id').value;
        const ten_gv = document.getElementById('ten_gv').value;
        const gioitinh_gv = document.getElementById('gioitinh_gv').value;
        const ngaysinh_gv = document.getElementById('ngaysinh_gv').value; // Định dạng yyyy-mm-dd
        const sdt_gv = document.getElementById('sdt_gv').value;
        const diachi_gv = document.getElementById('diachi_gv').value;

        // Kiểm tra độ dài số điện thoại trước khi gửi
        if (sdt_gv.length !== 10) {
            alert('Số điện thoại phải đúng 10 chữ số.');
            return;
        }

        fetch(`http://localhost:8000/admin/teachers/${teacherId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ten_gv,
                gioitinh_gv,
                ngaysinh_gv, // Định dạng yyyy-mm-dd tự động
                sdt_gv,
                diachi_gv
            })
        })
            .then(response => {
                if (response.ok) {
                    alert('Cập nhật thành công!');
                    window.location.href = '../ql_giaovien.html'; // Quay lại trang danh sách giáo viên
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

// Giới hạn số điện thoại chỉ cho phép 10 chữ số
document.getElementById('sdt_gv').addEventListener('input', function (e) {
    const input = e.target.value;

    // Loại bỏ các ký tự không phải là số
    e.target.value = input.replace(/[^0-9]/g, '');

    // Kiểm tra nếu nhập quá 10 số
    if (e.target.value.length > 10) {
        e.target.value = e.target.value.slice(0, 10); // Cắt chuỗi xuống còn 10 số
    }
});
