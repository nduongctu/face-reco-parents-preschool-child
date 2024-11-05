document.addEventListener('DOMContentLoaded', async function () {
    const token = localStorage.getItem('access_token');
    const detectionSlider = document.getElementById('detection-threshold');
    const detectionValue = document.getElementById('detection-value');
    const matchSlider = document.getElementById('match-threshold');
    const matchValue = document.getElementById('match-value');
    const video = document.getElementById('video');
    const today = new Date();
    const options = {year: 'numeric', month: '2-digit', day: '2-digit'};
    const formattedDate = today.toLocaleDateString('vi-VN', options).split('/').reverse().join('-');
    const canvas = document.getElementById('overlay');
    const context = canvas.getContext('2d'); // Lấy context 2D từ canvas

    document.getElementById('date-picker').value = formattedDate; // Đặt giá trị cho ô chọn ngày

    let id_lh;
    let students = [];

    // Cập nhật giá trị thanh trượt
    detectionSlider.addEventListener('input', () => {
        detectionValue.textContent = detectionSlider.value;
    });

    matchSlider.addEventListener('input', () => {
        matchValue.textContent = matchSlider.value;
    });


    // Kiểm tra token
    if (!token) {
        alert('Token không tồn tại! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../auth/login.html';
        }, 3000);
        return;
    }

    // Lấy quyền người dùng và ID giáo viên
    const user = await fetchUserRole(token);
    if (!user || user.quyen !== 1) {
        alert('Không có quyền truy cập! Vui lòng đăng nhập lại.');
        setTimeout(() => {
            window.location.href = '../../auth/login.html';
        }, 3000);
        return;
    }

    // Gọi API để lấy thông tin giáo viên, bao gồm id_lh
    const teacherApiUrl = `http://localhost:8000/admin/teachers/${user.id_gv}`;
    const teacherData = await fetchTeacherData(teacherApiUrl);
    if (teacherData) {
        id_lh = teacherData.id_lh; // Lưu id_lh từ dữ liệu giáo viên
        const className = teacherData.lop_hoc_ten; // Lấy tên lớp học từ dữ liệu giáo viên
        document.querySelector('.student-list-section h2').textContent = `Danh Sách ${className}`;

    }

    // Gọi API để lấy danh sách học sinh trong lớp
    const studentsApiUrl = `http://localhost:8000/admin/students_gv/${user.id_gv}`;
    students = await fetchAndDisplayStudents(studentsApiUrl);
    const id_hs_list = await fetchIdHsList(studentsApiUrl);
    console.log("Danh sách ID học sinh:", id_hs_list);

    // Gọi API để lấy danh sách học sinh có mặt cho ngày hôm nay
    const studentsPresentToday = await fetchStudentsByDate(id_lh, formattedDate);
    displayStudentsPresent(studentsPresentToday); // Hiển thị danh sách học sinh có mặt

    // Xử lý sự kiện chọn ngày
    const datePicker = document.getElementById('date-picker');
    datePicker.addEventListener('change', async function () {
        const selectedDate = datePicker.value;
        if (id_lh) { // Kiểm tra xem ID lớp đã được xác định chưa
            const studentsByDate = await fetchStudentsByDate(id_lh, selectedDate);
            displayStudentsPresent(studentsByDate); // Hiển thị danh sách học sinh theo ngày đã chọn
        } else {
            alert('ID lớp không hợp lệ. Vui lòng kiểm tra lại.');
        }
    });

    // Xử lý sự kiện tìm kiếm học sinh
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', function () {
        const query = searchInput.value;
        filterStudents(query); // Gọi hàm filterStudents để lọc danh sách học sinh
    });

    // Xử lý sự kiện tìm kiếm học sinh có mặt
    const searchAttendanceInput = document.getElementById('search-attendance-input');
    searchAttendanceInput.addEventListener('input', function () {
        const query = searchAttendanceInput.value;
        filterStudents_day(query);
    });

    // Tải mô hình phát hiện khuôn mặt
    try {
        await faceapi.nets.ssdMobilenetv1.loadFromUri('/virtual-learning-advisor/front-end/template/manage/giaovien/models');
    } catch (error) {
        console.error('Lỗi khi tải mô hình:', error);
        alert('Không thể tải mô hình nhận diện khuôn mặt. Vui lòng kiểm tra và thử lại.');
        return;
    }

    // Hàm phát hiện khuôn mặt
    async function detectFace() {
        const options = new faceapi.SsdMobilenetv1Options({
            minConfidence: parseFloat(detectionSlider.value) // Ngưỡng tin cậy từ thanh trượt
        });

        const detection = await faceapi.detectSingleFace(video, options); // Phát hiện một khuôn mặt duy nhất

        // Vẽ hộp bao quanh khuôn mặt
        context.clearRect(0, 0, canvas.width, canvas.height); // Xóa canvas trước khi vẽ
        faceapi.draw.drawDetections(canvas, detection ? [detection] : []); // Vẽ hộp bao quanh khuôn mặt

        // Nếu phát hiện khuôn mặt và đạt ngưỡng tin cậy
        if (detection) {
            // Chụp frame từ video
            const frame = document.createElement('canvas'); // Tạo một canvas tạm
            frame.width = video.videoWidth;
            frame.height = video.videoHeight;
            const frameContext = frame.getContext('2d');
            frameContext.drawImage(video, 0, 0, frame.width, frame.height); // Vẽ khung hình gốc từ video

            const base64Image = frame.toDataURL('image/jpeg').split(',')[1]; // Chuyển đổi frame sang base64 từ canvas tạm

            // Lấy danh sách ID học sinh
            const id_hs_list = await fetchIdHsList(studentsApiUrl);

            // Tạo payload
            const payload = {
                frame: {
                    frame: `data:image/jpeg;base64,${base64Image}`
                },
                id_hs_list: id_hs_list
            };

            // Gửi dữ liệu đến API
            await sendFrameToApi(payload);
        }

        requestAnimationFrame(detectFace); // Gọi lại hàm phát hiện khuôn mặt
    }

    video.addEventListener('play', () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        detectFace(); // Bắt đầu phát hiện khuôn mặt
    });


