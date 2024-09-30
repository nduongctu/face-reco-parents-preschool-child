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
        console.error('Lỗi khi lấy thông tin người dùng:', error);
        alert('Có lỗi xảy ra! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../auth/login.html';
        }, 3000);
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const apiUrl = 'http://localhost:8000/admin/classes'; // Địa chỉ API lấy danh sách lớp học
    let classIdToDelete = null; // Biến lưu ID của lớp học cần xóa

    // Hàm để hiển thị danh sách lớp học
    function displayClasses() {
        fetch(apiUrl)
            .then(response => response.json())
            .then(classes => {
                const tableBody = document.getElementById('class-list');
                tableBody.innerHTML = ''; // Xóa nội dung bảng trước khi thêm dữ liệu mới

                classes.forEach(cls => {
                    const row = document.createElement('tr');

                    // Tạo các ô cho thông tin lớp học
                    row.innerHTML = `
                        <td>${cls.id_lh}</td>
                        <td>${cls.lophoc}</td>
                        <td>${cls.nam_hoc.namhoc || 'Chưa có năm học'}</td>
                        <td>${cls.giao_vien ? cls.giao_vien.ten_gv : 'Chưa có giáo viên'}</td>
                        <td>${cls.tong_so_hoc_sinh || 0}</td> <!-- Hiển thị tổng số học sinh -->
                        <td><a href="edit_lh/edit_lh.html?id=${cls.id_lh}" class="btn-edit">Chỉnh Sửa</a></td>
                        <td><button class="btn-delete" data-id="${cls.id_lh}">Xóa</button></td>
                    `;

                    tableBody.appendChild(row);
                });

                // Thêm sự kiện cho các nút xóa
                document.querySelectorAll('.btn-delete').forEach(button => {
                    button.addEventListener('click', function () {
                        classIdToDelete = this.getAttribute('data-id');
                        document.getElementById('popup-overlay').style.display = 'flex'; // Hiển thị pop-up
                    });
                });
            })
            .catch(error => {
                console.error('Lỗi khi lấy dữ liệu:', error);
            });
    }

    // Hiển thị danh sách lớp học khi trang được tải
    displayClasses();

    // Xử lý nút xác nhận xóa
    document.getElementById('confirm-delete').addEventListener('click', function () {
        if (classIdToDelete) {
            fetch(`http://localhost:8000/admin/classes/${classIdToDelete}`, {
                method: 'DELETE',
            })
                .then(response => {
                    if (response.ok) {
                        alert('Xóa thành công!');
                        displayClasses(); // Cập nhật lại danh sách lớp học
                    } else {
                        alert('Có lỗi xảy ra khi xóa lớp học.');
                    }
                })
                .catch(error => {
                    console.error('Lỗi khi xóa:', error);
                    alert('Có lỗi xảy ra khi xóa lớp học.');
                });

            document.getElementById('popup-overlay').style.display = 'none'; // Ẩn pop-up
        }
    });

    // Xử lý nút hủy
    document.getElementById('cancel-delete').addEventListener('click', function () {
        document.getElementById('popup-overlay').style.display = 'none'; // Ẩn pop-up
        classIdToDelete = null; // Xóa ID của lớp học cần xóa
    });

    // Xử lý tìm kiếm lớp học
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', function () {
        const query = searchInput.value.toLowerCase();
        const rows = document.getElementById('class-list').getElementsByTagName('tr');

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
    });
});
