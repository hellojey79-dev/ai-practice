"""하네스 웹 대시보드 로컬 정적 HTTP 서버 구동 스크립트.

이 스크립트는 harness/src/webapp 디렉터리를 루트로 하여 정적 웹서버를 가동하고
브라우저를 자동으로 실행합니다.
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

BASE_DIR = Path(__file__).resolve().parent.parent  # harness 디렉터리
WEBAPP_DIR = BASE_DIR / "src" / "webapp"


def is_port_available(port: int) -> bool:
    """포트 점유 여부 확인."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def find_available_port(start_port: int = 8080, max_tries: int = 10) -> int:
    """사용 가능한 포트 탐색."""
    for p in range(start_port, start_port + max_tries):
        if is_port_available(p):
            return p
    return start_port


def run_server(port: int = 8080, open_browser: bool = True, dry_run: bool = False) -> None:
    """웹서버 실행."""
    if not WEBAPP_DIR.exists():
        print(f"[오류] 웹앱 폴더 부재: {WEBAPP_DIR}")
        sys.exit(1)

    target_port = find_available_port(port)

    print("=" * 60)
    print(f"[하네스 웹서버] 서빙 경로: {WEBAPP_DIR}")
    print(f"- 접속 URL: http://localhost:{target_port}")
    print("=" * 60)

    if dry_run:
        print("[성공] Dry-run 검증 완료")
        return

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(WEBAPP_DIR))
    with http.server.ThreadingHTTPServer(("127.0.0.1", target_port), handler) as httpd:
        url = f"http://localhost:{target_port}"
        if open_browser:
            webbrowser.open(url)
        print("[안내] 서버 가동 중 (종료: Ctrl+C)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[안내] 서버 종료")


def main() -> None:
    """CLI 메인 함수."""
    parser = argparse.ArgumentParser(description="하네스 웹서버")
    parser.add_argument("--port", type=int, default=8080, help="포트")
    parser.add_argument("--no-browser", action="store_true", help="브라우저 자동 오픈 끄기")
    parser.add_argument("--dry-run", action="store_true", help="검증만 수행")
    args = parser.parse_args()

    run_server(port=args.port, open_browser=not args.no_browser, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
