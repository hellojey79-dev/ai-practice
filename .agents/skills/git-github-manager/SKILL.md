---
name: git-github-manager
description: Git과 GitHub를 활용한 버전 관리, 커밋, 브랜치 전략, 원격 저장소 연동, PR(Pull Request), 충돌(Conflict) 해결, 변경 사항 추적 및 릴리스 관리 작업 시 반드시 활성화하는 전문 Git 버전 관리 스킬입니다. 사용자가 Git, GitHub, 버전 관리, commit, branch, push, pull, PR, merge, rebase, cherry-pick, stash, conflict, .gitignore 등을 언급하거나 레포지토리 관리 작업을 요청할 때 항상 이 스킬을 사용하세요.
---

# Git & GitHub 버전 관리 전문 가이드 (`git-github-manager`)

Git과 GitHub를 활용하여 안전하고 체계적인 소스 코드 버전 관리, 협업 워크플로, 릴리스 관리를 수행하는 엔지니어링 가이드입니다.

---

## 1. 핵심 원칙 및 작업 철학

1. **상태 먼저 확인 (Inspect First)**: 명령을 실행하기 전 반드시 `git status`와 `git diff`로 현재 작업 트리와 변경 내역을 확인합니다.
2. **원자적 커밋 (Atomic Commit)**: 하나의 커밋에는 논리적으로 하나의 변경 단위만 포함합니다. 관련 없는 여러 작업은 분리하여 커밋합니다.
3. **민감 정보 절대 커밋 금지**: API 키, 비밀번호, `.env`, 인증 토큰, 대용량 바이너리, 가상환경(`.venv`), 캐시 폴더는 커밋 전에 `.gitignore`로 철저히 차단합니다.
4. **Conventional Commits 준수**: 커밋 메시지는 표준화된 접두어(prefix)와 명확한 한 줄 요약, 필요 시 상세 본문으로 구성합니다.
5. **안전한 브랜치 전략**: 메인 브랜치(`main` / `master`)에 직접 커밋하지 않고 기능 단위 브랜치(`feature/*`, `fix/*`)에서 작업 후 PR을 통해 병합합니다.

---

## 2. 프로젝트 초기화 및 `.gitignore` 설정

### 2.1 저장소 초기화 및 기본 브랜치 설정
```bash
# Git 저장소 초기화
git init

# 기본 브랜치를 main으로 설정
git branch -M main

# 로컬 사용자 정보 확인 및 설정 (필요시)
git config user.name "Your Name"
git config user.email "your-email@example.com"
```

### 2.2 표준 파이썬/프로젝트 `.gitignore` 템플릿
저장소 루트에 `.gitignore` 파일을 작성하여 불필요한 빌드 아티팩트 및 가상환경을 제외합니다.
```gitignore
# 가상환경 및 패키지 매니저
.venv/
venv/
ENV/
env/

# 파이썬 바이트코드 및 캐시
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.coverage
htmlcov/

# 환경 변수 및 보안 키
.env
.env.local
*.pem
*.key

# IDE 및 OS 설정
.vscode/
.idea/
.DS_Store
Thumbs.db

# 대용량 데이터 및 임시 파일 (필요시 조정)
data/raw/
*.csv.gz
*.parquet
scratch/
```

---

## 3. 일상적인 버전 관리 워크플로

### 3.1 단계별 실행 순서
1. **상태 점검**:
   ```bash
   git status
   ```
2. **변경 내역 검토**:
   ```bash
   git diff
   ```
3. **선별적 스테이징**: 전체 추가(`git add .`)를 지양하고 변경된 개별 파일 단위로 스테이징합니다.
   ```bash
   git add <파일경로1> <파일경로2>
   ```
4. **커밋 작성**: Conventional Commit 규칙을 준수하여 작성합니다.
   ```bash
   git commit -m "feat(analysis): YES24 판매지수 왜도 분석 로직 추가"
   ```

---

## 4. Conventional Commits 메시지 규격

