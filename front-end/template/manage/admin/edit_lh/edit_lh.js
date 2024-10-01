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

    // Lấy ID lớp học từ URL
    const classId = getClassIdFromUrl();
    if (!classId) {
        alert('ID lớp học không hợp lệ!');
        window.location.href = '../ql_lophoc.html'; // Quay lại trang danh sách lớp học nếu không có ID
        return;
    }

    // Lấy thông tin lớp học từ API
    const classData = await fetchClassData(classId, token);
    if (!classData) return;

    // Hiển thị thông tin lớp học vào biểu mẫu
    await populateClassForm(classData, token); // Đợi cho quá trình điền form hoàn thành

    // Lấy danh sách giáo viên và điền vào select
    await fetchTeachers(token);

    // Lấy danh sách năm học và điền vào select
    await fetchAcademicYears(token);

    // Xử lý sự kiện gửi biểu mẫu
    document.getElementById('edit-class-form').addEventListener('submit', async function (event) {
        event.preventDefault();
        await updateClassInfo(classId, token);
    });

    // Thêm sự kiện cho nút "Thêm Giáo Viên"
    document.getElementById("btn-add-teacher").addEventListener('click', async function () {
        await addTeacherEntry(token); // Thêm phần nhập giáo viên mới
    });
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
        if (data.quyen !== 0) { // Kiểm tra quyền truy cập
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

// Hàm lấy ID lớp học từ URL
function getClassIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id');
}

// Hàm lấy thông tin lớp học từ API
async function fetchClassData(classId, token) {
    try {
        const response = await fetch(`http://localhost:8000/admin/classes/${classId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.detail || 'Không thể tải thông tin lớp học.');
            window.location.href = '../ql_lophoc.html'; // Quay lại trang danh sách lớp học nếu có lỗi
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching class data:', error);
        alert('Có lỗi xảy ra khi tải thông tin lớp học.');
        return null;
    }
}

// Hàm hiển thị thông tin lớp học vào biểu mẫu
async function populateClassForm(classData, token) {
    document.getElementById('id_lh').value = classData.id_lh; // ID lớp học
    document.getElementById('ten_lh').value = classData.lophoc; // Tên lớp
    document.getElementById('nam_hoc').value = classData.nam_hoc.id_nh; // Năm học

    // Kiểm tra nếu existingTeachers là mảng và thêm giáo viên đã được chỉ định
    const existingTeachers = classData.giao_vien || []; // Giả sử trường này chứa danh sách giáo viên

    if (Array.isArray(existingTeachers)) {
        for (const teacher of existingTeachers) {
            const teacherEntry = createTeacherEntry(teacher.id_gv); // Tạo phần nhập cho giáo viên
            document.getElementById("teacher-container").appendChild(teacherEntry);
            await populateTeacherSelect(teacherEntry.querySelector('select'), token); // Đợi cho danh sách giáo viên được điền vào select
        }
    } else {
        console.warn('existingTeachers không phải là mảng:', existingTeachers);
    }
}

// Hàm tạo phần nhập giáo viên
function createTeacherEntry(teacherId = '') {
    const teacherEntry = document.createElement("div");
    teacherEntry.classList.add("teacher-entry");
    teacherEntry.innerHTML = `
        <select name="giao_vien[]" required>
            <option value="">Chọn giáo viên</option>
            <!-- Các giáo viên sẽ được thêm từ cơ sở dữ liệu -->
        </select>
        <button type="button" class="btn-remove-teacher">Xóa</button>
    `;
    teacherEntry.querySelector('.btn-remove-teacher').addEventListener('click', () => {
        teacherEntry.remove();
    });

    // Gán ID giáo viên nếu có
    if (teacherId) {
        const teacherSelect = teacherEntry.querySelector('select');
        teacherSelect.value = teacherId; // Gán ID giáo viên vào select
    }

    return teacherEntry;
}

// Hàm thêm phần nhập giáo viên mới
async function addTeacherEntry(token) {
    const teacherContainer = document.getElementById("teacher-container");
    const teacherEntry = createTeacherEntry();
    teacherContainer.appendChild(teacherEntry);

    // Điền danh sách giáo viên vào select
    await populateTeacherSelect(teacherEntry.querySelector('select'), token); // Đợi cho danh sách giáo viên được điền vào select
}

// Hàm cập nhật thông tin lớp học
async function updateClassInfo(classId, token) {
    const ten_lh = document.getElementById('ten_lh').value;
    const nam_hoc = document.getElementById('nam_hoc').value;

    // Lấy danh sách giáo viên đã chọn
    const teacherSelects = document.querySelectorAll('select[name="giao_vien[]"]');
    const giao_vien = Array.from(teacherSelects).map(select => Number(select.value)).filter(value => value);

    try {
        const response = await fetch(`http://localhost:8000/admin/classes/${classId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_lh: classId,  // Đảm bảo bạn bao gồm id_lh
                lophoc: ten_lh,
                id_nh: Number(nam_hoc),
                id_gv: giao_vien
            })
        });

        if (response.ok) {
            alert('Cập nhật thành công!');
            window.location.href = '../ql_lophoc.html'; // Quay lại trang danh sách lớp học
        } else {
            const errorData = await response.json();
            console.error('Error data:', errorData);
            alert(errorData.detail || 'Có lỗi xảy ra khi cập nhật thông tin.');
        }
    } catch (error) {
        console.error('Lỗi khi cập nhật:', error);
        alert('Có lỗi xảy ra khi cập nhật thông tin.');
    }
}

