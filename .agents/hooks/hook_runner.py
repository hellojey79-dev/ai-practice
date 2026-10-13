"""라이프사이클 훅 러너: 에이전트 실행 시 하네스 품질 표준 점검 및 피드백 주입.

이 모듈은 Antigravity 에이전트의 라이프사이클(PreInvocation, PreToolUse, PostToolUse)에
연동되어 파괴적 명령어 사전 차단(Safety Gate), 품질 표준 가이드라인 실시간 주입,
도구 실행 감사 로깅 및 데이터 품질 모니터링을 수행합니다.
"""

import sys
import os
import json
import re
from datetime import datetime

# Windows 콘솔 인코딩 대응
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

# 파괴적 위험 명령어 패턴 목록 (PreToolUse 차단 대상)
DANGEROUS_COMMAND_PATTERNS = [
    r"rmdir\s+/[sS]\s+/[qQ]\s+[cC]:\\",
    r"rm\s+-rf\s+/\s*$",
    r"git\s+push\s+.*--force",
    r"git\s+push\s+.*-f\b",
    r"format\s+[cC]:",
    r"del\s+/[fF]\s+/[sS]\s+/[qQ]\s+[cC]:\\",
    r"drop\s+database",
]

def log_audit_event(event_type: str, detail: str):
    """훅 실행 감사 로그를 기록합니다 (.agents/hooks/hook_audit.log)."""
    try:
        log_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(log_dir, "hook_audit.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{event_type}] {detail}\n")
    except Exception:
        pass  # 로깅 실패로 인해 훅 실행이 중단되지 않도록 보호

def handle_pre_invocation(data):
    """PreInvocation 이벤트 처리: 파이프라인 규칙 및 6대 메타 스키마 표준 주입."""
    guideline_message = (
        "[하네스 파이프라인 실시간 가이드]\n"
        "1. 가상환경: 워크스페이스 공통 .venv 사용 (uv run python)\n"
        "2. 구조 표준: 신규 사이트/도메인 생성 시 4대 하위 폴더(images, docs, src, data) 필수 구성\n"
        "3. 데이터 추상화: 6대 메타 스키마(item_id, title, category, brand, metric_primary, metric_secondary) 준수\n"
        "4. 시각화 안전: Matplotlib 한글 폰트 적용(koreanize_matplotlib) 및 Seaborn 전역 스타일 충돌 방지\n"
        "5. 대시보드 무결성: data.js 전역 객체 임베딩으로 로컬 브라우저 CORS 차단 원천 방지\n"
        "6. 품질 보증: 모든 파이썬 파일 상단 한글 Docstring 작성 및 크롤링 후 validate_dataset.py 무결성 검증 필수"
    )
    response = {
        "injectSteps": [
            {
                "ephemeralMessage": guideline_message
            }
        ]
    }
    log_audit_event("PreInvocation", "표준 가이드라인 메시지 주입 완료")
    print(json.dumps(response, ensure_ascii=False))

def handle_pre_tool_use(data):
    """PreToolUse 이벤트 처리: 파괴적 명령어 사전 차단 및 안전성 검증."""
    tool_call = data.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    args = tool_call.get("args", {})
    
    # run_command 안전성 검사
    if tool_name == "run_command":
        cmd_line = args.get("CommandLine", "")
        for pattern in DANGEROUS_COMMAND_PATTERNS:
            if re.search(pattern, cmd_line, re.IGNORECASE):
                log_audit_event("PreToolUse_BLOCK", f"위험 명령어 차단: {cmd_line}")
                response = {
                    "decision": "deny",
                    "reason": (
                        f"[하네스 안전 가드레일] 시스템 파괴 또는 위험 명령어가 감지되어 실행이 차단되었습니다: {cmd_line}"
                    )
                }
                print(json.dumps(response, ensure_ascii=False))
                return

    log_audit_event("PreToolUse_ALLOW", f"도구 실행 승인: {tool_name}")
    response = {
        "decision": "allow"
    }
    print(json.dumps(response, ensure_ascii=False))

def handle_post_tool_use(data):
    """PostToolUse 이벤트 처리: 도구 실행 후 감사 기록 및 데이터 변경 감지."""
    tool_name = data.get("toolName", "unknown")
    step_idx = data.get("stepIdx", 0)
    has_error = "error" in data
    
    log_audit_event("PostToolUse", f"도구 완료: {tool_name} (step: {step_idx}, error: {has_error})")
    print(json.dumps({}, ensure_ascii=False))

def main():
    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input.strip() else {}
    except Exception:
        payload = {}

    event_type = sys.argv[1] if len(sys.argv) > 1 else "PreInvocation"

    if event_type == "PreInvocation":
        handle_pre_invocation(payload)
    elif event_type == "PreToolUse":
        handle_pre_tool_use(payload)
    elif event_type == "PostToolUse":
        handle_post_tool_use(payload)
    else:
        print(json.dumps({}, ensure_ascii=False))

if __name__ == "__main__":
    main()
