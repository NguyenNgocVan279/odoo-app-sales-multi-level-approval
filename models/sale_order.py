from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

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

    can_approve = fields.Boolean(
        compute="_compute_can_approve",
        store=False
    )

    approval_history_ids = fields.One2many(
        "sale.order.approval",
        "order_id",
        string="Approval History",
        # Quan hệ 1-nhiều tới bảng lịch sử phê duyệt
        # Lưu lại: ai duyệt, duyệt lúc nào, level nào, kết quả ra sao
    )


    @api.depends("amount_total", "company_id")
    def _compute_required_approval_levels(self):
        ApprovalLevel = self.env["sale.approval.level"]

        for order in self:
            order.required_approval_levels = 0

            if not order.amount_total:
                continue

            levels = ApprovalLevel.search([
                ("active", "=", True),
                ("company_id", "=", order.company_id.id),
                ("amount_from", "<=", order.amount_total),
                "|",
                ("amount_to", "=", 0),
                ("amount_to", ">=", order.amount_total),
            ])

            if levels:
                order.required_approval_levels = max(levels.mapped("level"))

            # _logger.info(
            #     "[APPROVAL DEBUG] Order %s | amount=%s | levels=%s | required=%s",
            #     order.name,
            #     order.amount_total,
            #     levels.mapped("level"),
            #     order.required_approval_levels,
            # )
            # # [APPROVAL DEBUG] Order SO023 | amount=15000000 | levels=[1, 2, 3] | required=3



    @api.depends(
        "approval_state",
        "current_approval_level",
        "company_id"
    )
    def _compute_can_approve(self):
        ApprovalLevel = self.env["sale.approval.level"]

        for order in self:
            order.can_approve = False

            if order.approval_state != "pending":
                continue

            level = ApprovalLevel.search([
                ("active", "=", True),
                ("company_id", "=", order.company_id.id),
                ("level", "=", order.current_approval_level),
            ], limit=1)

            if level and level.group_id in self.env.user.groups_id:
                order.can_approve = True



    def _check_user_can_approve(self):
        self.ensure_one()

        if self.approval_state != "pending":
            return False

        level = self.env["sale.approval.level"].search([
            ("active", "=", True),
            ("company_id", "=", self.company_id.id),
            ("level", "=", self.current_approval_level),
        ], limit=1)

        if not level:
            return False

        return level.group_id in self.env.user.groups_id


    # Action submit for approval
    def action_submit_approval(self):
        ApprovalLevel = self.env["sale.approval.level"]

        for order in self:
            if order.create_uid != self.env.user:
                raise UserError(_("Only the creator of this quotation can submit it."))

            if order.approval_state != "none":
                raise UserError(_("This quotation has already been submitted."))

            if order.required_approval_levels == 0:
                order.approval_state = "approved"
                order.current_approval_level = 0
                continue

            first_level = ApprovalLevel.search([
                ("active", "=", True),
                ("company_id", "=", order.company_id.id),
            ], order="level asc", limit=1)

            if not first_level:
                raise UserError(_("No approval level configured."))

            order.current_approval_level = first_level.level
            order.approval_state = "pending"

    # 🟢 Approve
    def action_approve(self):
        ApprovalLevel = self.env["sale.approval.level"]

        for order in self:
            if not order._check_user_can_approve():
                raise UserError(_("You are not allowed to approve this order."))

            self.env["sale.order.approval"].create({
                "order_id": order.id,
                "level": order.current_approval_level,
                "action": "approve",
            })

            next_level = ApprovalLevel.search([
                ("active", "=", True),
                ("company_id", "=", order.company_id.id),
                ("level", ">", order.current_approval_level),
            ], order="level asc", limit=1)

            if next_level and next_level.level <= order.required_approval_levels:
                order.current_approval_level = next_level.level
            else:
                order.approval_state = "approved"



    # 🔴 Reject
    def action_reject(self):
        for order in self:
            order.approval_state = "rejected"
    

    # ===================================
    # Only confirm the order when approval_status is "approved"
    # ===================================
    def action_confirm(self):
        for order in self:
            # Nếu đơn hàng có yêu cầu phê duyệt
            if order.required_approval_levels > 0:
                # Nhưng chưa được approved
                if order.approval_state != "approved":
                    raise UserError(_(
                        "This Sales Order must be approved before confirmation."
                    ))
                # Đã được approved nhưng không phải người tạo
                if order.create_uid != self.env.user:
                    raise UserError(_(
                        "Only the creator can confirm this Sales Order."
                    ))

        # Nếu tất cả đều hợp lệ → chạy logic confirm gốc của Odoo
        return super().action_confirm()
    

    