// Hàm lấy danh sách giáo viên và điền vào select
async function fetchTeachers(token) {
    const apiUrlTeachers = 'http://localhost:8000/admin/teachers'; // Địa chỉ API lấy danh sách giáo viên

    try {
        const response = await fetch(apiUrlTeachers, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.detail || 'Lỗi khi lấy danh sách giáo viên');
            return;
        }

        const teachers = await response.json();
        // Thêm giáo viên vào tất cả các select trong container
        const teacherSelects = document.querySelectorAll('select[name="giao_vien[]"]');
        teacherSelects.forEach(select => {
            teachers.forEach(teacher => {
                const option = document.createElement('option');
                option.value = teacher.id_gv; // Giá trị là ID giáo viên
                option.textContent = teacher.ten_gv; // Hiển thị tên giáo viên
                select.appendChild(option);
            });
        });
    } catch (error) {
        console.error('Lỗi:', error);
    }
}

// Hàm lấy danh sách năm học và điền vào select
async function fetchAcademicYears(token) {
    const apiUrlYears = 'http://localhost:8000/admin/years'; // Địa chỉ API lấy danh sách năm học
    const yearSelect = document.getElementById('nam_hoc'); // ID của select năm học

    try {
        const response = await fetch(apiUrlYears, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.detail || 'Lỗi khi lấy danh sách năm học');
            return;
        }

        const academicYears = await response.json();
        // Điền danh sách năm học vào select
        academicYears.forEach(year => {
            const option = document.createElement('option');
            option.value = year.id_nh; // Giá trị là ID năm học
            option.textContent = year.namhoc; // Hiển thị tên năm học
            yearSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Lỗi:', error);
    }
}

// Hàm chuyển hướng đến trang đăng nhập
function redirectToLogin() {
    window.location.href = 'login.html';
}

// Hàm điền danh sách giáo viên vào select
async function populateTeacherSelect(select, token) {
    const apiUrlTeachers = 'http://localhost:8000/admin/teachers'; // Địa chỉ API lấy danh sách giáo viên

    try {
        const response = await fetch(apiUrlTeachers, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.detail || 'Lỗi khi lấy danh sách giáo viên');
            return;
        }

        const teachers = await response.json();
        // Xóa các option cũ trong select
        select.innerHTML = '<option value="">Chọn giáo viên</option>'; // Reset danh sách

        // Thêm giáo viên vào select
        teachers.forEach(teacher => {
            const option = document.createElement('option');
            option.value = teacher.id_gv; // Giá trị là ID giáo viên
            option.textContent = teacher.ten_gv; // Hiển thị tên giáo viên
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Lỗi:', error);
    }
}