// Hàm gửi dữ liệu đến API
    async function sendFrameToApi(payload) {
        const euclidThreshold = matchSlider.value; // Lấy giá trị từ matchSlider
        const apiUrl = `http://localhost:8000/admin/recognize?euclid_threshold=${euclidThreshold}`; // Thêm tham số vào URL

        try {
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const result = await response.json();

                if (result.success) {
                    alert(result.message); // Thông báo thành công
                    const ngay = today.toLocaleDateString('vi-VN', options).split('/').reverse().join('-');

                    // Tải lại danh sách học sinh đã đến lớp
                    const students = await fetchStudentsByDate(id_lh, ngay);
                    updateRecognitionResults(students); // Cập nhật lại danh sách học sinh có mặt

                } else {
                    alert("Nhận dạng thất bại! Không có phụ huynh nào được tìm thấy.");
                }
            } else {
                const errorResponse = await response.json();
                if (errorResponse.detail) {
                    alert(errorResponse.detail);
                } else {
                    alert("Có lỗi xảy ra khi gửi dữ liệu đến API.");
                }
            }
        } catch (error) {
            console.error("Lỗi:", error);
            alert("Lỗi hệ thống, vui lòng thử lại sau.");
        }
    }

    async function fetchUserRole(token) {
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
                return null;
            }

            const data = await response.json();
            return {quyen: data.quyen, id_gv: data.id_gv};
        } catch (error) {
            console.error('Error fetching user info:', error);
            alert('Có lỗi xảy ra! Vui lòng đăng nhập lại.');
            setTimeout(() => {
                window.location.href = '../../auth/login.html';
            }, 3000);
        }
    }

    async function fetchTeacherData(apiUrl) {
        try {
            const response = await fetch(apiUrl, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}` // Thêm token vào header
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                alert(errorData.detail || 'Không thể lấy thông tin giáo viên.');
                return null;
            }

            return await response.json(); // Trả về dữ liệu giáo viên
        } catch (error) {
            console.error('Lỗi khi lấy thông tin giáo viên:', error);
            return null; // Trả về null nếu có lỗi
        }
    }

    async function fetchAndDisplayStudents(apiUrl) {
        try {
            const response = await fetch(apiUrl);
            const studentsData = await response.json();
            const studentListTable = document.getElementById('student-list');
            studentListTable.innerHTML = ''; // Xóa danh sách trước khi thêm mới

            studentsData.forEach(student => {
                if (student.ten_hs && student.gioitinh_hs && student.id_hs) {
                    const studentRow = createStudentRow(student);
                    studentListTable.appendChild(studentRow);
                } else {
                    console.warn(`Học sinh không hợp lệ: ${JSON.stringify(student)}`);
                }
            });

            return studentsData; // Trả về danh sách học sinh
        } catch (error) {
            console.error('Lỗi khi lấy dữ liệu:', error);
            return []; // Trả về mảng rỗng nếu có lỗi
        }
    }

    function createStudentRow(student) {
        const studentRow = document.createElement('tr');
        studentRow.classList.add('student-item');

        studentRow.innerHTML = `
        <td>${student.ten_hs}</td>
        <td>${student.gioitinh_hs}</td>
        <td>
            <button class="btn-confirm" data-id="${student.id_hs}"> 
                <img src="../../images/correct.png" alt="Tick_Icon">
            </button>
        </td>
    `;

        studentRow.querySelector('.btn-confirm').addEventListener('click', async function () {
            const idHs = student.id_hs; // Lấy ID học sinh
            const idLh = id_lh;
            const ngay = today.toLocaleDateString('vi-VN', options).split('/').reverse().join('-');
            const gioVao = new Date().toTimeString().split(' ')[0]; // Lấy giờ ở định dạng hh:mm:ss

            // Tạo payload
            const payload = {
                id_hs: idHs,
                id_lh: idLh,
                ngay: ngay,
                gio_vao: gioVao
            };

            // Gửi dữ liệu về server
            try {
                const response = await fetch('http://localhost:8000/admin/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload) // Chuyển đổi payload thành chuỗi JSON
                });

                // Kiểm tra phản hồi từ server
                if (response.ok) {
                    const data = await response.json(); // Xử lý phản hồi từ server
                    alert(`Đã xác nhận học sinh ID: ${idHs} đã đến lớp.`);

                    // Tải lại danh sách học sinh đã đến lớp
                    const students = await fetchStudentsByDate(idLh, ngay);
                    console.log("Danh sách học sinh đã lấy:", students);
                    updateRecognitionResults(students); // Cập nhật lại danh sách học sinh có mặt
                } else {
                    const errorData = await response.json(); // Nếu phản hồi không thành công, lấy thông tin lỗi
                    alert(`Có lỗi xảy ra: ${errorData.message || 'Không thể xác nhận.'}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Có lỗi xảy ra khi gửi dữ liệu!');
            }
        });

        return studentRow;
    }


    async function fetchStudentsByDate(id_lh, date) {
        const apiUrl = `http://localhost:8000/admin/diem-danh?id_lh=${id_lh}&ngay=${date}`;
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                console.error('Không thể lấy dữ liệu học sinh có mặt');
                return []; // Trả về mảng rỗng nếu có lỗi
            }
            const data = await response.json();

            // Kiểm tra xem danh sách học sinh có mặt có rỗng hay không
            if (!data.data || data.data.length === 0) {
                console.warn('Không tìm thấy học sinh nào có mặt.');
                return []; // Trả về mảng rỗng nếu không có học sinh nào
            }

            return data.data; // Trả về danh sách học sinh có mặt
        } catch (error) {
            console.error('Lỗi khi lấy danh sách học sinh có mặt:', error);
            alert('Đã xảy ra lỗi khi lấy danh sách học sinh. Vui lòng thử lại sau.');
            return []; // Trả về mảng rỗng nếu có lỗi
        }
    }

    function updateRecognitionResults(students) {
        const recognitionResultsBody = document.querySelector('#recognition-results');
        recognitionResultsBody.innerHTML = ''; // Xóa nội dung cũ

        // Kiểm tra nếu danh sách học sinh có rỗng
        if (students.length === 0) {
            recognitionResultsBody.innerHTML = `<tr><td colspan="5">Không có học sinh nào có mặt.</td></tr>`;
            return;
        }

        // Duyệt qua từng học sinh và tạo hàng trong bảng
        students.forEach(student => {
            const row = document.createElement('tr');
            row.innerHTML = `
            <td>${student.ho_ten_hoc_sinh ?? 'Chưa xác định'}</td>
            <td>${student.gio_vao ?? 'Chưa xác định'}</td>
            <td>${student.gio_ra ?? 'Chưa xác định'}</td>
            <td>${student.ten_phu_huynh ?? 'Chưa có'}</td>
            <td>${student.quan_he ?? 'Không xác định'}</td>
        `;
            recognitionResultsBody.appendChild(row);
        });
    }

    // Hàm để hiển thị danh sách học sinh có mặt
    function displayStudentsPresent(students) {
        const studentList = document.getElementById('recognition-results');
        studentList.innerHTML = ''; // Xóa danh sách hiện tại

        if (students.length === 0) {
            // Kiểm tra xem đã có thông báo chưa
            const noDataRow = document.createElement('tr');
            const noDataCell = document.createElement('td');
            noDataCell.colSpan = 5; // Chiếm toàn bộ cột
            noDataCell.textContent = 'Không tìm thấy học sinh nào!';
            noDataRow.appendChild(noDataCell);

            // Thêm hàng thông báo vào bảng chỉ nếu không có hàng nào trước đó
            studentList.appendChild(noDataRow);
        } else {
            students.forEach(student => {
                const studentRow = document.createElement('tr');

                const nameCell = document.createElement('td');
                const checkInCell = document.createElement('td');
                const checkOutCell = document.createElement('td');
                const parentNameCell = document.createElement('td');
                const relationshipCell = document.createElement('td');

                // Lấy giá trị từ thuộc tính mới
                nameCell.textContent = student.ho_ten_hoc_sinh; // Hiển thị tên học sinh
                checkInCell.textContent = student.gio_vao; // Hiển thị giờ vào
                checkOutCell.textContent = student.gio_ra; // Hiển thị giờ ra
                parentNameCell.textContent = student.ten_phu_huynh; // Hiển thị tên phụ huynh
                relationshipCell.textContent = student.quan_he; // Hiển thị quan hệ

                studentRow.appendChild(nameCell);
                studentRow.appendChild(checkInCell);
                studentRow.appendChild(checkOutCell);
                studentRow.appendChild(parentNameCell);
                studentRow.appendChild(relationshipCell);
                studentList.appendChild(studentRow);
            });
        }
    }

    function filterStudents_day(query) {
        const studentList = document.getElementById('recognition-results');
        const rows = studentList.getElementsByTagName('tr');

        let found = false; // Biến để theo dõi xem có học sinh nào khớp hay không

        // Xóa thông báo không tìm thấy nếu nó tồn tại
        const existingNoDataRow = studentList.querySelector('.no-data');
        if (existingNoDataRow) {
            existingNoDataRow.remove();
        }

        Array.from(rows).forEach(row => {
            const cells = row.getElementsByTagName('td');
            if (cells.length > 0) { // Kiểm tra xem hàng có dữ liệu không
                const name = cells[0].textContent.toLowerCase(); // Giả sử tên học sinh ở cột đầu tiên

                if (name.includes(query.toLowerCase())) {
                    row.style.display = ''; // Hiển thị hàng nếu trùng khớp
                    found = true; // Đánh dấu là tìm thấy ít nhất một học sinh
                } else {
                    row.style.display = 'none'; // Ẩn hàng nếu không trùng khớp
                }
            }
        });

        // Nếu không tìm thấy học sinh nào, hiển thị thông báo
        if (!found) {
            const noDataRow = document.createElement('tr');
            noDataRow.classList.add('no-data');
            const noDataCell = document.createElement('td');
            noDataCell.colSpan = 5;
            noDataCell.textContent = 'Không tìm thấy học sinh nào!'; // Thông báo không tìm thấy
            noDataRow.appendChild(noDataCell);
            studentList.appendChild(noDataRow);
        }
    }


    // Hàm để lọc học sinh theo tên hoặc ID
    function filterStudents(query) {
        const studentList = document.getElementById('student-list');
        const rows = studentList.getElementsByTagName('tr');
        let found = false; // Biến để theo dõi xem có học sinh nào khớp hay không

        // Xóa tất cả hàng thông báo trước đó nếu có
        const existingNoDataRow = studentList.querySelector('tr.no-data');
        if (existingNoDataRow) {
            studentList.removeChild(existingNoDataRow);
        }

        Array.from(rows).forEach(row => {
            const cells = row.getElementsByTagName('td');
            if (cells.length > 0) { // Kiểm tra xem hàng có dữ liệu không
                const id = cells[0].textContent.toLowerCase();
                const name = cells[1].textContent.toLowerCase();

                if (id.includes(query.toLowerCase()) || name.includes(query.toLowerCase())) {
                    row.style.display = ''; // Hiển thị hàng nếu trùng khớp
                    found = true;
                } else {
                    row.style.display = 'none'; // Ẩn hàng nếu không trùng khớp
                }
            }
        });

        // Nếu không tìm thấy học sinh nào, hiển thị thông báo
        if (!found) {
            const noDataRow = document.createElement('tr');
            noDataRow.classList.add('no-data');
            const noDataCell = document.createElement('td');
            noDataCell.colSpan = 3;
            noDataCell.textContent = 'Không tìm thấy học sinh nào!'; // Thông báo không tìm thấy
            noDataRow.appendChild(noDataCell);
            studentList.appendChild(noDataRow);
        }
    }

    async function fetchIdHsList(apiUrl) {
        try {
            const response = await fetch(apiUrl);
            const studentsData = await response.json();

            // Khởi tạo danh sách ID học sinh
            const id_hs_list = [];

            // Lặp qua từng học sinh và lấy ID
            studentsData.forEach(student => {
                if (student.id_hs) {
                    id_hs_list.push(student.id_hs);
                } else {
                    console.warn(`Học sinh không hợp lệ: ${JSON.stringify(student)}`);
                }
            });

            return id_hs_list; // Trả về danh sách ID học sinh
        } catch (error) {
            console.error('Lỗi khi lấy danh sách ID học sinh:', error);
            return []; // Trả về mảng rỗng nếu có lỗi
        }
    }

});
