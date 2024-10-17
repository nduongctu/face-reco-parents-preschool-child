document.addEventListener('DOMContentLoaded', async function () {
    const token = localStorage.getItem('access_token');
    const parentId = getParentIdFromURL();

    if (!token) {
        alert('Token không tồn tại! Vui lòng đăng nhập lại.');
        redirectToLogin();
        return;
    }

    const parentData = await fetchParentData(parentId, token);
    if (parentData) {
        populateParentForm(parentData);
    }

    document.getElementById('edit-parent-form').addEventListener('submit', async function (event) {
        event.preventDefault();
        await updateParentInfo(parentId, token);
    });
});

function getParentIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id');
}

async function fetchParentData(parentId, token) {
    try {
        const response = await fetch(`http://localhost:8000/admin/parents/${parentId}`, {
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

        return await response.json();
    } catch (error) {
        console.error('Error fetching parent data:', error);
        alert('Có lỗi xảy ra khi tải thông tin phụ huynh.');
        return null;
    }
}

function populateParentForm(parent) {
    const safeSetValue = (id, value) => {
        const element = document.getElementById(id);
        if (element) element.value = value || '';
    };

    safeSetValue('ten_ph', parent.ten_ph);
    safeSetValue('gioitinh_ph', parent.gioitinh_ph);
    safeSetValue('ngaysinh_ph', parent.ngaysinh_ph ? parent.ngaysinh_ph.slice(0, 10) : '');
    safeSetValue('sdt_ph', parent.sdt_ph);
    safeSetValue('diachi_ph', parent.diachi_ph);
    safeSetValue('quanhe', parent.quanhe);
}

async function updateParentInfo(parentId, token) {
    const safeGetValue = (id) => {
        const element = document.getElementById(id);
        return element ? element.value.trim() || null : null;
    };

    // Create a JavaScript object to hold the form data
    const payload = {
        ten_ph: safeGetValue('ten_ph'),
        gioitinh_ph: safeGetValue('gioitinh_ph'),
        ngaysinh_ph: safeGetValue('ngaysinh_ph'),
        sdt_ph: safeGetValue('sdt_ph'),
        diachi_ph: safeGetValue('diachi_ph'),
        quanhe: safeGetValue('quanhe'),
    };

    // Validate phone number (10 digits)
    if (payload.sdt_ph && payload.sdt_ph.length !== 10) {
        alert('Số điện thoại phải có 10 chữ số.');
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/admin/parents/${parentId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert('Cập nhật thông tin phụ huynh thành công!');
            window.location.href = 'phuhuynh.html';
        } else {
            const errorData = await response.json();
            console.error('Server response:', errorData);
            alert(errorData.detail || 'Có lỗi xảy ra khi cập nhật thông tin.');
        }
    } catch (error) {
        console.error('Lỗi khi cập nhật thông tin phụ huynh:', error);
        alert('Có lỗi xảy ra khi cập nhật thông tin.');
    }
}

function redirectToLogin() {
    window.location.href = '../../auth/login.html';
}
