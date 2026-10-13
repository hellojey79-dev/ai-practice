"""라이프사이클 훅 러너: 에이전트 실행 시 하네스 품질 표준 점검 및 피드백 주입."""

import sys
import json

# Windows 콘솔 인코딩 대응
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

def handle_pre_invocation(data):
    """PreInvocation 이벤트 처리: 파이프라인 규칙 및 표준 가이드 주입."""
    response = {
        "injectSteps": [
            {
                "ephemeralMessage": (
                    "[하네스 파이프라인 안내] 신규 도메인/사이트 작업 시:\n"
                    "1. 워크스페이스 공통 .venv 사용 (uv run python)\n"
                    "2. 신규 폴더 생성 시 4대 하위 폴더(images, docs, src, data) 필수 구성\n"
                    "3. Matplotlib 시각화 시 koreanize_matplotlib 사용 및 Seaborn 스타일 전역 함수 배제\n"
                    "4. 대시보드 구축 시 data.js 전역 객체 임베딩으로 로컬 CORS 차단 방지\n"
                    "5. 모든 코드 docstring 및 설명은 한국어로만 작성"
                )
            }
        ]
    }
    print(json.dumps(response, ensure_ascii=False))

def handle_post_tool_use(data):
    """PostToolUse 이벤트 처리: 빈 JSON 객체 반환."""
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
    elif event_type == "PostToolUse":
        handle_post_tool_use(payload)
    else:
        print(json.dumps({}, ensure_ascii=False))

if __name__ == "__main__":
    main()
