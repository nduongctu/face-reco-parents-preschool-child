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

    // Lấy quyền người dùng và id_gv
    const user = await fetchUserRole(token);

    // Kiểm tra nếu user không hợp lệ
    if (!user || user.quyen !== 1) {
        alert('Không có quyền truy cập! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../auth/login.html';
        }, 3000);
        return;
    }

    const apiUrl = `http://localhost:8000/admin/students_gv/${user.id_gv}`; // Dùng id_gv lấy từ API

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
                    alert(errorData.detail || 'Có lỗi xảy ra khi xóa học sinh.');
                }
            } catch (error) {
                console.error('Lỗi khi xóa:', error);
                alert('Có lỗi xảy ra khi xóa học sinh.');
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
            method: 'GET', headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.detail || 'Không có quyền truy cập hoặc token không hợp lệ! Vui lòng đăng nhập lại.');
            return null; // Trả về null nếu có lỗi
        }

        const data = await response.json();

        // Trả về đối tượng chứa cả quyền và id_gv
        return {quyen: data.quyen, id_gv: data.id_gv};
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
    const namHoc = student.nam_hoc || 'Chưa có năm học'; // Lấy thông tin năm học, mặc định nếu không có

    // Thiết lập nội dung cho hàng bảng
    row.innerHTML = `
        <td>${student.id_hs}</td>
        <td>${student.ten_hs}</td>
        <td>${student.gioitinh_hs}</td>
        <td>${formattedDate}</td>
        <td>${parentNames}</td>
        <td>${classNames}</td>
        <td>${namHoc}</td>  <!-- Hiển thị năm học -->
        <td><a href="edit_hs_gv.html?id=${student.id_hs}" class="btn-edit">Chỉnh Sửa</a></td>
        <td><button class="btn-delete" data-id="${student.id_hs}">Xóa</button></td>
    `;
    return row;
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

        if (id.includes(query.toLowerCase()) || name.includes(query.toLowerCase())) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}