### 4.1 커밋 태그(Type) 분류표
| 태그 | 목적 | 예시 |
|:---|:---|:---|
| `feat` | 새로운 기능 추가 | `feat(auth): 사용자 소셜 로그인 기능 추가` |
| `fix` | 버그 수정 | `fix(chart): 판매지수 이상치 렌더링 오류 수정` |
| `docs` | 문서 수정 및 추가 | `docs(readme): 프로젝트 실행 방법 가이드 추가` |
| `style` | 코드 포맷팅, 세미콜론 누락 등 (로직 변경 없음) | `style: black 및 ruff 린터 포맷 적용` |
| `refactor` | 코드 리팩토링 (기능 변경 없는 구조 개선) | `refactor(pipeline): 데이터 전처리 모듈 분리` |
| `test` | 테스트 코드 추가 또는 테스트 리팩토링 | `test(eda): 결측치 정제 단위 테스트 추가` |
| `chore` | 빌드 업무, 패키지 매니저 설정, 의존성 업데이트 | `chore(deps): python-pptx 1.0.2 의존성 추가` |

### 4.2 커밋 메시지 구조
```
<type>(<scope>): <간결한 한 줄 요약>

[선택적 본문]
- 무엇을 왜 변경했는지 구체적인 배경 설명
- 문제 해결 방식과 설계상 결정 사항 기술

[선택적 꼬리말]
Resolves: #123
```

---

## 5. 브랜치 전략 (GitHub Flow)

### 5.1 브랜치 명명 규칙
- `feature/<기능명>`: 새 기능 개발 (예: `feature/pptx-generator`)
- `fix/<버그명>`: 오류 수정 (예: `fix/rating-calculation`)
- `docs/<문서명>`: 문서화 작업 (예: `docs/eda-report`)
- `refactor/<대상>`: 대규모 구조 개선 (예: `refactor/data-loader`)

### 5.2 브랜치 작업 라이프사이클
```bash
# 1. main 최신화
git checkout main
git pull origin main

# 2. 새 기능 브랜치 생성 및 이동
git checkout -b feature/eda-presentation

# 3. 작업 진행 후 커밋
git add yes24/src/generate_pptx.py
git commit -m "feat(pptx): 30페이지 발표자료 자동 생성 모듈 구현"

# 4. 원격 저장소로 브랜치 푸시
git push -u origin feature/eda-presentation
```

---

## 6. GitHub 원격 저장소 연동 및 PR 워크플로

### 6.1 원격 저장소 연결
```bash
# 원격 저장소 추가
git remote add origin https://github.com/<사용자명>/<저장소명>.git

# 원격 저장소 연결 확인
git remote -v

# 첫 푸시 (기본 업스트림 지정)
git push -u origin main
```

### 6.2 Pull Request (PR) 템플릿
GitHub에서 PR을 생성할 때는 다음 구조로 기술합니다:
```markdown
## 📌 개요
- 작업 목적 및 배경 간략 요약

## 🛠️ 주요 변경 사항
- [x] 변경점 1
- [x] 변경점 2

## 🧪 테스트 및 검증 결과
- 테스트 실행 결과 및 스크린샷

## 🔗 관련 이슈
- Closes #관련이슈번호
```

---

## 7. 충돌(Conflict) 해결 가이드

두 브랜치에서 동일한 파일의 같은 라인을 수정한 경우 충돌이 발생합니다.

### 7.1 해결 절차
1. **충돌 상태 확인**:
   ```bash
   git status
   ```
2. **충돌 파일 열기**: 마커(`<<<<<<<`, `=======`, `>>>>>>>`) 확인
   ```
   <<<<<<< HEAD (현재 브랜치)
   current_value = 100
   =======
   incoming_value = 200
   >>>>>>> feature/new-logic (병합 대상 브랜치)
   ```
3. **충돌 내용 수동 정리**: 필요한 코드를 취합하고 충돌 마커 완전히 삭제
4. **해결 완료 파일 스테이징 및 커밋**:
   ```bash
   git add <충돌해결파일>
   git commit -m "fix(merge): feature 브랜치 병합 충돌 해결"
   ```

---

## 8. 안전 수칙 및 긴급 복구 (Safety & Undo)

| 상황 | 해결 명령 | 주의사항 |
|:---|:---|:---|
| **방금 한 커밋 메시지만 수정** | `git commit --amend -m "새 메시지"` | 이미 원격에 푸시된 경우 지양 |
| **작업 중이던 파일 임시 보관** | `git stash` / `git stash pop` | 브랜치 전환 전 작업 보존 시 유용 |
| **스테이징 취소 (unstage)** | `git restore --staged <파일>` | 작업 파일 내용은 유지됨 |
| **파일 수정사항 되돌리기** | `git restore <파일>` | ⚠️ 되돌린 수정사항은 복구 불가 |
| **원격 강제 푸시** | ⚠️ `git push --force` 절대 금지 | 팀원 작업 덮어쓰기 위험. 필요 시 `--force-with-lease` 고려 |
