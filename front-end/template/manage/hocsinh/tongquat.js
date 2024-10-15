document.addEventListener('DOMContentLoaded', async function () {
    const token = localStorage.getItem('access_token');

    // Kiểm tra token
    if (!token) {
        alert('Token không tồn tại! Vui lòng đăng nhập lại.');
        redirectToLogin();
        return;
    }

    // Kiểm tra quyền truy cập
    if (!(await checkAccess(token))) {
        redirectToLogin();
        return;
    }

    // Lấy thông tin người dùng từ API để lấy id_hs
    const userData = await fetchUserData(token);
    if (!userData || !userData.id_hs) {
        alert('ID học sinh không hợp lệ!');
        window.location.href = 'hocsinh.html';
        return;
    }

    const studentId = userData.id_hs; // Lấy ID học sinh từ dữ liệu người dùng

    // Lấy thông tin học sinh từ API
    const student = await fetchStudentData(studentId, token);
    if (!student) return;

    // Hiển thị thông tin học sinh vào biểu mẫu
    populateStudentForm(student);

    // Thêm sự kiện cho nút "Thêm Phụ Huynh"
    document.getElementById("btn-add-parent").addEventListener('click', addParentEntry);

    // Xử lý sự kiện gửi biểu mẫu
    document.getElementById('edit-student-form').addEventListener('submit', async function (event) {
        event.preventDefault();
        await updateStudentInfo(studentId, token);
    });

    // Lấy danh sách lớp học và điền vào select
    await fetchClasses();
});

// Hàm kiểm tra quyền truy cập
async function checkAccess(token) {
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
            return false;
        }

        const data = await response.json();
        if (data.quyen !== 2) { // Kiểm tra quyền truy cập
            alert('Không có quyền truy cập! Vui lòng đăng nhập lại.');
            return false;
        }
    } catch (error) {
        console.error('Error fetching user info:', error);
        alert('Có lỗi xảy ra! Vui lòng đăng nhập lại.');
        return false;
    }
    return true;
}

// Hàm lấy thông tin người dùng từ API
async function fetchUserData(token) {
    try {
        const response = await fetch('http://localhost:8000/auth/admin/me', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.detail || 'Không thể lấy thông tin người dùng.');
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching user info:', error);
        alert('Có lỗi xảy ra khi lấy thông tin người dùng.');
        return null;
    }
}
