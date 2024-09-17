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
});

document.addEventListener('DOMContentLoaded', function () {
    const apiUrl = 'http://localhost:8000/admin/students'; // Địa chỉ API lấy danh sách học sinh
    let studentIdToDelete = null; // Biến lưu ID của học sinh cần xóa

    // Hàm để chuyển đổi định dạng ngày từ yyyy-mm-dd sang dd-mm-yyyy
    function formatDate(inputDate) {
        const [year, month, day] = inputDate.split("-");
        return `${day}-${month}-${year}`;
    }

    // Hàm để chuyển đổi định dạng ngày từ dd-mm-yyyy sang yyyy-mm-dd
    function unformatDate(displayDate) {
        const [day, month, year] = displayDate.split("-");
        return `${year}-${month}-${day}`;
    }

    // Hiển thị danh sách học sinh
    fetch(apiUrl)
        .then(response => response.json())
        .then(students => {
            const tableBody = document.getElementById('student-list');
            tableBody.innerHTML = ''; // Xóa nội dung bảng trước khi thêm dữ liệu mới

            students.forEach(student => {
                const row = document.createElement('tr');

                // Chuyển đổi ngày sang định dạng dd-mm-yyyy
                const formattedDate = formatDate(student.ngaysinh_hs);

                // Tạo các ô cho thông tin học sinh
                row.innerHTML = `
                    <td>${student.id_hs}</td>
                    <td>${student.ten_hs}</td>
                    <td>${student.gioitinh_hs}</td>
                    <td>${formattedDate}</td>
                    <td>${student.lop_hoc.map(lop => lop.ten_lop).join(', ') || 'Chưa có lớp'}</td>
                    <td><a href="edit_hs/edit_hs.html?id=${student.id_hs}" class="btn-edit">Chỉnh Sửa</a></td>
                    <td><button class="btn-delete" data-id="${student.id_hs}">Xóa</button></td>
                `;

                tableBody.appendChild(row);
            });

            // Thêm sự kiện cho các nút xóa
            document.querySelectorAll('.btn-delete').forEach(button => {
                button.addEventListener('click', function () {
                    studentIdToDelete = this.getAttribute('data-id');
                    document.getElementById('popup-overlay').style.display = 'flex'; // Hiển thị pop-up
                });
            });

            // Xử lý nút xác nhận xóa
            document.getElementById('confirm-delete').addEventListener('click', function () {
                if (studentIdToDelete) {
                    fetch(`http://localhost:8000/admin/students/${studentIdToDelete}`, {
                        method: 'DELETE',
                    })
                        .then(response => {
                            if (response.ok) {
                                alert('Xóa thành công!');
                                location.reload(); // Tải lại trang để cập nhật danh sách
                            } else {
                                alert('Có lỗi xảy ra khi xóa học sinh.');
                            }
                        })
                        .catch(error => {
                            console.error('Lỗi khi xóa:', error);
                            alert('Có lỗi xảy ra khi xóa học sinh.');
                        });

                    document.getElementById('popup-overlay').style.display = 'none'; // Ẩn pop-up
                }
            });

            // Xử lý nút hủy
            document.getElementById('cancel-delete').addEventListener('click', function () {
                document.getElementById('popup-overlay').style.display = 'none'; // Ẩn pop-up
                studentIdToDelete = null; // Xóa ID của học sinh cần xóa
            });
        })
        .catch(error => {
            console.error('Lỗi khi lấy dữ liệu:', error);
        });
});
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-input');
    const studentList = document.getElementById('student-list');

    // Hàm lọc danh sách học sinh
    function filterStudents() {
        const query = searchInput.value.toLowerCase();
        const rows = studentList.getElementsByTagName('tr');

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
    searchInput.addEventListener('input', filterStudents);
});
