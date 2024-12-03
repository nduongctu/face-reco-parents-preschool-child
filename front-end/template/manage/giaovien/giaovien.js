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

    // Kiểm tra quyền truy cập và lấy ID giáo viên
    const checkAccessAndGetId = async () => {
        try {
            const response = await fetch('http://localhost:8000/auth/admin/me', {
                method: 'GET',
                headers: {'Authorization': `Bearer ${token}`}
            });

            if (!response.ok) {
                const errorData = await response.json();
                alert(errorData.detail || 'Không có quyền truy cập hoặc token không hợp lệ! Vui lòng đăng nhập lại.');
                setTimeout(() => {
                    window.location.href = '../../auth/login.html';
                }, 2000);
                return null;
            }

            const data = await response.json();
            if (data.quyen !== 1) { // Kiểm tra quyền truy cập
                alert('Không có quyền truy cập! Vui lòng đăng nhập lại.');
                setTimeout(() => {
                    window.location.href = '../../auth/login.html';
                }, 2000);
                return null;
            }

            return data.id_gv; // Trả về ID giáo viên
        } catch (error) {
            console.error('Error fetching user info:', error);
            alert('Có lỗi xảy ra! Vui lòng đăng nhập lại.');
            setTimeout(() => {
                window.location.href = '../../auth/login.html';
            }, 2000);
            return null;
        }
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
                window.location.href = '../ql_giaovien.html'; // Quay lại trang danh sách giáo viên nếu có lỗi
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

    // Hiển thị thông tin giáo viên vào biểu mẫu
    const displayTeacherInfo = (teacher) => {
        document.getElementById('ma_gv').value = teacher.id_gv;
        document.getElementById('ten_gv').value = teacher.ten_gv;
        document.getElementById('gioitinh_gv').value = teacher.gioitinh_gv;
        document.getElementById('ngaysinh_gv').value = teacher.ngaysinh_gv.split('T')[0]; // Định dạng yyyy-mm-dd
        document.getElementById('sdt_gv').value = teacher.sdt_gv;
        document.getElementById('diachi_gv').value = teacher.diachi_gv;
        document.getElementById('email_gv').value = teacher.email_gv;
        document.getElementById('quyen').value = teacher.quyen !== undefined ? teacher.quyen : '1'; // Giáo viên mặc định
        document.getElementById('lop_hoc').value = teacher.id_lh; // Đặt lớp học đã chọn
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
                window.location.href = 'giaovien.html';
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Có lỗi xảy ra khi cập nhật thông tin.');
            }
        } catch (error) {
            console.error('Lỗi khi cập nhật:', error);
            alert(error.message);
        }
    };

    // Lấy ID giáo viên và kiểm tra quyền truy cập
    const teacherId = await checkAccessAndGetId();
    if (!teacherId) return; // Nếu không có ID giáo viên, dừng lại

    const teacher = await fetchTeacherData(teacherId);
    if (teacher) {
        displayTeacherInfo(teacher);
    }

    // Tải danh sách lớp học và điền vào dropdown
    const classes = await fetchClasses();
    const classSelect = document.getElementById('lop_hoc');
    classes.forEach(cls => {
        const option = document.createElement('option');
        option.value = cls.id_lh; // ID lớp học
        option.textContent = cls.lophoc; // Tên lớp học
        classSelect.appendChild(option);
    });

    // Xử lý sự kiện gửi biểu mẫu
    document.getElementById('edit-teacher-form').addEventListener('submit', function (event) {
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
            id_lh: document.getElementById('lop_hoc').value
        };

        if (teacherData.sdt_gv.length !== 10) {
            alert('Số điện thoại phải đúng 10 chữ số.');
            return;
        }

        updateTeacherInfo(teacherData);
    });

    // Giới hạn số điện thoại chỉ cho phép 10 chữ số
    document.getElementById('sdt_gv').addEventListener('input', function (e) {
        e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 10); // Loại bỏ ký tự không phải số và giới hạn 10 số
    });

    // Xử lý ảnh đại diện
    const pictureInput = document.querySelector('input[name="picture"]');
    const profilePicture = document.querySelector("#profile-picture"); // Lấy hình ảnh đại diện

    // Lấy ảnh giáo viên hiện tại khi tải trang
    const getTeacherImage = async () => {
        try {
            const response = await fetch(`http://localhost:8000/admin/images/giao-vien/${teacherId}/`, {
                method: "GET",
                headers: {'Authorization': `Bearer ${token}`} // Thêm token nếu cần
            });
            if (response.ok) {
                const image = await response.json();
                profilePicture.src = image.image_path; // Cập nhật src của hình ảnh đại diện
            } else {
                console.error("Không thể lấy ảnh giáo viên.");
            }
        } catch (error) {
            console.error("Lỗi:", error);
        }
    };

    // Gọi hàm để tải ảnh giáo viên khi tải trang
    await getTeacherImage();

    // Cập nhật ảnh cho user-icon
    const getUserImage = async () => {
        try {
            const response = await fetch(`http://localhost:8000/admin/images/giao-vien/${teacherId}/`, {
                method: 'GET',
                headers: {'Authorization': `Bearer ${token}`}
            });

            if (response.ok) {
                const data = await response.json();
                document.getElementById('user-icon').src = data.image_path; // Cập nhật src cho thẻ img user-icon
            } else {
                console.error('Không thể lấy ảnh người dùng.');
            }
        } catch (error) {
            console.error('Lỗi:', error);
        }
    };

    // Gọi hàm để lấy ảnh cho user-icon
    await getUserImage();

    document.getElementById('change-picture-button').addEventListener('click', function () {
        pictureInput.click(); // Kích hoạt hộp thoại chọn tệp
    });

    // Hiển thị hình ảnh khi người dùng chọn ảnh mới
    pictureInput.addEventListener("change", async function (event) {
        const file = event.target.files[0]; // Lấy file ảnh từ input

        if (file) {
            const formData = new FormData();
            formData.append("file", file); // Thêm file vào FormData
            formData.append("id_gv", teacherId); // Thêm id_gv vào FormData

            try {
                const response = await fetch(`http://localhost:8000/admin/images/giao-vien/`, {
                    method: "PUT",
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: formData,
                });

                if (response.ok) {
                    alert("Cập nhật ảnh đại diện thành công!");
                    await getTeacherImage(); // Tải lại ảnh mới
                    await getUserImage(); // Tải lại ảnh cho user-icon
                } else {
                    const errorData = await response.json();
                    alert(errorData.detail || "Có lỗi xảy ra khi cập nhật ảnh đại diện.");
                }
            } catch (error) {
                console.error("Lỗi:", error);
                alert("Có lỗi xảy ra trong quá trình gửi yêu cầu.");
            }
        }
    });
});