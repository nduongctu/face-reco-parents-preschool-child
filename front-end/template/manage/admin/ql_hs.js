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

    // Lấy quyền người dùng
    const userRole = await fetchUserRole(token);
    if (userRole !== 0) {
        alert('Không có quyền truy cập! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../auth/login.html';
        }, 3000);
        return;
    }

    const apiUrl = 'http://localhost:8000/admin/students'; // Địa chỉ API lấy danh sách học sinh
    let studentIdToDelete = null; // Khai báo biến ID học sinh cần xóa

    // Lấy danh sách học sinh và hiển thị
    await fetchAndDisplayStudents(apiUrl);

    // Thêm sự kiện cho các nút xóa
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', function () {
            studentIdToDelete = this.getAttribute('data-id');
            document.getElementById('popup-overlay').style.display = 'flex'; // Hiển thị pop-up
        });
    });

    // Xử lý nút xác nhận xóa
    document.getElementById('confirm-delete').addEventListener('click', async function () {
        if (studentIdToDelete) {
            try {
                const response = await fetch(`http://localhost:8000/admin/students/${studentIdToDelete}`, {
                    method: 'DELETE',
                });

                if (response.ok) {
                    alert('Xóa thành công!');
                    location.reload(); // Tải lại trang để cập nhật danh sách
                } else {
                    const errorData = await response.json();
                    alert(errorData.detail || 'Có lỗi xảy ra khi xóa học sinh.'); // Hiển thị thông báo lỗi chi tiết
                }
            } catch (error) {
                console.error('Lỗi khi xóa:', error);
                alert('Có lỗi xảy ra khi xóa học sinh.'); // Thông báo lỗi chung
            }

            document.getElementById('popup-overlay').style.display = 'none'; // Ẩn pop-up
        }
    });

    // Sự kiện cho nút hủy
    document.getElementById('cancel-delete').addEventListener('click', function () {
        document.getElementById('popup-overlay').style.display = 'none'; // Ẩn pop-up
        studentIdToDelete = null; // Reset ID sau khi hủy
    });

    // Sự kiện tìm kiếm học sinh
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', function () {
        const query = searchInput.value;
        filterStudents(query); // Gọi hàm lọc học sinh
    });
});

// Hàm gọi API để lấy quyền người dùng
async function fetchUserRole(token) {
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
            return null; // Trả về null thay vì ném lỗi
        }

        const data = await response.json();
        return data.quyen; // Trả về quyền của người dùng
    } catch (error) {
        console.error('Error fetching user info:', error);
        alert('Có lỗi xảy ra! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../auth/login.html';
        }, 3000);
    }
}

// Hàm để lấy danh sách học sinh và hiển thị
async function fetchAndDisplayStudents(apiUrl) {
    try {
        const response = await fetch(apiUrl);
        const students = await response.json();

        const tableBody = document.getElementById('student-list');
        tableBody.innerHTML = ''; // Xóa nội dung bảng trước khi thêm dữ liệu mới

        students.forEach(student => {
            const row = createStudentRow(student);
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Lỗi khi lấy dữ liệu:', error);
    }
}

// Hàm tạo hàng cho bảng học sinh
function createStudentRow(student) {
    const row = document.createElement('tr');
    const formattedDate = formatDate(student.ngaysinh_hs);

    // Lấy tên lớp học và thông tin phụ huynh
    const classNames = student.lop_hoc_ten || 'Chưa có lớp';
    const parentNames = student.phu_huynh.map(phu_huynh => phu_huynh.ten_ph).join(', ') || 'Chưa có phụ huynh';

    // Thiết lập nội dung cho hàng bảng
    row.innerHTML = `
        <td>${student.id_hs}</td>
        <td>${student.ten_hs}</td>
        <td>${student.gioitinh_hs}</td>
        <td>${formattedDate}</td>
        <td>${parentNames}</td>
        <td>${classNames}</td>
        <td><a href="edit_hs/edit_hs.html?id=${student.id_hs}" class="btn-edit">Chỉnh Sửa</a></td>
        <td><button class="btn-delete" data-id="${student.id_hs}">Xóa</button></td>
    `;
    return row;
}

// Hàm để hiển thị hoặc ẩn pop-up
function togglePopup(show) {
    document.getElementById('popup-overlay').style.display = show ? 'flex' : 'none';
}

// Hàm để chuyển đổi định dạng ngày từ yyyy-mm-dd sang dd-mm-yyyy
function formatDate(inputDate) {
    const [year, month, day] = inputDate.split("-");
    return `${day}-${month}-${year}`;
}

// Hàm để lọc danh sách học sinh
function filterStudents(query) {
    const studentList = document.getElementById('student-list');
    const rows = studentList.getElementsByTagName('tr');

    Array.from(rows).forEach(row => {
        const cells = row.getElementsByTagName('td');
        const id = cells[0].textContent.toLowerCase();
        const name = cells[1].textContent.toLowerCase();

        // Lọc theo mã số học sinh hoặc tên học sinh
        if (id.includes(query.toLowerCase()) || name.includes(query.toLowerCase())) {
            row.style.display = ''; // Hiển thị hàng phù hợp
        } else {
            row.style.display = 'none'; // Ẩn hàng không phù hợp
        }
    });
}
