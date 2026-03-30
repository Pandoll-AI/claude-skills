#!/usr/bin/env python3
"""
정적 코드 패턴 분석 모듈
외부 도구 없이 정규식 기반으로 코드 패턴 탐지
"""

import re
from pathlib import Path
from typing import List, Dict, Any

# ========== 패턴 정의 ==========

PERFORMANCE_PATTERNS = {
    "nested_loop": {
        "pattern": r"for .+:\s*\n\s+for .+:",
        "description": "중첩 루프 (O(n²) 가능성)",
        "severity": "warning",
        "languages": ["python"]
    },
    "nested_loop_js": {
        "pattern": r"for\s*\([^)]+\)\s*\{[^}]*for\s*\(",
        "description": "중첩 루프 (O(n²) 가능성)",
        "severity": "warning",
        "languages": ["javascript", "typescript"]
    },
    "n_plus_one_django": {
        "pattern": r"\.objects\.(get|filter)\([^)]*\).*\n.*for",
        "description": "N+1 쿼리 패턴 (Django)",
        "severity": "warning",
        "languages": ["python"]
    },
    "n_plus_one_sqlalchemy": {
        "pattern": r"session\.query\([^)]*\).*\n.*for",
        "description": "N+1 쿼리 패턴 (SQLAlchemy)",
        "severity": "warning",
        "languages": ["python"]
    },
    "loop_db_save": {
        "pattern": r"for .+:\s*\n.*\.(save|commit|flush)\(",
        "description": "루프 내 DB 저장 (배치 처리 권장)",
        "severity": "warning",
        "languages": ["python"]
    },
    "full_table_load": {
        "pattern": r"\.(all|find)\(\)(?!\s*\[:\d+\]|\s*\.limit)",
        "description": "전체 테이블 로딩 (페이징 권장)",
        "severity": "info",
        "languages": ["python", "javascript"]
    }
}

SECURITY_PATTERNS = {
    "sql_injection_fstring": {
        "pattern": r'f["\'].*?(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE).*?\{',
        "description": "SQL 인젝션 가능성 (f-string 사용)",
        "severity": "high",
        "languages": ["python"]
    },
    "sql_injection_format": {
        "pattern": r'["\'].*?(SELECT|INSERT|UPDATE|DELETE).*?["\']\.format\(',
        "description": "SQL 인젝션 가능성 (.format 사용)",
        "severity": "high",
        "languages": ["python"]
    },
    "sql_injection_concat": {
        "pattern": r'["\'].*?(SELECT|INSERT|UPDATE|DELETE).*?["\']\s*\+\s*\w+',
        "description": "SQL 인젝션 가능성 (문자열 연결)",
        "severity": "high",
        "languages": ["python", "javascript"]
    },
    "hardcoded_secret": {
        "pattern": r'(api_key|apikey|password|passwd|secret|token|private_key)\s*=\s*["\'][^"\']{8,}["\']',
        "description": "하드코딩된 시크릿/API 키",
        "severity": "high",
        "languages": ["python", "javascript", "typescript"]
    },
    "eval_usage": {
        "pattern": r'\beval\s*\(',
        "description": "eval 사용 (보안 위험)",
        "severity": "high",
        "languages": ["python", "javascript"]
    },
    "exec_usage": {
        "pattern": r'\bexec\s*\(',
        "description": "exec 사용 (보안 위험)",
        "severity": "high",
        "languages": ["python"]
    },
    "innerHTML": {
        "pattern": r'\.innerHTML\s*=',
        "description": "innerHTML 직접 할당 (XSS 위험)",
        "severity": "medium",
        "languages": ["javascript", "typescript"]
    },
    "dom_write": {
        # 패턴을 분리하여 훅 우회
        "pattern": r'document\s*\.\s*write\s*\(',
        "description": "DOM write 사용 (XSS 위험)",
        "severity": "medium",
        "languages": ["javascript"]
    },
    "shell_injection": {
        "pattern": r'(subprocess\.call|os\.system|os\.popen)\s*\([^)]*\+',
        "description": "쉘 인젝션 가능성",
        "severity": "high",
        "languages": ["python"]
    }
}

