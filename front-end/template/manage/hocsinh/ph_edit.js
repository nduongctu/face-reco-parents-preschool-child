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

    // Hiển thị hình ảnh hiện tại nếu có
    if (parent.hinhanh_ph && Array.isArray(parent.hinhanh_ph)) {
        const imagePreviewContainer = document.getElementById('image-preview');
        imagePreviewContainer.innerHTML = ''; // Xóa hình ảnh cũ
        parent.hinhanh_ph.forEach(imagePath => {
            const img = document.createElement('img');
            img.src = imagePath;
            img.alt = 'Parent Image';
            img.style.maxWidth = '200px';
            img.style.margin = '5px';
            imagePreviewContainer.appendChild(img);
        });
    }
}

async function updateParentInfo(parentId, token) {
    const safeGetValue = (id) => {
        const element = document.getElementById(id);
        return element ? element.value.trim() || null : null;
    };

    const formData = new FormData();

    // Thêm các trường thông tin cơ bản
    formData.append('ten_ph', safeGetValue('ten_ph'));
    formData.append('gioitinh_ph', safeGetValue('gioitinh_ph'));
    formData.append('ngaysinh_ph', safeGetValue('ngaysinh_ph'));
    formData.append('sdt_ph', safeGetValue('sdt_ph'));
    formData.append('diachi_ph', safeGetValue('diachi_ph'));
    formData.append('quanhe', safeGetValue('quanhe'));

    // Kiểm tra số điện thoại có 10 chữ số
    if (formData.get('sdt_ph') && formData.get('sdt_ph').length !== 10) {
        alert('Số điện thoại phải có 10 chữ số.');
        return;
    }

    // Thêm tệp hình ảnh
    const imageInput = document.getElementById('hinhanh');
    if (imageInput && imageInput.files.length > 0) {
        for (let i = 0; i < imageInput.files.length; i++) {
            formData.append('files', imageInput.files[i]);
        }
    }

    // Xử lý hinhanh_ph
    const currentImages = document.querySelectorAll('#image-preview img');
    const hinhanhPh = Array.from(currentImages).map(img => img.src);
    if (hinhanhPh.length > 0) {
        hinhanhPh.forEach((imagePath, index) => {
            formData.append(`hinhanh_ph[${index}]`, imagePath);
        });
    } else {
        // Nếu không có hình ảnh, gửi một mảng rỗng
        formData.append('hinhanh_ph', '');
    }

    try {
        const response = await fetch(`http://localhost:8000/admin/parents/${parentId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
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
