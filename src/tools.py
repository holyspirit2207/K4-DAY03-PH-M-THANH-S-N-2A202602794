"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND — VINFAST HR ASSISTANT
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
Đề tài 2.1: Trợ lý Nhân sự VinFast — Tra cứu phép, bảo hiểm và tạo đơn nghỉ phép.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # ─────────────────────────────────────────────────────────────────────────
    # Tool 1: Tra cứu số ngày phép còn lại của nhân viên
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "check_leave_balance",
        "description": (
            "Tra cứu số ngày phép năm còn lại của nhân viên VinFast theo mã nhân viên. "
            "Trả về thông tin: tổng phép năm, đã nghỉ, còn lại và ngày phép sắp hết hạn."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Mã nhân viên cần tra cứu (ví dụ: 'NV001', 'NV002')"
                }
            },
            "required": ["employee_id"]
        }
    },

    # ─────────────────────────────────────────────────────────────────────────
    # Tool 2: Tra cứu chính sách bảo hiểm theo loại hợp đồng
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "get_insurance_policy",
        "description": (
            "Tra cứu chính sách bảo hiểm (BHYT, BHXH, BHTN) của VinFast theo loại hợp đồng lao động. "
            "Hỗ trợ các loại hợp đồng: 'full_time' (toàn thời gian), 'part_time' (bán thời gian), 'probation' (thử việc)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "contract_type": {
                    "type": "string",
                    "description": "Loại hợp đồng lao động: 'full_time', 'part_time', hoặc 'probation'",
                    "enum": ["full_time", "part_time", "probation"]
                }
            },
            "required": ["contract_type"]
        }
    },

    # ─────────────────────────────────────────────────────────────────────────
    # Tool 3: Tạo đơn xin nghỉ phép
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "submit_leave_request",
        "description": (
            "Tạo và gửi đơn xin nghỉ phép cho nhân viên VinFast. "
            "Hệ thống sẽ kiểm tra số ngày phép còn lại, tự động tính số ngày nghỉ và trả về mã đơn nghị phép."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Mã nhân viên xin nghỉ phép (ví dụ: 'NV001')"
                },
                "leave_type": {
                    "type": "string",
                    "description": "Loại nghỉ phép: 'annual' (phép năm), 'sick' (nghỉ bệnh), 'personal' (việc cá nhân), 'unpaid' (không lương)",
                    "enum": ["annual", "sick", "personal", "unpaid"]
                },
                "start_date": {
                    "type": "string",
                    "description": "Ngày bắt đầu nghỉ theo định dạng DD/MM/YYYY (ví dụ: '15/09/2026')"
                },
                "end_date": {
                    "type": "string",
                    "description": "Ngày kết thúc nghỉ theo định dạng DD/MM/YYYY (ví dụ: '17/09/2026')"
                },
                "reason": {
                    "type": "string",
                    "description": "Lý do xin nghỉ phép (ví dụ: 'Nghỉ phép du lịch gia đình')"
                }
            },
            "required": ["employee_id", "leave_type", "start_date", "end_date", "reason"]
        }
    }
]


# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

# --- Mock Database: Hồ sơ nhân viên VinFast ---
EMPLOYEE_DATABASE: Dict[str, Dict] = {
    "NV001": {
        "full_name": "Nguyễn Văn Hùng",
        "department": "Kỹ thuật Sản xuất",
        "position": "Kỹ sư Sản xuất Cấp 2",
        "contract_type": "full_time",
        "email": "hung.nv@vinfast.vn",
        "manager": "Trần Minh Khoa",
        "leave_balance": {
            "total_annual": 12,
            "used_annual": 3,
            "remaining_annual": 9,
            "sick_days_used": 1,
            "expiry_date": "31/12/2026"
        }
    },
    "NV002": {
        "full_name": "Trần Thị Lan",
        "department": "Kiểm định Chất lượng (QC)",
        "position": "Kỹ sư QC Cấp 1",
        "contract_type": "full_time",
        "email": "lan.tt@vinfast.vn",
        "manager": "Lê Quốc Bảo",
        "leave_balance": {
            "total_annual": 12,
            "used_annual": 7,
            "remaining_annual": 5,
            "sick_days_used": 0,
            "expiry_date": "31/12/2026"
        }
    },
    "NV003": {
        "full_name": "Phạm Đức Anh",
        "department": "Nhân sự & Hành chính",
        "position": "Chuyên viên Nhân sự",
        "contract_type": "full_time",
        "email": "anh.pd@vinfast.vn",
        "manager": "Nguyễn Thị Mai",
        "leave_balance": {
            "total_annual": 14,
            "used_annual": 0,
            "remaining_annual": 14,
            "sick_days_used": 2,
            "expiry_date": "31/12/2026"
        }
    },
    "NV004": {
        "full_name": "Lê Thị Hương",
        "department": "Chuỗi Cung ứng",
        "position": "Nhân viên thử việc - Logistics",
        "contract_type": "probation",
        "email": "huong.lt@vinfast.vn",
        "manager": "Võ Thanh Bình",
        "leave_balance": {
            "total_annual": 0,
            "used_annual": 0,
            "remaining_annual": 0,
            "sick_days_used": 0,
            "expiry_date": "N/A"
        }
    }
}

