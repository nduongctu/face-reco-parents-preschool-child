document.addEventListener('DOMContentLoaded', async function () {
    const token = localStorage.getItem('access_token');

    // Kiểm tra xem token có tồn tại không
    if (!token) {
        alert('Token không tồn tại! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../../auth/login.html';
        }, 3000);
        return;
    }

    // Kiểm tra quyền truy cập
    const checkAccess = async () => {
        try {
            const response = await fetch('http://localhost:8000/auth/admin/me', {
                method: 'GET',
                headers: {'Authorization': `Bearer ${token}`}
            });

            if (!response.ok) {
                const errorData = await response.json();
                alert(errorData.detail || 'Không có quyền truy cập hoặc token không hợp lệ! Vui lòng đăng nhập lại.');
                setTimeout(() => {
                    window.location.href = '../../../auth/login.html';
                }, 3000);
                return false; // Không có quyền
            }

            const data = await response.json();
            if (data.quyen !== 0) { // Kiểm tra quyền truy cập
                alert('Không có quyền truy cập! Vui lòng đăng nhập lại.');
                setTimeout(() => {
                    window.location.href = '../../../auth/login.html';
                }, 3000);
                return false; // Không có quyền
            }

            return true; // Có quyền
        } catch (error) {
            console.error('Error fetching user info:', error);
            alert('Có lỗi xảy ra! Vui lòng đăng nhập lại.');
            setTimeout(() => {
                window.location.href = '../../../auth/login.html';
            }, 3000);
            return false; // Không có quyền
        }
    };

    // Lấy ID giáo viên từ URL
    const getTeacherId = () => {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('id');
    };

    // Tải thông tin giáo viên
    const fetchTeacherData = async (teacherId) => {
        try {
            const response = await fetch(`http://localhost:8000/admin/teachers/${teacherId}`, {
                method: 'GET',
                headers: {'Authorization': `Bearer ${token}`}
            });

            if (!response.ok) {
                const errorData = await response.json();
                alert(errorData.detail || 'Không thể tải thông tin giáo viên.');
                window.location.href = '../ql_giaovien.html';
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching teacher data:', error);
            alert('Có lỗi xảy ra khi tải thông tin giáo viên.');
            return null;
        }
    };

    // Tải danh sách lớp học
    const fetchClasses = async () => {
        try {
            const response = await fetch('http://localhost:8000/admin/classes', {
                method: 'GET',
                headers: {'Authorization': `Bearer ${token}`}
            });

            if (!response.ok) {
                const errorData = await response.json();
                alert(errorData.detail || 'Không thể tải danh sách lớp học.');
                return [];
            }

            return await response.json(); // Giả sử API trả về danh sách lớp học
        } catch (error) {
            console.error('Error fetching classes:', error);
            alert('Có lỗi xảy ra khi tải danh sách lớp học.');
            return [];
        }
    };

    // Hiển thị thông tin giáo viên
    const displayTeacherInfo = (teacher) => {
        document.getElementById('ma_gv').value = teacher.id_gv;
        document.getElementById('ten_gv').value = teacher.ten_gv;
        document.getElementById('gioitinh_gv').value = teacher.gioitinh_gv;
        document.getElementById('ngaysinh_gv').value = teacher.ngaysinh_gv.split('T')[0]; // Định dạng yyyy-mm-dd
        document.getElementById('sdt_gv').value = teacher.sdt_gv;
        document.getElementById('diachi_gv').value = teacher.diachi_gv;
        document.getElementById('email_gv').value = teacher.email_gv;
        document.getElementById('quyen').value = teacher.quyen !== undefined ? teacher.quyen : '1'; // Giáo viên mặc định

        // Kiểm tra xem giáo viên có lớp học không và hiển thị tên lớp
        const className = teacher.lop_hoc_ten || 'Chưa có lớp học'; // Lấy tên lớp học từ dữ liệu
        document.getElementById('lop_hoc').value = teacher.id_lh || ''; // Nếu có lớp học, điền ID lớp vào trường

        // Nếu không có lớp, hiển thị "Chưa có lớp" trong ô Lớp Học
        if (!teacher.id_lh) {
            document.getElementById('lop_hoc').value = 'Chưa có lớp'; // Thiết lập ô là "Chưa có lớp"
        }
    };

    // Gửi yêu cầu cập nhật thông tin giáo viên
    const updateTeacherInfo = async (teacherData) => {
        try {
            const response = await fetch(`http://localhost:8000/admin/teachers/${teacherData.id_gv}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(teacherData)
            });

            if (response.ok) {
                alert('Cập nhật thành công!');
                window.location.href = '../ql_giaovien.html'; // Quay lại trang danh sách giáo viên
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Có lỗi xảy ra khi cập nhật thông tin.');
            }
        } catch (error) {
            console.error('Lỗi khi cập nhật:', error);
            alert(error.message);
        }
    };

    // Kiểm tra quyền truy cập
    if (!(await checkAccess())) return;

    const teacherId = getTeacherId();
    if (!teacherId) {
        alert('ID giáo viên không hợp lệ!');
        window.location.href = '../ql_giaovien.html';
        return;
    }

    const teacher = await fetchTeacherData(teacherId);
    if (teacher) {
        displayTeacherInfo(teacher);
    }

    // Tải danh sách lớp học và điền vào dropdown
    const classes = await fetchClasses();
    const classSelect = document.getElementById('lop_hoc');

    // Điền danh sách lớp vào dropdown
    classes.forEach(cls => {
        const option = document.createElement('option');
        option.value = cls.id_lh; // ID lớp học
        option.textContent = cls.lophoc; // Tên lớp học
        classSelect.appendChild(option);
    });

    if (teacher && teacher.id_lh) {
        classSelect.value = teacher.id_lh; // Đặt giá trị của dropdown là lớp hiện tại của giáo viên
    } else {
        const noClassOption = document.createElement('option');
        noClassOption.value = ''; // Giá trị trống
        noClassOption.textContent = 'Chưa có lớp';
        classSelect.appendChild(noClassOption);
        classSelect.value = ''; // Đặt giá trị ô thành trống
    }

    // Xử lý sự kiện gửi biểu mẫu
    document.getElementById('edit-teacher-form').addEventListener('submit', async function (event) {
        event.preventDefault();

        const teacherData = {
            id_gv: document.getElementById('ma_gv').value,
            ten_gv: document.getElementById('ten_gv').value,
            gioitinh_gv: document.getElementById('gioitinh_gv').value,
            ngaysinh_gv: document.getElementById('ngaysinh_gv').value,
            sdt_gv: document.getElementById('sdt_gv').value,
            diachi_gv: document.getElementById('diachi_gv').value,
            email_gv: document.getElementById('email_gv').value,
            quyen: parseInt(document.getElementById('quyen').value, 10),
            id_lh: classSelect.value || null // Thêm ID lớp học vào dữ liệu, nếu không có thì là null
        };

        // Kiểm tra độ dài số điện thoại trước khi gửi
        if (teacherData.sdt_gv.length !== 10) {
            alert('Số điện thoại phải đúng 10 chữ số.');
            return;
        }

        const className = teacher.lop_hoc_ten || 'Chưa có lớp học';
        if (teacher && teacher.id_lh && teacher.id_lh !== teacherData.id_lh) {
            const confirmChange = confirm(`Giáo viên này đang dạy lớp học "${className}". Bạn có chắc chắn muốn thay đổi lớp học không?`);
            if (!confirmChange) {
                return;
            }
        }

        updateTeacherInfo(teacherData);
    });

    document.getElementById('sdt_gv').addEventListener('input', function (e) {
        e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 10);
    });
});