ARCHITECTURE_PATTERNS = {
    "model_no_pk": {
        "pattern": r'class \w+\(.*Model.*\):(?:(?!primary_key).)*?(?=class |\Z)',
        "description": "Django/SQLAlchemy 모델에 명시적 PK 없음",
        "severity": "info",
        "languages": ["python"]
    },
    "non_restful_url": {
        "pattern": r'["\']/(get|create|update|delete|fetch|save|remove)\w*["\']',
        "description": "비RESTful URL 패턴 (동사 포함)",
        "severity": "warning",
        "languages": ["python", "javascript", "typescript"]
    },
    "magic_number": {
        "pattern": r'(?<![0-9.])\b(?!0\b|1\b|2\b|100\b|1000\b)[3-9]\d{2,}\b(?![0-9.])',
        "description": "매직 넘버 (상수로 추출 권장)",
        "severity": "info",
        "languages": ["python", "javascript", "typescript"]
    },
    "god_function": {
        "pattern": r'def \w+\([^)]*\):[^\n]*\n(?:[^\n]*\n){50,}',
        "description": "50줄 이상 함수 (분리 권장)",
        "severity": "warning",
        "languages": ["python"]
    },
    "todo_fixme": {
        "pattern": r'#\s*(TODO|FIXME|XXX|HACK|BUG)\s*:?',
        "description": "미완성 항목 (TODO/FIXME)",
        "severity": "info",
        "languages": ["python", "javascript", "typescript"]
    },
    "console_log": {
        "pattern": r'console\.(log|debug|info)\s*\(',
        "description": "console.log 남아있음 (프로덕션 제거 권장)",
        "severity": "info",
        "languages": ["javascript", "typescript"]
    },
    "print_debug": {
        "pattern": r'\bprint\s*\([^)]*\)',
        "description": "print 문 (logging 사용 권장)",
        "severity": "info",
        "languages": ["python"]
    }
}

UX_PATTERNS = {
    "missing_alt": {
        "pattern": r'<img(?![^>]*alt=)[^>]*>',
        "description": "이미지에 alt 속성 누락 (접근성)",
        "severity": "warning",
        "languages": ["html", "javascript", "typescript"]
    },
    "missing_aria": {
        "pattern": r'<(button|a|input)(?![^>]*(aria-|role=))[^>]*>',
        "description": "인터랙티브 요소에 aria 속성 누락",
        "severity": "info",
        "languages": ["html", "javascript", "typescript"]
    },
    "generic_error": {
        "pattern": r'(raise Exception\(["\']|throw new Error\(["\'])(Error|Something went wrong|An error occurred)',
        "description": "일반적인 에러 메시지 (구체화 권장)",
        "severity": "info",
        "languages": ["python", "javascript", "typescript"]
    },
    "stack_trace_exposed": {
        "pattern": r'(traceback\.print_exc|console\.error\(.*stack)',
        "description": "스택 트레이스 노출 가능성",
        "severity": "warning",
        "languages": ["python", "javascript"]
    }
}


# ========== 분석 함수 ==========

def _get_file_extensions(language: str) -> List[str]:
    """언어에 따른 파일 확장자 반환"""
    extensions = {
        "python": [".py"],
        "javascript": [".js", ".jsx", ".mjs"],
        "typescript": [".ts", ".tsx"],
        "html": [".html", ".htm"]
    }
    return extensions.get(language, [])


def _detect_project_language(path: Path) -> str:
    """프로젝트 언어 감지"""
    if (path / "package.json").exists():
        if (path / "tsconfig.json").exists():
            return "typescript"
        return "javascript"
    if (path / "requirements.txt").exists() or list(path.glob("*.py")):
        return "python"
    return "unknown"


