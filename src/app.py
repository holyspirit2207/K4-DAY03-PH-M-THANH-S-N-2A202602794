"""
🚀 CORE AGENT APPLICATION — VINFAST HR ASSISTANT (DAY 03: CHATBOT VS REACT AGENT)
Thực thi so sánh giữa Chatbot Baseline (Cấp 2) và ReAct Agent kết nối MCP Server (Cấp 3).
Đề tài 2.1: Trợ lý Nhân sự VinFast — Tra cứu ngày phép, chính sách bảo hiểm và tạo đơn nghỉ phép.
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from prompts import CHATBOT_BASELINE_PROMPT, REACT_AGENT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider, BaseLLMProvider
from mcp_server import MCPHRServer


def run_chatbot_baseline(query: str, provider: BaseLLMProvider) -> Dict[str, Any]:
    """
    [CẤP 2] CHATBOT BASELINE: Phản hồi dựa trên prompt trực tiếp mà KHÔNG CÓ Tool/MCP Server.
    """
    start_time = time.time()
    response = provider.generate(prompt=query, system_prompt=CHATBOT_BASELINE_PROMPT)
    execution_time = round(time.time() - start_time, 3)

    return {
        "level": "Level 2: Baseline Chatbot",
        "query": query,
        "response": response,
        "execution_time_sec": execution_time,
        "tools_called": []
    }


def run_react_agent(query: str, provider: BaseLLMProvider, mcp_server: MCPHRServer) -> List[Dict[str, Any]]:
    """
    [CẤP 3] REACT AGENT SYSTEM: Vòng lặp suy luận ReAct (Thought -> Action -> Observation) 
    kết nối MCP Server để xử lý câu hỏi thời gian thực.
    """
    tools_schema = mcp_server.list_tools()
    logs = []
    current_prompt = query
    iteration = 0

    print(f"\n🤖 [ReAct Agent] Bắt đầu xử lý Query: '{query}'")

    while iteration < MAX_ITERATIONS:
        iteration += 1
        step_start = time.time()

        # Gọi LLM với Tools Schema qua Adapter
        result = provider.generate_with_tools(
            prompt=current_prompt,
            tools_schema=tools_schema,
            system_prompt=REACT_AGENT_SYSTEM_PROMPT
        )

        step_duration = round(time.time() - step_start, 3)
        thought = result.get("thought", "Đang phân tích yêu cầu...")

        if result.get("type") == "tool_call":
            tool_name = result.get("tool_name")
            arguments = result.get("arguments", {})

            print(f"  🔹 Step {iteration} [THOUGHT]: {thought}")
            print(f"  🛠️ Step {iteration} [ACTION]: Calling MCP Tool '{tool_name}' with args {json.dumps(arguments, ensure_ascii=False)}")

            # Thực thi Tool qua MCP Server
            mcp_response = mcp_server.call_tool(tool_name, arguments)
            tool_result = mcp_response.get("result", {})
            observation_str = json.dumps(tool_result, ensure_ascii=False)

            print(f"  👁️ Step {iteration} [OBSERVATION]: {observation_str[:120]}...")

            logs.append({
                "step": iteration,
                "thought": thought,
                "action": tool_name,
                "action_input": arguments,
                "observation": tool_result,
                "duration_sec": step_duration
            })

            # Cập nhật prompt tiếp theo với kết quả Observation từ Tool
            current_prompt += f"\n\n[System Tool Observation for '{tool_name}']: {observation_str}\nHãy tổng hợp câu trả lời cuối cùng cho nhân viên dựa trên kết quả trên."

        else:
            # LLM đã đưa ra phản hồi văn bản cuối cùng (Final Answer)
            final_text = result.get("content", "")
            print(f"  🔹 Step {iteration} [THOUGHT]: {thought}")
            print(f"  💬 Step {iteration} [FINAL ANSWER]: {final_text[:120]}...")

            logs.append({
                "step": iteration,
                "thought": thought,
                "action": "Final Answer",
                "action_input": None,
                "observation": final_text,
                "duration_sec": step_duration
            })
            break

    return logs


def save_waterfall_trace(logs: List[Dict[str, Any]], filepath: str = "docs/trace_waterfall.json"):
    """Lưu vết luồng ReAct Agent dạng JSON Waterfall để kiểm thử nghiệm thu"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    print(f"💾 Đã lưu Waterfall Trace Log vào: {filepath}")


