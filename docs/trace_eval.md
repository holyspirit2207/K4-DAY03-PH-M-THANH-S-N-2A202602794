# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Phạm Thanh Sơn  
> **Mã Sinh Viên / Mã Học viên:** 2A202602794  
> **Chủ đề Lựa chọn:** Gợi ý 2.1 — Trợ lý Nhân sự VinFast (HR Assistant)

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Bài toán yêu cầu Agent suy luận nhiều bước liên tiếp: nhận diện intent từ câu hỏi tự nhiên → chọn đúng Tool trong 3 công cụ → trích xuất và truyền đúng tham số (TC04 cần 5 params: employee_id, leave_type, start_date, end_date, reason) → nhận Observation từ MCP Server → tổng hợp Final Answer. Chưa đạt 5/5 vì chưa có chain-tool tự động (tra cứu phép → nộp đơn liên tiếp trong 1 query). |
| **2. Tool Interaction** | 5 / 5 | Hệ thống kết nối trực tiếp MCP Server `vinfast-hr-mcp-server v2026.1.0` qua giao thức JSON-RPC 2.0. Triển khai đầy đủ 3 công cụ thực thi: `check_leave_balance` (tra cứu phép), `get_insurance_policy` (tra bảo hiểm), `submit_leave_request` (tạo đơn nghỉ phép). Mọi dữ liệu phản hồi đều từ Tool Execution Layer, không phụ thuộc hallucination LLM. |
| **3. Dynamic Decision** | 4 / 5 | Nội dung Final Answer thay đổi hoàn toàn theo Observation: Tool trả `SUCCESS` → tổng hợp chi tiết; trả `NOT_FOUND` (TC05: NV999) → phản hồi lịch sự không bịa dữ liệu; trả `INSUFFICIENT_LEAVE` → cảnh báo và gợi ý phương án "nghỉ không lương". Agent thực sự ra quyết định dựa trên dữ liệu quan sát được từ MCP Server. |
| **4. Long Horizon Goal** | 3 / 5 | Agent giữ mục tiêu trong phạm vi 1 query (tối đa 2 bước ReAct: Action → Observation → Final Answer). Chưa có memory liên phiên hoặc multi-turn goal tracking. Phù hợp bài toán HR tra cứu đơn lẻ; yêu cầu phức tạp hơn (theo dõi trạng thái đơn qua nhiều lượt) cần nâng cấp lên Cấp 4. |
| **TỔNG ĐIỂM AGENTIC FIT** | **16 / 20** | *Tổng 16/20 > 12/20: Bài toán HR VinFast rất phù hợp triển khai Agentic System. Tool Interaction đạt tối đa 5/5 — hệ thống xử lý đúng chuỗi Thought → Action → Observation → Final Answer qua MCP Server thực tế, đảm bảo Anti-Hallucination.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

**Provider đã dùng:** `GeminiProvider` · Model: `gemini-2.5-flash-latest` · MCP Server: `vinfast-hr-mcp-server v2026.1.0`  
**Kết quả:** Đã thực thi thành công **5/5 Test Cases** · Xuất **10 sự kiện** vào `docs/trace_waterfall.json`

Trích xuất 2 đoạn log tiêu biểu từ `docs/trace_waterfall.json` — **TC02: check_leave_balance** và **TC04: submit_leave_request**:

```json
[
  {
    "step": 1,
    "query": "Kiểm tra số ngày phép còn lại của nhân viên NV001.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "check_leave_balance",
    "arguments": { "employee_id": "NV001" },
    "observation": {
      "status": "SUCCESS",
      "employee_id": "NV001",
      "full_name": "Nguyễn Văn Hùng",
      "department": "Kỹ thuật Sản xuất",
      "leave_balance": {
        "total_annual": 12,
        "used_annual": 3,
        "remaining_annual": 9,
        "expiry_date": "31/12/2026"
      }
    },
    "latency_ms": 2094.62
  },
  {
    "step": 2,
    "query": "Kiểm tra số ngày phép còn lại của nhân viên NV001.",
    "action_type": "FINAL_ANSWER",
    "thought": "Tổng hợp kết quả từ MCP Server HR VinFast thành công.",
    "output": "✅ NV001 — Nguyễn Văn Hùng: Tổng phép 12 ngày, đã nghỉ 3 ngày, còn lại 9 ngày (hết hạn 31/12/2026).",
    "latency_ms": 10.0
  },
  {
    "step": 1,
    "query": "Tạo đơn xin nghỉ phép năm cho nhân viên NV002 từ ngày 20/09/2026 đến 22/09/2026, lý do nghỉ phép du lịch cùng gia đình.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "submit_leave_request",
    "arguments": {
      "employee_id": "NV002",
      "leave_type": "annual",
      "start_date": "20/09/2026",
      "end_date": "22/09/2026",
      "reason": "Nghỉ phép du lịch cùng gia đình"
    },
    "observation": {
      "status": "SUCCESS",
      "request_id": "LP-NV002-20260913-EBA0",
      "full_name": "Trần Thị Lan",
      "days_requested": 3,
      "manager": "Lê Quốc Bảo",
      "submitted_at": "13/09/2026 15:00"
    },
    "latency_ms": 2011.11
  },
  {
    "step": 2,
    "query": "Tạo đơn xin nghỉ phép năm cho nhân viên NV002 từ ngày 20/09/2026 đến 22/09/2026, lý do nghỉ phép du lịch cùng gia đình.",
    "action_type": "FINAL_ANSWER",
    "thought": "Tổng hợp kết quả từ MCP Server HR VinFast thành công.",
    "output": "✅ Đơn LP-NV002-20260913-EBA0 tạo thành công. Trần Thị Lan nghỉ 3 ngày (20–22/09/2026). Đã gửi tới Lê Quốc Bảo phê duyệt.",
    "latency_ms": 10.0
  }
]
```

**Bảng tóm tắt toàn bộ Test Suite (5/5 Test Cases):**

| Test Case | Câu hỏi | Tool được gọi | Status | Latency |
| :---: | :--- | :--- | :---: | ---: |
| TC01 | Quy định phép năm VinFast? | *(Trả lời trực tiếp — không gọi Tool)* | FINAL_ANSWER | ~10ms |
| TC02 | Tra cứu ngày phép còn lại NV001 | `check_leave_balance` | ✅ SUCCESS | 2094ms |
| TC03 | Chính sách BHXH, BHYT, BHTN hợp đồng full_time | `get_insurance_policy` | ✅ SUCCESS | 1959ms |
| TC04 | Tạo đơn xin nghỉ phép NV002 (20–22/09/2026) | `submit_leave_request` | ✅ SUCCESS | 2011ms |
| TC05 | Tra cứu ngày phép NV999 (không tồn tại) | `check_leave_balance` | ⚠️ NOT_FOUND | 1072ms |

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã cấu hình `GEMINI_API_KEY` trong `.env` — Provider `GeminiProvider` (gemini-2.5-flash-latest) khởi tạo thành công.
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 4 lượt (TC02, TC03, TC04, TC05). TC01 trả lời trực tiếp không cần Tool.
- **MCP Server:** `vinfast-hr-mcp-server v2026.1.0` — 3 Tools đăng ký thành công.
- **Waterfall Trace Log:** File `docs/trace_waterfall.json` xuất đầy đủ 10 sự kiện (2 bước × 5 TC).
- **Kết quả đẩy Repo nộp bài:** [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