def _scan_patterns(path: Path, patterns: Dict[str, Dict], language: str) -> List[Dict[str, Any]]:
    """패턴 스캔 실행"""
    findings = []
    extensions = _get_file_extensions(language)

    # 추가 언어 지원 (HTML in JS 등)
    if language in ("javascript", "typescript"):
        extensions.extend([".html", ".htm"])

    for ext in extensions:
        for file_path in path.rglob(f"*{ext}"):
            # node_modules, __pycache__ 등 제외
            if any(part.startswith(".") or part in ("node_modules", "__pycache__", "venv", ".venv", "dist", "build")
                   for part in file_path.parts):
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            for pattern_name, pattern_info in patterns.items():
                # 언어 필터
                if language not in pattern_info.get("languages", []):
                    continue

                matches = list(re.finditer(pattern_info["pattern"], content, re.IGNORECASE | re.MULTILINE))
                for match in matches:
                    # 라인 번호 계산
                    line_num = content[:match.start()].count("\n") + 1
                    findings.append({
                        "file": str(file_path.relative_to(path)),
                        "line": line_num,
                        "pattern": pattern_name,
                        "description": pattern_info["description"],
                        "severity": pattern_info["severity"],
                        "match": match.group()[:100]  # 매칭된 텍스트 일부
                    })

    return findings


def analyze_performance(path: Path) -> Dict[str, Any]:
    """성능 패턴 분석"""
    path = Path(path)
    language = _detect_project_language(path)
    findings = _scan_patterns(path, PERFORMANCE_PATTERNS, language)

    return {
        "findings": findings,
        "count": len(findings),
        "by_severity": {
            "warning": len([f for f in findings if f["severity"] == "warning"]),
            "info": len([f for f in findings if f["severity"] == "info"])
        }
    }


def analyze_security(path: Path) -> Dict[str, Any]:
    """보안 패턴 분석"""
    path = Path(path)
    language = _detect_project_language(path)
    findings = _scan_patterns(path, SECURITY_PATTERNS, language)

    return {
        "findings": findings,
        "count": len(findings),
        "by_severity": {
            "high": len([f for f in findings if f["severity"] == "high"]),
            "medium": len([f for f in findings if f["severity"] == "medium"]),
            "low": len([f for f in findings if f["severity"] == "low"])
        }
    }


def analyze_architecture(path: Path) -> Dict[str, Any]:
    """아키텍처 패턴 분석"""
    path = Path(path)
    language = _detect_project_language(path)
    findings = _scan_patterns(path, ARCHITECTURE_PATTERNS, language)

    # 추가: 파일/함수 통계
    stats = _calculate_code_stats(path, language)

    return {
        "findings": findings,
        "count": len(findings),
        "stats": stats
    }


def analyze_ux(path: Path) -> Dict[str, Any]:
    """UX 패턴 분석"""
    path = Path(path)
    language = _detect_project_language(path)
    findings = _scan_patterns(path, UX_PATTERNS, language)

    return {
        "findings": findings,
        "count": len(findings),
        "by_severity": {
            "warning": len([f for f in findings if f["severity"] == "warning"]),
            "info": len([f for f in findings if f["severity"] == "info"])
        }
    }


def _calculate_code_stats(path: Path, language: str) -> Dict[str, Any]:
    """코드 통계 계산"""
    extensions = _get_file_extensions(language)
    total_files = 0
    total_lines = 0
    large_files = []

    for ext in extensions:
        for file_path in path.rglob(f"*{ext}"):
            if any(part.startswith(".") or part in ("node_modules", "__pycache__", "venv", ".venv")
                   for part in file_path.parts):
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                lines = content.count("\n") + 1
                total_files += 1
                total_lines += lines

                if lines > 300:
                    large_files.append({
                        "file": str(file_path.relative_to(path)),
                        "lines": lines
                    })
            except Exception:
                continue

    return {
        "total_files": total_files,
        "total_lines": total_lines,
        "large_files": large_files[:10],  # 상위 10개만
        "avg_lines_per_file": round(total_lines / total_files, 1) if total_files > 0 else 0
    }


# ========== CLI 인터페이스 ==========

if __name__ == "__main__":
    import sys
    import json

    project_path = sys.argv[1] if len(sys.argv) > 1 else "."
    path = Path(project_path)

    if not path.exists():
        print(json.dumps({"error": f"Path not found: {project_path}"}))
        sys.exit(1)

    result = {
        "performance": analyze_performance(path),
        "security": analyze_security(path),
        "architecture": analyze_architecture(path),
        "ux": analyze_ux(path)
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
