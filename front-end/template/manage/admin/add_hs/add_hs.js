document.addEventListener('DOMContentLoaded', function () {
    const token = localStorage.getItem('access_token');

    // Kiểm tra token đăng nhập
    if (!token) {
        alert('Token không tồn tại! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../../auth/login.html';
        }, 3000);
        return;
    }

    // Xử lý sự kiện khi submit form thêm học sinh
    document.getElementById('add-student-form').addEventListener('submit', function (event) {
        event.preventDefault();

        // Lấy thông tin học sinh
        const ten_hs = document.getElementById('ten_hs').value;
        const gioitinh_hs = document.getElementById('gioitinh_hs').value;
        const ngaysinh_hs = document.getElementById('ngaysinh_hs').value;
        const taikhoan = document.getElementById('taikhoan_hs').value;
        const matkhau = document.getElementById('matkhau_hs').value;

        // Lấy thông tin phụ huynh
        const parentEntries = document.querySelectorAll('.parent-entry');
        const phu_huynh = [];

        parentEntries.forEach(entry => {
            const ten_ph = entry.querySelector('input[type="text"]').value;
            const quanhe = entry.querySelector('select:nth-of-type(1)').value; // Quan hệ
            const gioitinh_ph = entry.querySelector('select:nth-of-type(2)').value; // Giới tính phụ huynh

            // Thêm thông tin phụ huynh vào mảng phu_huynh
            phu_huynh.push({ten_ph, quanhe, gioitinh_ph});
        });

        // Gửi dữ liệu lên API
        fetch('http://localhost:8000/admin/students', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ten_hs,
                gioitinh_hs,
                ngaysinh_hs,
                taikhoan,  // Tài khoản
                matkhau,   // Mật khẩu
                phu_huynh  // Thông tin phụ huynh
            })
        })
            .then(response => {
                if (response.ok) {
                    alert('Thêm học sinh thành công!');
                    window.location.href = '../ql_hocsinh.html'; // Chuyển hướng đến trang quản lý học sinh
                } else {
                    return response.json().then(data => {
                        throw new Error(data.detail || 'Có lỗi xảy ra khi thêm học sinh.');
                    });
                }
            })
            .catch(error => {
                console.error('Lỗi khi thêm học sinh:', error);
                alert(error.message);
            });
    });

    // Xử lý thêm phụ huynh khi nhấn nút "Thêm Phụ Huynh"
    document.getElementById('btn-add-parent').addEventListener('click', function () {
        const parentContainer = document.getElementById('parent-container');

        // Tạo một div mới cho thông tin phụ huynh
        const newParentEntry = document.createElement('div');
        newParentEntry.classList.add('parent-entry');
        newParentEntry.innerHTML = `
            <input type="text" placeholder="Tên Phụ Huynh" required>
            <select required>
                <option value="">Chọn Quan Hệ</option>
                <option value="Cha">Cha</option>
                <option value="Mẹ">Mẹ</option>
                <option value="Người Giám Hộ">Người Giám Hộ</option>
            </select>
            <select required>
                <option value="">Chọn Giới Tính</option>
                <option value="Nam">Nam</option>
                <option value="Nữ">Nữ</option>
            </select>
            <button type="button" class="btn-remove-parent">Xóa</button>
        `;

        // Thêm div mới vào container phụ huynh
        parentContainer.appendChild(newParentEntry);

        // Thêm sự kiện xóa cho nút "Xóa"
        newParentEntry.querySelector('.btn-remove-parent').addEventListener('click', function () {
            parentContainer.removeChild(newParentEntry);
        });
    });
});
