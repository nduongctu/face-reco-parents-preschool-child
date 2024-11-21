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
    await populateClassForm(classData); // Đợi cho quá trình điền form hoàn thành

    // Lấy danh sách giáo viên và lưu vào biến
    const teachers = await fetchTeachers(token); // Lấy danh sách giáo viên từ API

    // Lấy danh sách năm học và điền vào select
    await fetchAcademicYears(token);

    // Xử lý sự kiện gửi biểu mẫu
    document.getElementById('edit-class-form').addEventListener('submit', async function (event) {
        event.preventDefault();
        await updateClassInfo(classId, token);
    });

    // Thêm sự kiện cho nút "Thêm Giáo Viên"
    document.getElementById("btn-add-teacher").addEventListener('click', async function () {
        await addTeacherEntry(teachers); // Thêm phần nhập giáo viên mới với danh sách giáo viên
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
        console.error('Lỗi khi lấy thông tin người dùng:', error);
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
        console.error('Lỗi khi lấy thông tin lớp học:', error);
        alert('Có lỗi xảy ra khi tải thông tin lớp học.');
        return null;
    }
}

async function populateClassForm(classData) {
    // Điền thông tin lớp học vào form
    document.getElementById('id_lh').value = classData.id_lh; // ID lớp học
    document.getElementById('ten_lh').value = classData.lophoc; // Tên lớp
    document.getElementById('nam_hoc').value = classData.nam_hoc.id_nh; // Năm học

    // Xóa tất cả phần nhập giáo viên cũ trước khi thêm mới
    const teacherContainer = document.getElementById("teacher-container");
    teacherContainer.innerHTML = ''; // Reset container

    // Lấy danh sách giáo viên và điền vào select
    await populateTeachersSelect(classData.giao_vien); // Sử dụng dữ liệu từ classData
}

async function populateTeachersSelect(teachers) {
    const teacherContainer = document.getElementById("teacher-container");

    // Thêm từng giáo viên vào form
    if (Array.isArray(teachers) && teachers.length > 0) {
        for (const teacher of teachers) {
            const teacherEntry = createTeacherEntry(teacher.id_gv, teacher.ten_gv);
            teacherContainer.appendChild(teacherEntry);
        }
    } else {
        console.warn('Không có giáo viên nào được chỉ định cho lớp này.');
    }
}

// Hàm tạo phần nhập giáo viên
function createTeacherEntry(teacherId = '', teacherName = '') {
    const teacherEntry = document.createElement("div");
    teacherEntry.classList.add("teacher-entry");
    teacherEntry.innerHTML = `
        <select name="giao_vien[]" required>
            <option value="">Chọn giáo viên</option>
        </select>
        <button type="button" class="btn-remove-teacher">Xóa</button>
    `;

    const teacherSelect = teacherEntry.querySelector('select');

    // Nếu có tên giáo viên, thêm nó vào ô select
    if (teacherName) {
        const option = document.createElement('option');
        option.value = teacherId; // Giá trị là ID giáo viên
        option.textContent = teacherName; // Hiển thị tên giáo viên
        teacherSelect.appendChild(option); // Thêm tên giáo viên vào select
        teacherSelect.value = teacherId; // Đảm bảo ID giáo viên được chọn
    }

    teacherEntry.querySelector('.btn-remove-teacher').addEventListener('click', () => {
        teacherEntry.remove();
    });

    return teacherEntry;
}

// Hàm thêm phần nhập giáo viên mới
async function addTeacherEntry(teachers) {
    const teacherContainer = document.getElementById("teacher-container");
    const teacherEntry = createTeacherEntry(); // Tạo một ô nhập giáo viên mới

    // Thêm danh sách giáo viên vào select cho phần mới thêm
    const teacherSelect = teacherEntry.querySelector('select');
    teachers.forEach(teacher => {
        const option = document.createElement('option');
        option.value = teacher.id_gv; // Giá trị là ID giáo viên
        option.textContent = teacher.ten_gv; // Hiển thị tên giáo viên
        teacherSelect.appendChild(option);
    });

    // Kiểm tra nếu giáo viên đã có lớp khác
    teacherSelect.addEventListener('change', async (event) => {
        const selectedTeacherId = event.target.value;

        if (selectedTeacherId) {
            const teacherData = await checkTeacherClass(selectedTeacherId);

            if (teacherData && teacherData.id_lh !== null) { // Kiểm tra xem giáo viên đã có lớp nào chưa
                const confirmChange = confirm(`Giáo viên ${teacherData.ten_gv} đã có lớp "${teacherData.lop_hoc_ten}". Bạn có muốn thay đổi không?`);
                if (!confirmChange) {
                    teacherSelect.value = ""; // Nếu không xác nhận, reset select
                }
            }
        }
    });

    teacherContainer.appendChild(teacherEntry); // Thêm ô nhập vào container giáo viên
}

// Cập nhật thông tin lớp học
async function updateClassInfo(classId, token) {
    const ten_lh = document.getElementById('ten_lh').value;
    const nam_hoc = document.getElementById('nam_hoc').value;

    const teacherSelects = document.querySelectorAll('select[name="giao_vien[]"]');
    const giao_vien = Array.from(teacherSelects).map(select => Number(select.value)).filter(value => value);

    // Kiểm tra dữ liệu trước khi cập nhật
    if (!ten_lh || !nam_hoc || giao_vien.length === 0) {
        alert('Vui lòng điền đầy đủ thông tin lớp học và giáo viên.');
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/admin/classes/${classId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_lh: classId,
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
            console.error('Dữ liệu lỗi:', errorData);
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
            return [];
        }

        return await response.json(); // Trả về danh sách giáo viên
    } catch (error) {
        console.error('Lỗi:', error);
        return []; // Trả về danh sách giáo viên rỗng khi có lỗi
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

async function checkTeacherClass(teacherId) {
    const apiUrl = `http://localhost:8000/admin/teachers/${teacherId}`; // Địa chỉ API kiểm tra lớp của giáo viên

    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.detail || 'Lỗi khi lấy thông tin giáo viên.');
            return null; // Nếu không lấy được thông tin, trả về null
        }

        return await response.json(); // Trả về thông tin giáo viên
    } catch (error) {
        console.error('Lỗi khi kiểm tra lớp của giáo viên:', error);
        return null; // Xử lý lỗi
    }
}
