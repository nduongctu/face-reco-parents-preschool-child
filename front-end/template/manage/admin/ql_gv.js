document.addEventListener('DOMContentLoaded', async function () {
    const token = localStorage.getItem('access_token');

    if (!token) {
        alert('Token không tồn tại! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../auth/login.html';
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
                window.location.href = '../../auth/login.html';
            }, 3000);
            return;
        }

        const data = await response.json();
        if (data.quyen !== 0) { // Kiểm tra quyền truy cập
            alert('Không có quyền truy cập! Vui lòng đăng nhập lại.');
            setTimeout(() => {
                window.location.href = '../../auth/login.html';
            }, 3000);
        }
    } catch (error) {
        console.error('Error fetching user info:', error);
        alert('Có lỗi xảy ra! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../auth/login.html';
        }, 3000);
    }

    // Tiến hành hiển thị danh sách giáo viên
    const apiUrl = 'http://localhost:8000/admin/teachers'; // Địa chỉ API lấy danh sách giáo viên
    let teacherIdToDelete = null; // Biến lưu ID của giáo viên cần xóa

    // Hàm để chuyển đổi định dạng ngày từ yyyy-mm-dd sang dd-mm-yyyy
    function formatDate(inputDate) {
        const [year, month, day] = inputDate.split("-");
        return `${day}-${month}-${year}`;
    }

    // Hàm để hiển thị danh sách giáo viên
    async function displayTeachers() {
        try {
            const response = await fetch(apiUrl);
            const teachers = await response.json();
            const tableBody = document.getElementById('teacher-list');
            tableBody.innerHTML = ''; // Xóa nội dung bảng trước khi thêm dữ liệu mới

            teachers.forEach(teacher => {
                const row = document.createElement('tr');

                // Chuyển đổi ngày sang định dạng dd-mm-yyyy
                const formattedDate = formatDate(teacher.ngaysinh_gv);

                // Tạo các ô cho thông tin giáo viên
                row.innerHTML = `
                    <td>${teacher.id_gv}</td>
                    <td>${teacher.ten_gv}</td>
                    <td>${teacher.gioitinh_gv}</td>
                    <td>${formattedDate}</td>
                    <td>${teacher.diachi_gv}</td>
                    <td>${teacher.sdt_gv}</td>  
                    <td>${teacher.email_gv}</td>
                    <td>${teacher.tai_khoan_quyen === 0 ? 'Quản Lý' : 'Giáo Viên'}</td>
                    <td>${teacher.lop_hoc_ten || 'Chưa có lớp'}</td>
                    <td><a href="edit_gv/edit_gv.html?id=${teacher.id_gv}" class="btn-edit">Chỉnh Sửa</a></td>
                    <td><button class="btn-delete" data-id="${teacher.id_gv}">Xóa</button></td>
                `;

                tableBody.appendChild(row);
            });

            // Thêm sự kiện cho các nút xóa
            addDeleteEventListeners();

        } catch (error) {
            console.error('Lỗi khi lấy dữ liệu:', error);
        }
    }

    // Hàm thêm sự kiện cho các nút xóa
    function addDeleteEventListeners() {
        document.querySelectorAll('.btn-delete').forEach(button => {
            button.addEventListener('click', function () {
                teacherIdToDelete = this.getAttribute('data-id');
                document.getElementById('popup-overlay').style.display = 'flex'; // Hiển thị pop-up
            });
        });

        // Xử lý nút xác nhận xóa
        document.getElementById('confirm-delete').addEventListener('click', async function () {
            if (teacherIdToDelete) {
                try {
                    const response = await fetch(`http://localhost:8000/admin/teachers/${teacherIdToDelete}`, {
                        method: 'DELETE',
                    });
                    if (response.ok) {
                        alert('Xóa thành công!');
                        location.reload(); // Tải lại trang để cập nhật danh sách
                    } else {
                        alert('Có lỗi xảy ra khi xóa giáo viên.');
                    }
                } catch (error) {
                    console.error('Lỗi khi xóa:', error);
                    alert('Có lỗi xảy ra khi xóa giáo viên.');
                }

                document.getElementById('popup-overlay').style.display = 'none'; // Ẩn pop-up
            }
        });

        // Xử lý nút hủy
        document.getElementById('cancel-delete').addEventListener('click', function () {
            document.getElementById('popup-overlay').style.display = 'none'; // Ẩn pop-up
            teacherIdToDelete = null; // Xóa ID của giáo viên cần xóa
        });
    }

    // Hàm lọc danh sách giáo viên
    function filterTeachers() {
        const query = searchInput.value.toLowerCase();
        const rows = teacherList.getElementsByTagName('tr');

        Array.from(rows).forEach(row => {
            const cells = row.getElementsByTagName('td');
            const id = cells[0].textContent.toLowerCase();
            const name = cells[1].textContent.toLowerCase();

            if (id.includes(query) || name.includes(query)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    // Xử lý sự kiện nhập liệu trong ô tìm kiếm
    const searchInput = document.getElementById('search-input');
    const teacherList = document.getElementById('teacher-list');
    searchInput.addEventListener('input', filterTeachers);

    // Hiển thị danh sách giáo viên ngay khi trang tải xong
    await displayTeachers(); // Sử dụng await khi gọi hàm này
});
