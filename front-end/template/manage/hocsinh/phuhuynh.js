document.addEventListener('DOMContentLoaded', async function () {
    const token = localStorage.getItem('access_token');

    // Kiểm tra token
    if (!token) {
        alert('Token không tồn tại! Vui lòng đăng nhập lại.');
        redirectToLogin();
        return;
    }

    // Lấy thông tin người dùng để lấy ID học sinh
    const userData = await fetchUserData(token);
    if (!userData || !userData.id_hs) {
        alert('ID học sinh không hợp lệ!');
        redirectToLogin();
        return;
    }

    const studentId = userData.id_hs; // Lấy ID học sinh từ dữ liệu người dùng

    // Lấy thông tin phụ huynh từ API
    const parents = await fetchParentsData(studentId, token);
    if (!parents) return;

    // Hiển thị thông tin phụ huynh vào bảng
    populateParentsTable(parents);
});

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

        return await response.json(); // Trả về thông tin người dùng
    } catch (error) {
        console.error('Lỗi khi lấy thông tin người dùng:', error);
        alert('Có lỗi xảy ra khi lấy thông tin người dùng.');
        return null;
    }
}

// Hàm lấy thông tin phụ huynh từ API
async function fetchParentsData(studentId, token) {
    try {
        const response = await fetch(`http://localhost:8000/admin/students/${studentId}/parents`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.detail || 'Không thể tải thông tin phụ huynh.');
            return null;
        }

        return await response.json(); // Trả về danh sách phụ huynh
    } catch (error) {
        console.error('Lỗi khi lấy thông tin phụ huynh:', error);
        alert('Có lỗi xảy ra khi tải thông tin phụ huynh.');
        return null;
    }
}

// Hàm điền dữ liệu phụ huynh vào bảng
function populateParentsTable(parents) {
    const phList = document.getElementById('ph-list');
    phList.innerHTML = ''; // Xóa nội dung hiện tại

    parents.forEach(parent => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${parent.id_ph || 'Chưa có thông tin'}</td>
            <td>${parent.ten_ph || 'Chưa có thông tin'}</td>
            <td>${parent.gioitinh_ph || 'Chưa có thông tin'}</td>
            <td>${parent.ngaysinh_ph || 'Chưa có thông tin'}</td>
            <td>${parent.sdt_ph || 'Chưa có thông tin'}</td>
            <td>${parent.diachi_ph || 'Chưa có thông tin'}</td>
            <td>${parent.quanhe || 'Chưa có thông tin'}</td>
            <td><button class="btn-edit" data-id="${parent.id_ph}">Chỉnh Sửa</button></td>
            <td><button class="btn-delete" data-id="${parent.id_ph}">Xóa</button></td>
        `;
        phList.appendChild(row);
    });

    // Thêm sự kiện cho nút xóa
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.getAttribute('data-id');
            confirmDeleteParent(id);
        });
    });

    // Thêm sự kiện cho nút chỉnh sửa
    document.querySelectorAll('.btn-edit').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.getAttribute('data-id');
            redirectToEditPage(id); // Chuyển hướng tới trang chỉnh sửa
        });
    });
}

// Hàm chuyển hướng đến trang chỉnh sửa
function redirectToEditPage(id) {
    window.location.href = `edit_ph.html?id=${id}`; // Chuyển hướng và truyền ID phụ huynh
}

// Hàm xác nhận xóa phụ huynh
function confirmDeleteParent(id) {
    const popupOverlay = document.getElementById('popup-overlay');
    popupOverlay.style.display = 'block';

    document.getElementById('confirm-delete').onclick = async () => {
        await deleteParent(id);
        popupOverlay.style.display = 'none';
    };

    document.getElementById('cancel-delete').onclick = () => {
        popupOverlay.style.display = 'none';
    };
}

// Hàm xóa phụ huynh
async function deleteParent(id) {
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`http://localhost:8000/admin/parents/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert('Xóa phụ huynh thành công!');
            location.reload(); // Tải lại trang để cập nhật bảng
        } else {
            const errorData = await response.json();
            alert(errorData.detail || 'Có lỗi xảy ra khi xóa phụ huynh.');
        }
    } catch (error) {
        console.error('Lỗi khi xóa phụ huynh:', error);
        alert('Có lỗi xảy ra khi xóa phụ huynh.');
    }
}

// Hàm chuyển hướng về trang đăng nhập
function redirectToLogin() {
    setTimeout(() => {
        window.location.href = '../../auth/login.html';
    }, 3000);
}
