"""교보문고 IT 베스트셀러 웹 대시보드 로컬 정적 HTTP 서버 구동 스크립트.

이 스크립트는 kyobooks/src/webapp 디렉터리를 루트로 하여 경량 정적 웹서버를 실행하고
기본 웹 브라우저를 자동으로 실행하여 Chart.js 대시보드를 즉시 체험할 수 있도록 지원합니다.
"""

from __future__ import annotations

import argparse
import functools
import http.server
from pathlib import Path
import socket
import sys
import webbrowser

# Windows 콘솔 인코딩 대응
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# 프로젝트 상대경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent  # kyobooks 디렉터리
WEBAPP_DIR = BASE_DIR / "src" / "webapp"


def is_port_available(port: int) -> bool:
    """해당 포트가 사용 가능한지 확인합니다."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def find_available_port(start_port: int = 8080, max_tries: int = 10) -> int:
    """사용 가능한 포트를 순차적으로 탐색합니다."""
    for p in range(start_port, start_port + max_tries):
        if is_port_available(p):
            return p
    return start_port


def run_server(port: int = 8080, open_browser: bool = True, dry_run: bool = False) -> None:
    """정적 웹서버를 실행합니다."""
    if not WEBAPP_DIR.exists():
        print(f"[오류] 웹앱 디렉터리가 존재하지 않습니다: {WEBAPP_DIR}")
        sys.exit(1)

    index_html = WEBAPP_DIR / "index.html"
    data_js = WEBAPP_DIR / "data.js"
    if not index_html.exists() or not data_js.exists():
        print(f"[오류] 필수 웹앱 파일이 누락되었습니다 (index.html 또는 data.js).")
        sys.exit(1)

    target_port = find_available_port(port)

    print("=" * 60)
    print("[서버] 교보문고 IT 베스트셀러 웹 대시보드 로컬 서버")
    print(f"- 서빙 디렉터리: {WEBAPP_DIR}")
    print(f"- 접속 URL: http://localhost:{target_port}")
    print("=" * 60)


    if dry_run:
        print("[성공] Dry-run 모드 검증 완료: 모든 필수 리소스가 정상 준비되었습니다.")
        return

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(WEBAPP_DIR))

    with http.server.ThreadingHTTPServer(("127.0.0.1", target_port), handler) as httpd:
        url = f"http://localhost:{target_port}"
        if open_browser:
            print(f"[안내] 웹 브라우저를 자동으로 실행합니다: {url}")
            webbrowser.open(url)
        print("[안내] 서버가 정상 실행 중입니다. (종료하려면 Ctrl+C를 누르세요)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[안내] 사용자에 의해 서버가 정상 종료되었습니다.")


def main() -> None:
    """메인 실행 함수."""
    parser = argparse.ArgumentParser(description="교보문고 IT 베스트셀러 웹 대시보드 로컬 서버")
    parser.add_argument("--port", type=int, default=8080, help="서버 포트 번호 (기본값: 8080)")
    parser.add_argument("--no-browser", action="store_true", help="브라우저 자동 실행 비활성화")
    parser.add_argument("--dry-run", action="store_true", help="서버 실행 전 파일 및 포트 검증만 수행")
    args = parser.parse_args()

    run_server(port=args.port, open_browser=not args.no_browser, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
