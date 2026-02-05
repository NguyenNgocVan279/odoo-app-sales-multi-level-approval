from odoo import models, fields

class SaleOrderApproval(models.Model):
    _name = "sale.order.approval"
    # Model lưu lịch sử phê duyệt của Sale Order
    # Mỗi record tương ứng với 1 hành động phê duyệt (approve / reject)

    _description = "Sales Order Approval History"
    # Mô tả model hiển thị trong technical / developer mode

    _order = "action_date asc"
    # Sắp xếp lịch sử phê duyệt theo thời gian tăng dần
    # → Hiển thị đúng thứ tự các bước phê duyệt

    order_id = fields.Many2one(
        "sale.order",
        required=True,
        ondelete="cascade",
        # Liên kết tới Sale Order được phê duyệt
        # ondelete="cascade":
        #   nếu Sale Order bị xóa → toàn bộ lịch sử phê duyệt cũng bị xóa theo
    )

    level = fields.Integer(required=True)
    # Cấp phê duyệt của hành động này
    # Ví dụ:
    #   level = 1 → trưởng nhóm
    #   level = 2 → manager
    #   level = 3 → director

    user_id = fields.Many2one(
        "res.users",
        required=True,
        default=lambda self: self.env.user,
        # Người thực hiện hành động phê duyệt
        # Mặc định là user đang đăng nhập khi tạo record
    )

    action = fields.Selection(
        [
            ("approve", "Approved"),
            ("reject", "Rejected"),
        ],
        required=True,
        # Kết quả của hành động tại cấp phê duyệt này
        # approve → cho phép lên cấp tiếp theo
        # reject  → dừng luồng, đơn hàng bị từ chối
    )

    note = fields.Text()
    # Ghi chú của người phê duyệt
    # Ví dụ: lý do reject, yêu cầu chỉnh sửa, comment nghiệp vụ

    action_date = fields.Datetime(
        default=fields.Datetime.now,
        required=True,
        # Thời điểm thực hiện hành động phê duyệt
        # Dùng để audit, truy vết và hiển thị timeline
    )
