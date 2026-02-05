from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"  
    # Kế thừa model sale.order gốc của Odoo
    # → Mở rộng logic phê duyệt cho đơn bán hàng

    approval_state = fields.Selection(
        [
            ("none", "No Approval"),        # Chưa cần phê duyệt
            ("pending", "Pending Approval"),# Đang chờ phê duyệt
            ("approved", "Approved"),       # Đã được phê duyệt
            ("rejected", "Rejected"),       # Bị từ chối
        ],
        default="none",  
        # Trạng thái phê duyệt ban đầu của sale order
        tracking=True,  
        # Bật tracking để ghi nhận thay đổi trạng thái vào chatter
    )

    current_approval_level = fields.Integer(
        default=0,
        # Cấp phê duyệt hiện tại mà đơn hàng đang ở
        # Ví dụ: 0 = chưa ai duyệt, 1 = level 1 đã duyệt, ...
        tracking=True,  
        # Theo dõi thay đổi level trong lịch sử chatter
    )

    required_approval_levels = fields.Integer(
        string="Required Approval Levels",
        compute="_compute_required_approval_levels",
        store=True,
        # Tổng số cấp phê duyệt mà đơn hàng này yêu cầu
        # Giá trị được tính động dựa trên rule / policy (compute)
        # store=True để lưu vào database → dùng được trong search, filter
    )

    approval_history_ids = fields.One2many(
        "sale.order.approval",
        "order_id",
        string="Approval History",
        # Quan hệ 1-nhiều tới bảng lịch sử phê duyệt
        # Lưu lại: ai duyệt, duyệt lúc nào, level nào, kết quả ra sao
    )

    def _compute_required_approval_levels(self):
        # Hàm compute xác định số cấp phê duyệt cần thiết cho từng đơn hàng
        for order in self:
            order.required_approval_levels = 0
            # Hiện tại set cứng = 0 (chưa có rule)
            # Thực tế thường sẽ:
            # - Dựa trên tổng tiền đơn hàng
            # - Dựa trên company / department
            # - Dựa trên chính sách phê duyệt nhiều cấp


    # 🔵 Submit
    def action_submit_approval(self):
        for order in self:
            order.approval_state = "pending"

    # 🟢 Approve
    def action_approve(self):
        for order in self:
            order.approval_state = "approved"

    # 🔴 Reject
    def action_reject(self):
        for order in self:
            order.approval_state = "rejected"

