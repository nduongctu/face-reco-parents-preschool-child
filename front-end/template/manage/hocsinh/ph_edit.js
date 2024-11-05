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

    await fetchAndDisplayAllImages(parentId); // Gọi hàm để lấy tất cả ảnh của phụ huynh khi trang được tải
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

    const payload = {
        ten_ph: safeGetValue('ten_ph'),
        gioitinh_ph: safeGetValue('gioitinh_ph'),
        ngaysinh_ph: safeGetValue('ngaysinh_ph'),
        sdt_ph: safeGetValue('sdt_ph'),
        diachi_ph: safeGetValue('diachi_ph'),
        quanhe: safeGetValue('quanhe'),
    };

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

async function fetchAndDisplayAllImages(parentId) {
    try {
        const response = await fetch(`http://localhost:8000/admin/images/phu-huynh/${parentId}/`);
        if (response.ok) {
            const images = await response.json();
            console.log("Dữ liệu trả về từ API:", images);  // In ra dữ liệu để kiểm tra
            displayUploadedPictures(images);
        } else if (response.status === 404) {
            console.log("Không có ảnh nào cho phụ huynh này.");
            alert("Không có ảnh nào cho phụ huynh này.");
            displayUploadedPictures([]); // Xóa ảnh cũ
        } else {
            console.error("Lấy ảnh không thành công");
            alert("Lỗi: Không thể lấy ảnh.");
        }
    } catch (error) {
        console.error("Lỗi khi gọi API:", error);
        alert("Đã xảy ra lỗi khi lấy ảnh.");
    }
}

document.getElementById("upload-picture-button").addEventListener("click", () => {
    document.getElementById("file-input").click();
});

document.getElementById("file-input").addEventListener("change", async function () {
    const parentId = getParentIdFromURL();
    const files = this.files;
    const formData = new FormData();

    for (let file of files) {
        formData.append("file", file);
    }

    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`http://localhost:8000/admin/images/phu-huynh/${parentId}/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}` // Thêm token vào headers
            },
            body: formData
        });

        if (response.ok) {
            // Gọi lại hàm để lấy tất cả ảnh
            await fetchAndDisplayAllImages(parentId);
        } else {
            console.error("Tải ảnh lên thất bại");
            const errorData = await response.json();
            alert("Lỗi: " + errorData.detail);
        }
    } catch (error) {
        console.error("Lỗi:", error);
        alert("Đã xảy ra lỗi khi tải ảnh lên.");
    }
});

function displayUploadedPictures(images) {
    const uploadedPicturesContainer = document.getElementById("uploaded-pictures");
    uploadedPicturesContainer.innerHTML = '';

    if (!Array.isArray(images) || images.length === 0) {
        console.log("Không có ảnh nào để hiển thị.");
        return;
    }

    images.forEach(image => {
        const imgWrapper = document.createElement("div");
        imgWrapper.classList.add("image-wrapper");
        imgWrapper.id = `image-${image.id_ph}`;

        const imgElement = document.createElement("img");
        imgElement.src = image.image_path;
        imgElement.alt = "Ảnh đại diện";

        const deleteButton = document.createElement("button");
        deleteButton.classList.add("delete-button");

        // Thêm hình ảnh icon xóa vào nút
        const iconElement = document.createElement("img");
        iconElement.src = "../../images/x_icon.png"; // Đường dẫn đến icon xóa
        iconElement.alt = "Xóa ảnh"; // Thêm thuộc tính alt cho hình ảnh

        deleteButton.appendChild(iconElement); // Thêm icon vào nút xóa
        deleteButton.addEventListener("click", async () => {
            const confirmDelete = confirm("Bạn có chắc chắn muốn xóa ảnh này?");
            if (!confirmDelete) return;

            try {
                const response = await fetch(`http://localhost:8000/admin/images/phu-huynh/${image.id_ph}/`, {
                    method: "DELETE",
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    console.error("Lỗi khi xóa ảnh:", errorData.detail);
                    alert("Lỗi khi xóa ảnh: " + errorData.detail);
                    return;
                }

                alert("Ảnh đã được xóa thành công");
                document.getElementById(`image-${image.id_ph}`).remove();
            } catch (error) {
                console.error("Lỗi hệ thống khi xóa ảnh:", error);
                alert("Đã xảy ra lỗi hệ thống khi xóa ảnh.");
            }
        });

        imgWrapper.appendChild(imgElement);
        imgWrapper.appendChild(deleteButton);
        uploadedPicturesContainer.appendChild(imgWrapper);
    });
}
