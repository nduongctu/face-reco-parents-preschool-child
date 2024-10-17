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

    // Xử lý ảnh đại diện
    const pictureInput = document.querySelector('input[name="picture"]');
    const profilePicture = document.querySelector("#profile-picture"); // Lấy hình ảnh đại diện

    // Lấy ảnh học sinh hiện tại khi tải trang
    const getStudentImage = async () => {
        try {
            const response = await fetch(`http://localhost:8000/admin/images/hoc-sinh/${studentId}/`, {
                method: "GET",
                headers: {'Authorization': `Bearer ${token}`} // Thêm token nếu cần
            });
            if (response.ok) {
                const image = await response.json();
                profilePicture.src = image.image_path; // Cập nhật src của hình ảnh đại diện
            } else {
                console.error("Không thể lấy ảnh học sinh.");
            }
        } catch (error) {
            console.error("Lỗi:", error);
        }
    };

    // Gọi hàm để tải ảnh học sinh khi tải trang
    await getStudentImage();

    const getUserImage = async () => {
        try {
            const response = await fetch(`http://localhost:8000/admin/images/hoc-sinh/${studentId}/`, {
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
            formData.append("id_hs", studentId); // Thêm id_hs vào FormData

            try {
                const response = await fetch(`http://localhost:8000/admin/images/hoc-sinh/${studentId}/`, {
                    method: "PUT",
                    headers: {
                        'Authorization': `Bearer ${token}` // Thêm token nếu cần
                    },
                    body: formData,
                });

                if (response.ok) {
                    alert("Cập nhật ảnh đại diện thành công!");
                    await getStudentImage(); // Tải lại ảnh mới
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

// Hàm lấy thông tin học sinh từ API
async function fetchStudentData(studentId, token) {
    try {
        const response = await fetch(`http://localhost:8000/admin/students/${studentId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.detail || 'Không thể tải thông tin học sinh.');
            window.location.href = 'hocsinh.html';
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching student data:', error);
        alert('Có lỗi xảy ra khi tải thông tin học sinh.');
        return null;
    }
}

// Hàm hiển thị thông tin học sinh vào biểu mẫu
function populateStudentForm(student) {
    document.getElementById('student-id').value = student.id_hs;
    document.getElementById('ten_hs').value = student.ten_hs;
    document.getElementById('gioitinh_hs').value = student.gioitinh_hs;
    document.getElementById('ngaysinh_hs').value = student.ngaysinh_hs;

    // Thiết lập ID lớp học vào select
    const classSelect = document.getElementById('lop_hoc_ten');
    classSelect.value = student.lop_hoc_ten; // Đây là ID lớp học

    const parentContainer = document.getElementById("parent-container");
    student.phu_huynh.forEach(phuHuynh => {
        const parentEntry = createParentEntry(phuHuynh.ten_ph, phuHuynh.quanhe, phuHuynh.id_ph, phuHuynh.gioitinh_ph);
        parentContainer.appendChild(parentEntry);
    });
}

// Hàm tạo phần nhập thông tin phụ huynh với giới tính
function createParentEntry(tenPh = '', quanHe = '', idPh = '', gioiTinhPh = '') {
    const parentEntry = document.createElement("div");
    parentEntry.classList.add("parent-entry");
    parentEntry.innerHTML = `
        <input type="hidden" value="${idPh}" placeholder="ID Phụ Huynh">
        <input type="text" value="${tenPh}" placeholder="Tên Phụ Huynh" required>
        <select required>
            <option value="${quanHe}">${quanHe ? quanHe : 'Chọn quan hệ'}</option>
            <option value="Cha">Cha</option>
            <option value="Mẹ">Mẹ</option>
            <option value="Người Giám Hộ">Người Giám Hộ</option>
        </select>
        <select required>
            <option value="${gioiTinhPh}">${gioiTinhPh ? gioiTinhPh : 'Chọn giới tính'}</option>
            <option value="Nam">Nam</option>
            <option value="Nữ">Nữ</option>
        </select>
        <button type="button" class="btn-remove-parent">Xóa</button>
    `;
    parentEntry.querySelector('.btn-remove-parent').addEventListener('click', () => {
        parentEntry.remove();
    });
    return parentEntry;
}

// Hàm thêm phần nhập phụ huynh mới
function addParentEntry() {
    const parentContainer = document.getElementById("parent-container");
    const parentEntry = createParentEntry();
    parentContainer.appendChild(parentEntry);
}

// Hàm cập nhật thông tin học sinh
async function updateStudentInfo(studentId, token) {
    const ten_hs = document.getElementById('ten_hs').value;
    const gioitinh_hs = document.getElementById('gioitinh_hs').value;
    const ngaysinh_hs = document.getElementById('ngaysinh_hs').value;
    const lop_hoc_ten = document.getElementById('lop_hoc_ten').value; // Lấy ID lớp học

    const parentEntries = document.querySelectorAll(".parent-entry");
    const phu_huynh = [];
    parentEntries.forEach(entry => {
        const tenPh = entry.querySelector('input[type="text"]').value;
        const quanHe = entry.querySelector('select').value;
        const gioiTinhPh = entry.querySelectorAll('select')[1].value; // Lấy giá trị giới tính
        let idPh = entry.querySelector('input[type="hidden"]').value; // Lấy ID phụ huynh

        // Kiểm tra và chuyển đổi idPh từ chuỗi rỗng sang null nếu không có ID
        if (idPh === "") {
            idPh = null;
        }

        // Đảm bảo rằng giới tính không được bỏ trống
        if (gioiTinhPh === "" || gioiTinhPh === "Chọn giới tính") {
            alert("Vui lòng chọn giới tính cho phụ huynh.");
            return;
        }

        phu_huynh.push({ten_ph: tenPh, quanhe: quanHe, id_ph: idPh, gioitinh_ph: gioiTinhPh}); // Thêm giới tính vào mảng
    });

    console.log('Thông tin học sinh:', {
        ten_hs, gioitinh_hs, ngaysinh_hs, lop_hoc_ten, phu_huynh
    });

    try {
        const response = await fetch(`http://localhost:8000/admin/students/${studentId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ten_hs, gioitinh_hs, ngaysinh_hs, lop_hoc_ten, phu_huynh
            })
        });

        if (response.ok) {
            alert('Cập nhật thành công!');
            window.location.href = 'hocsinh.html'; // Quay lại trang danh sách học sinh
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

// Hàm lấy danh sách lớp học và điền vào select
async function fetchClasses() {
    const apiUrlClasses = 'http://localhost:8000/admin/classes'; // Địa chỉ API lấy danh sách lớp học
    const classSelect = document.getElementById('lop_hoc_ten');

    try {
        const response = await fetch(apiUrlClasses);
        if (!response.ok) {
            const errorData = await response.json(); // Lấy thông tin lỗi từ response nếu có
            alert(errorData.detail || 'Lỗi khi lấy lớp học'); // Hiển thị thông báo lỗi
            return; // Kết thúc hàm nếu có lỗi
        }

        const classes = await response.json();
        classes.forEach(cls => {
            const option = document.createElement('option');
            option.value = cls.id_lh; // Giá trị là ID lớp học
            option.textContent = cls.lophoc; // Hiển thị tên lớp học
            classSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Lỗi:', error);
    }
}

// Hàm chuyển hướng về trang đăng nhập
function redirectToLogin() {
    setTimeout(() => {
        window.location.href = '../../auth/login.html';
    }, 3000);
}
