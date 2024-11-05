document.addEventListener('DOMContentLoaded', async () => {
    const video = document.getElementById('video');

    // Mở camera
    async function startCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({video: true});
            video.srcObject = stream;
        } catch (error) {
            console.error("Không thể mở camera:", error);
            alert("Không thể mở camera. Vui lòng kiểm tra quyền truy cập và thiết bị camera.");
        }
    }

    // Bắt đầu camera ngay khi trang tải
    await startCamera();

    // Xử lý khi camera sẵn sàng
    video.addEventListener('loadedmetadata', () => {
        console.log("Camera đã sẵn sàng!");
    });
});
