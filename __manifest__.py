{
    "name": "Sales Multi-Level Approval Workflow",
    "summary": "Manage multi-level approval for quotations and sales orders",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "category": "Sales",
    "author": "BrianNguyen",
    "depends": ["sale", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "views/sale_approval_level_view.xml",
        "views/sale_approval_level_action.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False,
}
