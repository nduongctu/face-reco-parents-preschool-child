document.addEventListener('DOMContentLoaded', function () {
    const token = localStorage.getItem('access_token');

    if (!token) {
        alert('Token không tồn tại! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../../auth/login.html';
        }, 3000);
        return;
    }

    // Hàm để nạp danh sách giáo viên vào menu chọn
    function loadTeachers() {
        fetch('http://localhost:8000/admin/teachers', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => response.json())
        .then(teachers => {
            const teacherSelect = document.getElementById('giaovien_lop');
            teacherSelect.innerHTML = '';

            teachers.forEach(teacher => {
                const option = document.createElement('option');
                option.value = teacher.id_gv;  // Giá trị này phải là ID của giáo viên
                option.textContent = teacher.ten_gv;  // Hiển thị tên giáo viên
                teacherSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Lỗi khi nạp danh sách giáo viên:', error);
            alert('Có lỗi xảy ra khi nạp danh sách giáo viên.');
        });
    }

    // Hàm để nạp danh sách năm học vào menu chọn
    function loadAcademicYears() {
        fetch('http://localhost:8000/admin/years', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => response.json())
        .then(years => {
            const yearSelect = document.getElementById('nam_hoc');
            yearSelect.innerHTML = '';

            years.forEach(year => {
                const option = document.createElement('option');
                option.value = year.id_nh;  // Đảm bảo lấy ID năm học
                option.textContent = year.namhoc;  // Hiển thị năm học
                yearSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Lỗi khi nạp danh sách năm học:', error);
            alert('Có lỗi xảy ra khi nạp danh sách năm học.');
        });
    }

    // Nạp danh sách giáo viên và năm học khi trang được tải
    loadTeachers();
    loadAcademicYears();

    document.getElementById('add-class-form').addEventListener('submit', function (event) {
        event.preventDefault();

        const ten_lop = document.getElementById('ten_lop').value;
        const nam_hoc = document.getElementById('nam_hoc').value;  // Lấy giá trị năm học
        const giaovien_lop = document.getElementById('giaovien_lop').value;  // Lấy giá trị giáo viên

        fetch('http://localhost:8000/admin/classes', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                lophoc: ten_lop,
                nam_hoc: parseInt(nam_hoc),  // Đảm bảo là ID của năm học
                giao_vien: [parseInt(giaovien_lop)]  // Đảm bảo là ID giáo viên
            })
        })
        .then(response => {
            if (response.ok) {
                alert('Thêm lớp học thành công!');
                window.location.href = '../ql_lophoc.html';
            } else {
                return response.json().then(data => {
                    throw new Error(data.detail || 'Có lỗi xảy ra khi thêm lớp học.');
                });
            }
        })
        .catch(error => {
            console.error('Lỗi khi thêm lớp học:', error);
            alert(error.message);
        });
    });
});
