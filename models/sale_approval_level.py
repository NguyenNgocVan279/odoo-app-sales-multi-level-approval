from odoo import models, fields

class SaleApprovalLevel(models.Model):
    _name = "sale.approval.level"
    # Model cấu hình các cấp phê duyệt cho Sale Order
    # Dùng để map: giá trị đơn hàng → cấp phê duyệt → nhóm người duyệt

    _description = "Sales Approval Level"
    # Mô tả model, hiển thị trong chế độ developer

    _order = "level asc"
    # Sắp xếp các rule theo thứ tự level tăng dần
    # → đảm bảo luồng phê duyệt đi từ thấp đến cao

    name = fields.Char(required=True)
    # Tên mô tả của cấp phê duyệt
    # Ví dụ: "Level 1 - Team Lead", "Level 2 - Manager"

    level = fields.Integer(required=True)
    # Thứ tự cấp phê duyệt
    # level càng lớn → quyền phê duyệt càng cao

    amount_from = fields.Monetary(required=True)
    # Giá trị đơn hàng tối thiểu để áp dụng level này

    amount_to = fields.Monetary(required=True)
    # Giá trị đơn hàng tối đa để áp dụng level này
    # Kết hợp amount_from → amount_to để xác định rule phù hợp

    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        store=True,
        readonly=True,
        # Đồng tiền áp dụng cho rule phê duyệt
        # Lấy theo currency của company
        # store=True để dùng trong search / domain
    )

    group_id = fields.Many2one(
        "res.groups",
        string="Approver Group",
        required=True,
        # Nhóm người dùng có quyền phê duyệt ở level này
        # Tất cả user thuộc group này đều có thể approve / reject
    )

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
        # Company áp dụng rule phê duyệt
        # Hỗ trợ multi-company: mỗi công ty có rule riêng
    )

    active = fields.Boolean(default=True)
    # Cho phép bật / tắt rule phê duyệt
    # Không xóa record để tránh mất dữ liệu lịch sử