# --- Mock Database: Chính sách bảo hiểm theo loại hợp đồng ---
INSURANCE_POLICY_DATABASE: Dict[str, Dict] = {
    "full_time": {
        "contract_type_label": "Hợp đồng Toàn thời gian (Full-time)",
        "bhxh": {
            "label": "Bảo hiểm Xã hội (BHXH)",
            "employee_rate": "8%",
            "employer_rate": "17%",
            "note": "Tính trên mức lương đóng BHXH. Áp dụng từ tháng đầu tiên ký hợp đồng."
        },
        "bhyt": {
            "label": "Bảo hiểm Y tế (BHYT)",
            "employee_rate": "1.5%",
            "employer_rate": "3%",
            "note": "Thẻ BHYT cấp trong vòng 30 ngày. Hỗ trợ khám chữa bệnh tại bệnh viện tuyến 1."
        },
        "bhtn": {
            "label": "Bảo hiểm Thất nghiệp (BHTN)",
            "employee_rate": "1%",
            "employer_rate": "1%",
            "note": "Áp dụng cho hợp đồng từ 12 tháng trở lên."
        },
        "additional_benefits": "Bảo hiểm tai nạn 24/24 (VinFast tài trợ 100%), Khám sức khỏe định kỳ hàng năm."
    },
    "part_time": {
        "contract_type_label": "Hợp đồng Bán thời gian (Part-time)",
        "bhxh": {
            "label": "Bảo hiểm Xã hội (BHXH)",
            "employee_rate": "Không áp dụng",
            "employer_rate": "Không áp dụng",
            "note": "Hợp đồng bán thời gian không đủ điều kiện đóng BHXH bắt buộc."
        },
        "bhyt": {
            "label": "Bảo hiểm Y tế (BHYT)",
            "employee_rate": "1.5%",
            "employer_rate": "3%",
            "note": "BHYT vẫn được áp dụng nếu làm đủ điều kiện theo quy định."
        },
        "bhtn": {
            "label": "Bảo hiểm Thất nghiệp (BHTN)",
            "employee_rate": "Không áp dụng",
            "employer_rate": "Không áp dụng",
            "note": "Không đủ điều kiện BHTN cho hợp đồng bán thời gian."
        },
        "additional_benefits": "Hỗ trợ ăn trưa tại căng-tin VinFast."
    },
    "probation": {
        "contract_type_label": "Thử việc (Probation)",
        "bhxh": {
            "label": "Bảo hiểm Xã hội (BHXH)",
            "employee_rate": "Không áp dụng trong thời gian thử việc",
            "employer_rate": "Không áp dụng",
            "note": "BHXH sẽ được đóng đầy đủ ngay sau khi ký hợp đồng chính thức."
        },
        "bhyt": {
            "label": "Bảo hiểm Y tế (BHYT)",
            "employee_rate": "Không áp dụng trong thời gian thử việc",
            "employer_rate": "Không áp dụng",
            "note": "VinFast hỗ trợ mua BHYT tự nguyện trong thời gian thử việc nếu có yêu cầu."
        },
        "bhtn": {
            "label": "Bảo hiểm Thất nghiệp (BHTN)",
            "employee_rate": "Không áp dụng",
            "employer_rate": "Không áp dụng",
            "note": "Không áp dụng trong thời gian thử việc."
        },
        "additional_benefits": "Hỗ trợ ăn trưa tại căng-tin VinFast. Được tham gia các khóa đào tạo nội bộ."
    }
}


# --- Execution Functions ---

