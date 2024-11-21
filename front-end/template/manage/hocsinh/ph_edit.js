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

    await fetchAndDisplayAllImages(parentId);
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
            displayUploadedPictures(images);
        } else if (response.status === 404) {
            console.log("Không có ảnh nào cho phụ huynh này.");
            alert("Không có ảnh nào cho phụ huynh này.");
            displayUploadedPictures([]);
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

let cropper;

function openCropModal(imageSrc) {
    const cropModal = document.getElementById("crop-modal");
    const imageElement = document.getElementById("image-to-crop");

    imageElement.src = imageSrc;  // Cập nhật nguồn ảnh
    cropModal.style.display = "block";  // Hiển thị modal

    // Tạo cropper cho ảnh
    cropper = new Cropper(imageElement, {
        aspectRatio: 1,  // Tỷ lệ cắt vuông
        viewMode: 1,     // Chế độ xem ảnh
    });
}

document.getElementById("file-input").addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
            openCropModal(event.target.result);  // Mở modal với ảnh đã chọn
        };
        reader.readAsDataURL(file);
    }
});

document.getElementById("crop-button").addEventListener("click", async function () {
    const parentId = getParentIdFromURL();
    const croppedCanvas = cropper.getCroppedCanvas({
        width: 256,
        height: 256,
    });

    croppedCanvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append("file", blob, "cropped_image.jpg");

        const token = localStorage.getItem('access_token');

        try {
            const response = await fetch(`http://localhost:8000/admin/images/phu-huynh/${parentId}/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (response.ok) {
                alert("Ảnh đã được tải lên thành công.");
                closeCropModal();
                await fetchAndDisplayAllImages(parentId);
            } else {
                const errorData = await response.json();
                alert("Lỗi khi tải ảnh lên: " + errorData.detail);
            }
        } catch (error) {
            console.error("Lỗi:", error);
            alert("Đã xảy ra lỗi khi tải ảnh lên.");
        }
    });
});

function closeCropModal() {
    const cropModal = document.getElementById("crop-modal");
    cropModal.style.display = "none";  // Ẩn modal khi đóng
    if (cropper) {
        cropper.destroy();  // Hủy cropper khi đóng modal
        cropper = null;
    }
}

document.getElementById("close-crop-modal").addEventListener("click", closeCropModal);

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
        imgWrapper.id = `image-${image.id_image}`;  // Dùng id_image cho đúng

        const imgElement = document.createElement("img");
        imgElement.src = image.image_path;
        imgElement.alt = "Ảnh đại diện";

        const deleteButton = document.createElement("button");
        deleteButton.classList.add("delete-button");

        const iconElement = document.createElement("img");
        iconElement.src = "../../images/x_icon.png";
        iconElement.alt = "Xóa ảnh";

        deleteButton.appendChild(iconElement);
        deleteButton.addEventListener("click", async () => {
            const confirmDelete = confirm("Bạn có chắc chắn muốn xóa ảnh này?");
            if (!confirmDelete) return;

            try {
                const response = await fetch(`http://localhost:8000/admin/images/phu-huynh/${image.id_image}/`, {
                    method: "DELETE",
                    headers: {
                        "Authorization": `Bearer ${localStorage.getItem('access_token')}`
                    }
                });

                // Kiểm tra xem response có thành công không
                if (!response.ok) {
                    const errorData = await response.json();
                    console.error("Lỗi khi xóa ảnh:", errorData.detail);
                    alert("Lỗi khi xóa ảnh: " + errorData.detail);
                    return;
                }

                alert("Ảnh đã được xóa thành công");

                // Xóa ảnh khỏi DOM sau khi xóa thành công từ backend
                document.getElementById(`image-${image.id_image}`).remove();  // Sử dụng id_image để xóa đúng
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
