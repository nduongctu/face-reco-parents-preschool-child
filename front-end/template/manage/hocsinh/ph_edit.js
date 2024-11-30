document.addEventListener('DOMContentLoaded', async function () {
    const token = localStorage.getItem('access_token');
    const parentId = getParentIdFromURL();
    const uploadPictureButton = document.getElementById('upload-picture-button');
    const imageOptionsModal = document.getElementById('image-options-modal');
    const closeModalButton = document.getElementById('close-modal-button');
    const uploadExistingButton = document.getElementById('upload-existing-button');
    const capturePhotoButton = document.getElementById('capture-photo-button');
    const captureButton = document.getElementById('capture-button');
    const cancelButton = document.getElementById('cancel-button');
    const cameraPreview = document.getElementById('camera-preview');

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

    uploadPictureButton.addEventListener("click", function () {
        imageOptionsModal.style.display = "block"; // Hiển thị modal
    });

    closeModalButton.addEventListener("click", function () {
        imageOptionsModal.style.display = "none"; // Ẩn modal
    });

    uploadExistingButton.addEventListener("click", function () {
        document.getElementById("file-input").click(); // Mở file input
        imageOptionsModal.style.display = "none"; // Ẩn modal
    });

    captureButton.addEventListener("click", function () {
        captureImage(); // Chụp ảnh và mở modal cắt ảnh
    });

    cancelButton.addEventListener("click", function () {
        stopCamera(); // Dừng camera
        cameraPreview.style.display = 'none'; // Ẩn camera preview
        imageOptionsModal.style.display = "none"; // Đóng modal
    });

    capturePhotoButton.addEventListener("click", function () {
        startCamera(); // Bật camera
        imageOptionsModal.style.display = "none"; // Ẩn modal
    });
});

// Lấy ID phụ huynh từ URL
function getParentIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id');
}

// Lấy thông tin phụ huynh từ API
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

// Điền thông tin vào form
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

// Cập nhật thông tin phụ huynh
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

// Chuyển hướng về trang đăng nhập nếu không có token
function redirectToLogin() {
    window.location.href = '../../auth/login.html';
}

// Lấy và hiển thị ảnh đã tải lên
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

// Mở camera để chụp ảnh
function startCamera() {
    const video = document.getElementById('video');
    const cameraPreview = document.getElementById('camera-preview');
    cameraPreview.style.display = 'block'; // Hiển thị preview camera

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({video: true})
            .then(function (stream) {
                video.srcObject = stream;
            })
            .catch(function (error) {
                alert('Không thể truy cập vào camera của bạn.');
            });
    }
}

// Dừng camera khi hủy
function stopCamera() {
    const video = document.getElementById('video');
    const cameraPreview = document.getElementById('camera-preview');
    cameraPreview.style.display = 'none'; // Ẩn camera preview

    if (video.srcObject) {
        const stream = video.srcObject;
        const tracks = stream.getTracks();

        tracks.forEach(track => track.stop()); // Dừng tất cả các track của camera
    }
}

document.getElementById("capture-button").addEventListener("click", async function () {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');

    // Vẽ khung hình video lên canvas
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Lấy ảnh từ canvas và hiển thị trong modal cắt ảnh
    const imageSrc = canvas.toDataURL('image/jpeg');

    // Mở modal cắt ảnh và truyền ảnh vào
    openCropModal(imageSrc);
});

let cropper;
document.getElementById("file-input").addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
            openCropModal(event.target.result);
        };
        reader.readAsDataURL(file);
    }
});

function captureImage() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    const cameraPreview = document.getElementById('camera-preview'); // Modal chụp ảnh

    // Vẽ khung hình video lên canvas
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Lấy ảnh từ canvas
    const imageSrc = canvas.toDataURL('image/jpeg');

    // Ẩn modal chụp ảnh tạm thời
    cameraPreview.style.display = 'none';

    // Mở modal crop ảnh
    openCropModal(imageSrc);
}

function openCropModal(imageSrc) {
    const cropModal = document.getElementById("crop-modal");
    const imageElement = document.getElementById("image-to-crop");

    // Hủy cropper cũ nếu có
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }

    imageElement.src = imageSrc;

    cropModal.style.display = "block";  // Mở modal

    cropper = new Cropper(imageElement, {
        aspectRatio: 1,
        viewMode: 1,
    });
}

// Cắt ảnh và tải lên
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

// Đóng modal cắt ảnh
function closeCropModal() {
    const cropModal = document.getElementById("crop-modal");
    cropModal.style.display = "none";  // Ẩn modal khi đóng

    // Hủy cropper khi đóng modal
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
}

// Xóa ảnh
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
