CHƯƠNG 1: TỔNG QUAN HỆ THỐNG
1.1 Giới thiệu hệ thống

Hệ thống Sakura Learning System là một hệ thống web quản lý và theo dõi quá trình học tập, được xây dựng với mục tiêu hỗ trợ Admin tạo khóa học, bài học và các nhiệm vụ (mission), đồng thời cho phép User tham gia học tập, thực hiện nhiệm vụ và theo dõi tiến độ cá nhân.

Hệ thống được thiết kế với giao diện chủ đạo màu hồng Sakura, mang phong cách nhẹ nhàng, thân thiện, tạo cảm giác thoải mái và tạo động lực học tập cho người dùng.

1.2 Mục tiêu hệ thống

Hệ thống được xây dựng nhằm:

Quản lý khóa học và nội dung học tập tập trung

Phân quyền rõ ràng giữa Admin và User

Theo dõi tiến độ học tập của từng người dùng

Tạo động lực thông qua hệ thống mission và bảng xếp hạng

Hỗ trợ lưu trữ dữ liệu đa ngôn ngữ và emoji

CHƯƠNG 2: KIẾN TRÚC HỆ THỐNG
2.1 Công nghệ sử dụng

Hệ thống được xây dựng với các công nghệ sau:

Backend: Flask (Python)

Frontend: Flask Template (Jinja2) kết hợp Bootstrap

Database: MySQL (charset utf8mb4)

Kiến trúc: MVC nhiều tầng kết hợp Service và Repository Pattern

2.2 Kiến trúc tổng thể

Hệ thống được xây dựng theo mô hình nhiều tầng nhằm đảm bảo tính mở rộng và dễ bảo trì.

Luồng xử lý:

Controller → Service → Repository → Model → Database

Trong đó:

Controller: tiếp nhận request và trả về response

Service: xử lý nghiệp vụ

Repository: truy cập và thao tác dữ liệu

Model: định nghĩa thực thể và cấu trúc bảng trong database

CHƯƠNG 3: PHÂN QUYỀN HỆ THỐNG

Hệ thống sử dụng cơ chế phân quyền dựa trên trường role trong bảng User.

Có hai loại người dùng:

ADMIN

USER

Việc phân quyền được kiểm tra tại tầng Controller trước khi xử lý request.

CHƯƠNG 4: CHỨC NĂNG HỆ THỐNG
4.1 Chức năng dành cho ADMIN
4.1.1 Đăng nhập / Đăng xuất

Admin đăng nhập bằng tài khoản được cấp.

Hệ thống xác thực thông tin và tạo session.

Đăng xuất sẽ xóa session và quay về trang đăng nhập.

4.1.2 Quản lý người dùng

Admin có thể:

Xem danh sách tất cả người dùng

Xem tình trạng học tập của từng người

Theo dõi số mission đã hoàn thành

Theo dõi số task đã hoàn thành

Xem tiến độ tổng thể của từng user

4.1.3 Quản lý khóa học

Admin có thể:

Tạo khóa học mới

Chỉnh sửa thông tin khóa học

Xóa hoặc ẩn khóa học


4.1.4 Quản lý bài học

Mỗi khóa học có nhiều bài học.

Admin có thể:

Tạo bài học mới

Chỉnh sửa nội dung bài học

Gắn link tài liệu (PDF, Google Drive, YouTube…)

Người dùng chỉ cần nhấn vào link để truy cập tài liệu.

4.1.5 Quản lý Mission

Mission là một tập hợp các nhiệm vụ được giao cho người học.

Admin có thể:

Tạo mission

Chọn giao cho toàn bộ người dùng (tag ALL)

Hoặc giao cho người dùng cụ thể

4.1.6 Quản lý Task

Mỗi mission bao gồm nhiều task.

Admin có thể:

Tạo task

Liên kết task với bài học cụ thể

Mô tả yêu cầu của task

4.1.7 Thống kê hệ thống

Admin có thể xem:

Tổng số user

Tổng số khóa học

Tổng số mission

Bảng xếp hạng người học

Tình trạng hoàn thành nhiệm vụ

4.2 Chức năng dành cho USER
4.2.1 Đăng nhập / Đăng xuất

User đăng nhập vào hệ thống

Hệ thống xác thực và tạo session

4.2.2 Quản lý hồ sơ cá nhân

User có thể:

Xem thông tin cá nhân

Cập nhật tên, ảnh đại diện

Cập nhật bio (hỗ trợ emoji)

Chọn ngôn ngữ hiển thị

4.2.3 Xem khóa học

User có thể:

Xem danh sách khóa học

Truy cập vào từng khóa học

Xem danh sách bài học

Nhấn vào bài học để xem nội dung và tài liệu

4.2.4 Thực hiện Mission

User có thể:

Xem danh sách mission được giao

Xem danh sách task trong mission

Đánh dấu hoàn thành task/ bỏ đanh dấu hoàn thành task

Theo dõi phần trăm hoàn thành

4.2.5 Xem bảng xếp hạng

Hệ thống hiển thị bảng xếp hạng dựa trên:

Số mission hoàn thành

Số task hoàn thành

Tỷ lệ tiến độ

Mục tiêu là tạo động lực cạnh tranh lành mạnh giữa các người học.