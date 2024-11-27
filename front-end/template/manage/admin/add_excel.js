function convertExcelDateToISO(excelDate) {
    if (excelDate === null || excelDate === undefined) {
        return '';
    }
    const date = new Date((excelDate - 25569) * 86400 * 1000);
    return date.toISOString().split('T')[0];
}

let studentCount = 1;

const token = localStorage.getItem('access_token');

if (!token) {
    alert('Token không tồn tại! Vui lòng đăng nhập lại.');
    setTimeout(() => {
        window.location.href = '../../../auth/login.html';
    }, 3000);
}

document.getElementById('upload-excel-btn').addEventListener('click', function () {
    const fileInput = document.getElementById('upload-excel-input');
    fileInput.click(); // Mở hộp thoại chọn file
});

document.getElementById('upload-excel-input').addEventListener('change', function () {
    const file = this.files[0]; // Lấy file được chọn

    if (!file) {
        alert('Vui lòng chọn một file Excel để tải lên.');
        return;
    }

    const reader = new FileReader();

    reader.onload = function (e) {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, {type: 'array'});

        const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
        const jsonData = XLSX.utils.sheet_to_json(firstSheet, {header: 1});

        // Bỏ qua hàng tiêu đề
        const students = jsonData.slice(1).map(row => {
            if (row.length < 7) {
                console.warn(`Dòng không đủ thông tin: ${row}`);
                return null;
            }

            const ten_hs = `${row[0] || ''} ${row[1] || ''}`.trim(); // Ghép họ và tên
            const gioitinh_hs = row[2] || '';
            const ngaysinh_hs = convertExcelDateToISO(row[3]); // Chuyển đổi ngày sinh

            const taikhoan = createUsername(row[1], studentCount);
            const matkhau = '123';

            const phu_huynh = [{
                ten_ph: (row[4] || '').trim(), // Loại bỏ khoảng trắng
                quanhe: row[5] || '',
                gioitinh_ph: row[6] || ''
            }];

            studentCount++;
            return {ten_hs, gioitinh_hs, ngaysinh_hs, taikhoan, matkhau, phu_huynh};
        }).filter(student => student !== null); // Loại bỏ các dòng không hợp lệ

        // Biến để theo dõi số lượng thành công và lưu trữ lỗi
        let successCount = 0;
        const errorMessages = [];

        // Gửi từng học sinh đến server
        const promises = students.map(student => {
            return addStudentToDatabase(student, token)
                .then(() => {
                    successCount++; // Tăng số lượng thành công
                })
                .catch(error => {
                    errorMessages.push(`Lỗi khi thêm học sinh "${student.ten_hs}": ${error.message}`);
                });
        });

        // Sau khi tất cả các yêu cầu đã hoàn thành
        Promise.all(promises)
            .then(() => {
                if (successCount === students.length) {
                    alert('Tất cả học sinh đã được thêm thành công!');
                    location.reload(); // Làm mới trang sau khi thêm thành công
                } else {
                    alert(`Có ${errorMessages.length} lỗi xảy ra:\n${errorMessages.join('\n')}`);
                }
            });
    };

    reader.readAsArrayBuffer(file); // Đọc file dưới dạng ArrayBuffer
});

// Hàm tạo tên đăng nhập từ tên học sinh
function createUsername(name) {
    if (!name || typeof name !== 'string' || name.trim() === '') {
        console.warn(`Tên không hợp lệ: ${name}`);
        const randomNumber = Math.floor(1000 + Math.random() * 9000); // Tạo số ngẫu nhiên 4 chữ số
        return `user${randomNumber}`;
    }

    const sanitized = name.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    const username = sanitized.toLowerCase().replace(/\s+/g, '');
    const randomNumber = Math.floor(1000 + Math.random() * 9000);
    return `${username}${randomNumber}`;
}

// Hàm gửi dữ liệu học sinh lên server
function addStudentToDatabase(student, token) {
    return fetch('http://localhost:8000/admin/students', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(student)
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.detail || 'Có lỗi xảy ra khi thêm học sinh.');
                });
            }
        });
}