def execute_check_leave_balance(employee_id: str) -> str:
    """Tra cứu số ngày phép còn lại của nhân viên VinFast"""
    emp = EMPLOYEE_DATABASE.get(employee_id.strip().upper())
    if emp:
        lb = emp["leave_balance"]
        return json.dumps({
            "status": "SUCCESS",
            "employee_id": employee_id.upper(),
            "full_name": emp["full_name"],
            "department": emp["department"],
            "position": emp["position"],
            "contract_type": emp["contract_type"],
            "leave_balance": lb
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy nhân viên có mã '{employee_id}' trong hệ thống VinFast. Vui lòng kiểm tra lại mã nhân viên."
        }, ensure_ascii=False)


def execute_get_insurance_policy(contract_type: str) -> str:
    """Tra cứu chính sách bảo hiểm theo loại hợp đồng"""
    policy = INSURANCE_POLICY_DATABASE.get(contract_type.strip().lower())
    if policy:
        return json.dumps({
            "status": "SUCCESS",
            "contract_type": contract_type,
            "policy": policy
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Loại hợp đồng '{contract_type}' không hợp lệ. Các loại hợp đồng hỗ trợ: 'full_time', 'part_time', 'probation'."
        }, ensure_ascii=False)


def execute_submit_leave_request(
    employee_id: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str
) -> str:
    """Tạo và gửi đơn xin nghỉ phép cho nhân viên VinFast"""
    emp = EMPLOYEE_DATABASE.get(employee_id.strip().upper())
    if not emp:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy nhân viên '{employee_id}'. Không thể tạo đơn nghỉ phép."
        }, ensure_ascii=False)

    leave_type_labels = {
        "annual": "Phép năm",
        "sick": "Nghỉ bệnh",
        "personal": "Việc cá nhân",
        "unpaid": "Nghỉ không lương"
    }

    # Tính số ngày nghỉ (đơn giản hoá)
    try:
        fmt = "%d/%m/%Y"
        d1 = datetime.strptime(start_date.strip(), fmt)
        d2 = datetime.strptime(end_date.strip(), fmt)
        days_requested = max(1, (d2 - d1).days + 1)
    except ValueError:
        days_requested = 1

    lb = emp["leave_balance"]
    remaining = lb.get("remaining_annual", 0)

    # Kiểm tra số phép còn lại nếu là phép năm
    if leave_type == "annual" and days_requested > remaining:
        return json.dumps({
            "status": "INSUFFICIENT_LEAVE",
            "employee_id": employee_id.upper(),
            "full_name": emp["full_name"],
            "days_requested": days_requested,
            "remaining_annual": remaining,
            "message": (
                f"Không đủ ngày phép năm. Nhân viên {emp['full_name']} yêu cầu {days_requested} ngày "
                f"nhưng chỉ còn {remaining} ngày phép năm. "
                f"Vui lòng điều chỉnh thời gian nghỉ hoặc chuyển sang loại 'unpaid' (không lương)."
            )
        }, ensure_ascii=False)

    # Tạo mã đơn nghỉ phép
    request_id = f"LP-{employee_id.upper()}-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

    return json.dumps({
        "status": "SUCCESS",
        "request_id": request_id,
        "employee_id": employee_id.upper(),
        "full_name": emp["full_name"],
        "department": emp["department"],
        "manager": emp["manager"],
        "leave_type": leave_type,
        "leave_type_label": leave_type_labels.get(leave_type, leave_type),
        "start_date": start_date,
        "end_date": end_date,
        "days_requested": days_requested,
        "reason": reason,
        "submitted_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "message": (
            f"Đơn xin nghỉ phép đã được tạo thành công! Mã đơn: {request_id}. "
            f"Nhân viên {emp['full_name']} xin nghỉ {days_requested} ngày ({leave_type_labels.get(leave_type, leave_type)}) "
            f"từ {start_date} đến {end_date}. Đơn đã được gửi tới quản lý {emp['manager']} để phê duyệt."
        )
    }, ensure_ascii=False)


# ==============================================================================
# 3. TOOL ROUTER (Ánh xạ tên tool → hàm thực thi)
# ==============================================================================

TOOL_ROUTER = {
    "check_leave_balance": execute_check_leave_balance,
    "get_insurance_policy": execute_get_insurance_policy,
    "submit_leave_request": execute_submit_leave_request
}


def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool — gọi đúng hàm backend theo tên tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại trong hệ thống HR VinFast!"}, ensure_ascii=False)
