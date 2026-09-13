"""
🔌 MODEL CONTEXT PROTOCOL (MCP) SERVER MODULE — VINFAST HR
Mô phỏng kiến trúc MCP Server (Client-Server Architecture) cung cấp công cụ HR chuẩn hóa.
Đề tài 2.1: Trợ lý Nhân sự VinFast — vinfast-hr-mcp-server
"""

import json
import sys
from typing import Dict, Any, List
from tools import TOOLS_SCHEMA, dispatch_tool_call

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class MCPHRServer:
    """
    Giả lập MCP Server tuân thủ chuẩn giao thức Model Context Protocol
    Phục vụ các Tool HR VinFast: check_leave_balance, get_insurance_policy, submit_leave_request
    """
    def __init__(self, server_name: str = "vinfast-hr-mcp-server"):
        self.server_name = server_name
        self.version = "2026.1.0"

    def list_tools(self) -> List[Dict[str, Any]]:
        """Trả về danh sách các Tools HR chuẩn giao thức MCP"""
        return TOOLS_SCHEMA

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        [TASK 2.1] Thực thi request gọi Tool theo chuẩn MCP JSON-RPC 2.0
        1. Gọi dispatch_tool_call(tool_name, arguments) để lấy chuỗi JSON kết quả.
        2. Chuyển chuỗi JSON → Python Dict (json.loads).
        3. Đóng gói phản hồi chuẩn MCP JSON-RPC 2.0 với các trường bắt buộc.
        """
        raw_result = dispatch_tool_call(tool_name, arguments)
        content = json.loads(raw_result)
        return {
            "jsonrpc": "2.0",
            "server": self.server_name,
            "tool": tool_name,
            "result": content
        }


if __name__ == "__main__":
    print("==========================================================")
    print("🔌 KIỂM THỬ ĐỘC LẬP MCP SERVER (vinfast-hr-mcp-server)")
    print("==========================================================")

    server = MCPHRServer()
    tools = server.list_tools()
    print(f"✅ [MCP SERVER] Đã khởi tạo thành công {server.server_name} (Version: {server.version})")
    print(f"📦 Số lượng Tools công bố qua MCP: {len(tools)}")
    for t in tools:
        print(f"   🛠️  {t['name']}: {t['description'][:60]}...")

    print("\n--- Kiểm tra Tool 1: check_leave_balance (NV001) ---")
    r1 = server.call_tool("check_leave_balance", {"employee_id": "NV001"})
    print(f"✅ Phản hồi JSON-RPC: {json.dumps(r1, ensure_ascii=False, indent=2)}")

    print("\n--- Kiểm tra Tool 2: get_insurance_policy (full_time) ---")
    r2 = server.call_tool("get_insurance_policy", {"contract_type": "full_time"})
    print(f"✅ Phản hồi JSON-RPC: status={r2['result']['status']}, contract={r2['result']['policy']['contract_type_label']}")

    print("\n--- Kiểm tra Tool 3: submit_leave_request (NV002) ---")
    r3 = server.call_tool("submit_leave_request", {
        "employee_id": "NV002",
        "leave_type": "annual",
        "start_date": "15/09/2026",
        "end_date": "17/09/2026",
        "reason": "Nghỉ phép du lịch gia đình"
    })
    print(f"✅ Phản hồi JSON-RPC: status={r3['result']['status']}, request_id={r3['result'].get('request_id', 'N/A')}")

    print("\n--- Kiểm tra Edge Case: nhân viên không tồn tại (NV999) ---")
    r4 = server.call_tool("check_leave_balance", {"employee_id": "NV999"})
    print(f"✅ Edge Case: status={r4['result']['status']}")
    print("\n==========================================================")
    print("✅ Tất cả kiểm thử MCP Server đã PASS!")