def run_evaluation_test_suite(provider: BaseLLMProvider, mcp_server: MCPHRServer, test_cases_file: str = "config/test_cases.json"):
    """Kiểm thử tự động 5 Test Cases chuẩn hóa để đánh giá Chatbot vs ReAct Agent"""
    if not os.path.exists(test_cases_file):
        print(f"❌ Không tìm thấy file test cases: {test_cases_file}")
        return

    with open(test_cases_file, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print("\n==========================================================")
    print("🧪 BẮT ĐẦU CHẠY EVALUATION TEST SUITE (5 TEST CASES)")
    print("==========================================================")

    results = []
    for tc in test_cases:
        tc_id = tc.get("id")
        query = tc.get("question") or tc.get("query", "")
        category = tc.get("type") or tc.get("category", "")
        print(f"\n----------------------------------------------------------")
        print(f"📌 [{tc_id}] Category: {category} | Query: '{query}'")

        # 1. Run Baseline Chatbot
        baseline_res = run_chatbot_baseline(query, provider)

        # 2. Run ReAct Agent
        agent_logs = run_react_agent(query, provider, mcp_server)
        tools_called = [l["action"] for l in agent_logs if l["action"] != "Final Answer"]
        final_answer = agent_logs[-1]["observation"] if agent_logs else "No response"

        results.append({
            "id": tc_id,
            "category": category,
            "query": query,
            "baseline_response": baseline_res["response"],
            "agent_final_answer": final_answer,
            "tools_called": tools_called,
            "total_steps": len(agent_logs)
        })

    print("\n==========================================================")
    print("✅ ĐÃ HOÀN THÀNH TẤT CẢ TEST CASES EVALUATION!")
    print("==========================================================")
    return results


def main():
    parser = argparse.ArgumentParser(description="VinFast HR Assistant CLI App")
    parser.add_argument("--interactive", action="store_true", help="Bật chế độ chat tương tác trực tiếp trong Terminal")
    parser.add_argument("--eval", action="store_true", help="Chạy bộ kiểm thử 5 Test Cases mẫu")
    args = parser.parse_args()

    provider = get_llm_provider()
    mcp_server = MCPHRServer()

    print(f"🚀 Initialized VinFast HR System with Provider: {provider.__class__.__name__}")

    if args.interactive:
        print("\n💬 CHẾ ĐỘ INTERACTIVE CHAT — VINFAST HR ASSISTANT")
        print("Gõ 'exit' hoặc 'quit' để thoát.\n")
        while True:
            try:
                user_input = input("👤 Nhân viên VinFast: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit"]:
                    print("👋 Cảm ơn bạn đã sử dụng Trợ lý HR VinFast!")
                    break

                logs = run_react_agent(user_input, provider, mcp_server)
                save_waterfall_trace(logs)
            except (KeyboardInterrupt, EOFError):
                break

    elif args.eval:
        run_evaluation_test_suite(provider, mcp_server)

    else:
        # Mặc định chạy 1 sample test case (TC02: Tra cứu ngày phép NV001)
        sample_query = "Tôi muốn tra cứu số ngày phép còn lại của nhân viên mã NV001"
        print(f"\n--- CHẠY DEMO 1 TEST CASE MẪU (TC02: Tra cứu ngày phép) ---")
        logs = run_react_agent(sample_query, provider, mcp_server)
        save_waterfall_trace(logs)
        print("\n💡 Hãy thử ngay lệnh: python src/app.py --interactive để chat trực tiếp!")


if __name__ == "__main__":
    main()
