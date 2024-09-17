document.addEventListener('DOMContentLoaded', function () {
    const token = localStorage.getItem('access_token');

    if (!token) {
        alert('Token không tồn tại! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../../auth/login.html';
        }, 3000);
        return;
    }

    document.getElementById('add-teacher-form').addEventListener('submit', function (event) {
        event.preventDefault();

        const ten_gv = document.getElementById('ten_gv').value;
        const gioitinh_gv = document.getElementById('gioitinh_gv').value;
        const ngaysinh_gv = document.getElementById('ngaysinh_gv').value;
        const sdt_gv = document.getElementById('sdt_gv').value;
        const diachi_gv = document.getElementById('diachi_gv').value;

        const sdtError = document.getElementById('sdt_error');

        if (sdt_gv.length !== 10) {
            sdtError.style.display = 'block';
            return;
        } else {
            sdtError.style.display = 'none';
        }

        fetch('http://localhost:8000/admin/teachers', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ten_gv,
                gioitinh_gv,
                ngaysinh_gv,
                sdt_gv,
                diachi_gv
            })
        })
        .then(response => {
            if (response.ok) {
                alert('Thêm giáo viên thành công!');
                window.location.href = '../ql_giaovien.html';
            } else {
                return response.json().then(data => {
                    throw new Error(data.detail || 'Có lỗi xảy ra khi thêm giáo viên.');
                });
            }
        })
        .catch(error => {
            console.error('Lỗi khi thêm giáo viên:', error);
            alert(error.message);
        });
    });

    // Hàm hỗ trợ xử lý số điện thoại
    function formatPhoneNumber(inputElement, maxLength) {
        inputElement.addEventListener('input', function (e) {
            const input = e.target.value;
            e.target.value = input.replace(/[^0-9]/g, '');
            if (e.target.value.length > maxLength) {
                e.target.value = e.target.value.slice(0, maxLength);
            }
        });
    }

    // Áp dụng hàm hỗ trợ cho số điện thoại
    formatPhoneNumber(document.getElementById('sdt_gv'), 10);
});
