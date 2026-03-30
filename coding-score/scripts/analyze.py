#!/usr/bin/env python3
"""
프로젝트 품질 통합 분석 스크립트
Python/JavaScript 프로젝트 자동 감지 및 분석
"""

import json
import subprocess
import sys
import shutil
from pathlib import Path
from typing import Optional

# 같은 디렉토리의 patterns 모듈 임포트
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import patterns
except ImportError:
    patterns = None


class ProjectAnalyzer:
    """프로젝트 품질 분석기"""

    def __init__(self, project_path: str):
        self.path = Path(project_path).resolve()
        self.language = self._detect_language()
        self.tools_available = {}

    def _detect_language(self) -> str:
        """프로젝트 언어 자동 감지"""
        # JavaScript/TypeScript 우선 체크
        if (self.path / "package.json").exists():
            return "javascript"
        if (self.path / "tsconfig.json").exists():
            return "typescript"

        # Python 체크
        if (self.path / "requirements.txt").exists():
            return "python"
        if (self.path / "pyproject.toml").exists():
            return "python"
        if (self.path / "setup.py").exists():
            return "python"
        if list(self.path.glob("*.py")):
            return "python"

        return "unknown"

    def _check_tool(self, tool: str) -> bool:
        """도구 설치 여부 확인 (캐싱)"""
        if tool not in self.tools_available:
            self.tools_available[tool] = shutil.which(tool) is not None
        return self.tools_available[tool]

    def _run_command(self, cmd: list, timeout: int = 120) -> Optional[dict]:
        """명령 실행 및 결과 반환"""
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.path),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"error": "timeout", "returncode": -1}
        except Exception as e:
            return {"error": str(e), "returncode": -1}

    # ========== Python 분석 ==========

    def _run_pytest(self) -> dict:
        """pytest 실행"""
        if not self._check_tool("pytest"):
            return {"available": False, "message": "pytest not installed"}

        result = self._run_command(["pytest", "--tb=short", "-q"])
        if not result or result.get("error"):
            return {"available": True, "error": result.get("error", "unknown")}

        # 결과 파싱
        output = result["stdout"] + result["stderr"]
        passed = failed = 0

        for line in output.split("\n"):
            if "passed" in line:
                import re
                match = re.search(r"(\d+) passed", line)
                if match:
                    passed = int(match.group(1))
            if "failed" in line:
                import re
                match = re.search(r"(\d+) failed", line)
                if match:
                    failed = int(match.group(1))

        total = passed + failed
        pass_rate = (passed / total * 100) if total > 0 else 0

        return {
            "available": True,
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": round(pass_rate, 1)
        }

    def _run_coverage(self) -> dict:
        """coverage.py 실행"""
        if not self._check_tool("coverage"):
            return {"available": False, "message": "coverage not installed"}

        # coverage run
        self._run_command(["coverage", "run", "-m", "pytest", "-q"], timeout=180)

        # coverage report
        result = self._run_command(["coverage", "report", "--format=total"])
        if not result or result.get("error"):
            return {"available": True, "error": result.get("error", "unknown")}

        try:
            coverage_pct = float(result["stdout"].strip())
            return {"available": True, "percentage": coverage_pct}
        except (ValueError, AttributeError):
            return {"available": True, "percentage": None, "raw": result["stdout"]}

    def _run_pylint(self) -> dict:
        """pylint 실행"""
        if not self._check_tool("pylint"):
            return {"available": False, "message": "pylint not installed"}

        py_files = list(self.path.rglob("*.py"))
        if not py_files:
            return {"available": True, "message": "no Python files found"}

        # 최대 10개 파일만 분석 (성능)
        files_to_check = [str(f) for f in py_files[:10]]
        result = self._run_command(
            ["pylint", "--output-format=json", "--max-line-length=120"] + files_to_check,
            timeout=60
        )

        if not result:
            return {"available": True, "error": "execution failed"}

        try:
            issues = json.loads(result["stdout"]) if result["stdout"] else []
            error_count = sum(1 for i in issues if i.get("type") == "error")
            warning_count = sum(1 for i in issues if i.get("type") == "warning")
            convention_count = sum(1 for i in issues if i.get("type") == "convention")

            return {
                "available": True,
                "errors": error_count,
                "warnings": warning_count,
                "conventions": convention_count,
                "total_issues": len(issues)
            }
        except json.JSONDecodeError:
            return {"available": True, "raw": result["stdout"][:500]}

    def _run_bandit(self) -> dict:
        """bandit 보안 검사"""
        if not self._check_tool("bandit"):
            return {"available": False, "message": "bandit not installed"}

        result = self._run_command(
            ["bandit", "-r", ".", "-f", "json", "-q"],
            timeout=60
        )

        if not result:
            return {"available": True, "error": "execution failed"}

        try:
            data = json.loads(result["stdout"]) if result["stdout"] else {}
            results = data.get("results", [])

            high = sum(1 for r in results if r.get("issue_severity") == "HIGH")
            medium = sum(1 for r in results if r.get("issue_severity") == "MEDIUM")
            low = sum(1 for r in results if r.get("issue_severity") == "LOW")

            return {
                "available": True,
                "high": high,
                "medium": medium,
                "low": low,
                "total": len(results)
            }
        except json.JSONDecodeError:
            return {"available": True, "raw": result["stdout"][:500]}

    def _run_radon(self) -> dict:
        """radon 복잡도 분석"""
        if not self._check_tool("radon"):
            return {"available": False, "message": "radon not installed"}

        result = self._run_command(["radon", "cc", ".", "-j", "-a"], timeout=60)

        if not result:
            return {"available": True, "error": "execution failed"}

        try:
            data = json.loads(result["stdout"]) if result["stdout"] else {}
            complexities = []

            for file_path, funcs in data.items():
                if isinstance(funcs, list):
                    for func in funcs:
                        if isinstance(func, dict):
                            complexities.append(func.get("complexity", 0))

            if complexities:
                avg_complexity = sum(complexities) / len(complexities)
                max_complexity = max(complexities)
                high_complexity_count = sum(1 for c in complexities if c > 10)
            else:
                avg_complexity = 0
                max_complexity = 0
                high_complexity_count = 0

            return {
                "available": True,
                "average": round(avg_complexity, 2),
                "max": max_complexity,
                "high_complexity_functions": high_complexity_count
            }
        except json.JSONDecodeError:
            return {"available": True, "raw": result["stdout"][:500]}

    # ========== JavaScript 분석 ==========

    def _run_npm_test(self) -> dict:
        """npm test 실행"""
        if not self._check_tool("npm"):
            return {"available": False, "message": "npm not installed"}

        pkg_json = self.path / "package.json"
        if not pkg_json.exists():
            return {"available": False, "message": "package.json not found"}

        try:
            pkg = json.loads(pkg_json.read_text())
            scripts = pkg.get("scripts", {})
            if "test" not in scripts:
                return {"available": True, "message": "no test script defined"}
        except json.JSONDecodeError:
            return {"available": False, "message": "invalid package.json"}

        result = self._run_command(["npm", "test", "--", "--passWithNoTests"], timeout=180)

        return {
            "available": True,
            "returncode": result.get("returncode", -1) if result else -1,
            "output": (result.get("stdout", "") + result.get("stderr", ""))[:1000] if result else ""
        }

    def _run_eslint(self) -> dict:
        """eslint 실행"""
        # npx eslint 또는 전역 eslint
        if not self._check_tool("npx") and not self._check_tool("eslint"):
            return {"available": False, "message": "eslint/npx not installed"}

        cmd = ["npx", "eslint", ".", "--format", "json", "--max-warnings", "0"]
        result = self._run_command(cmd, timeout=60)

        if not result:
            return {"available": True, "error": "execution failed"}

        try:
            data = json.loads(result["stdout"]) if result["stdout"] else []
            total_errors = sum(f.get("errorCount", 0) for f in data)
            total_warnings = sum(f.get("warningCount", 0) for f in data)

            return {
                "available": True,
                "errors": total_errors,
                "warnings": total_warnings,
                "files_with_issues": len([f for f in data if f.get("errorCount", 0) + f.get("warningCount", 0) > 0])
            }
        except json.JSONDecodeError:
            return {"available": True, "message": "eslint not configured or failed"}

    def _run_npm_audit(self) -> dict:
        """npm audit 실행"""
        if not self._check_tool("npm"):
            return {"available": False, "message": "npm not installed"}

        if not (self.path / "package-lock.json").exists():
            return {"available": True, "message": "package-lock.json not found"}

        result = self._run_command(["npm", "audit", "--json"], timeout=60)

        if not result:
            return {"available": True, "error": "execution failed"}

        try:
            data = json.loads(result["stdout"]) if result["stdout"] else {}
            vulnerabilities = data.get("metadata", {}).get("vulnerabilities", {})

            return {
                "available": True,
                "critical": vulnerabilities.get("critical", 0),
                "high": vulnerabilities.get("high", 0),
                "moderate": vulnerabilities.get("moderate", 0),
                "low": vulnerabilities.get("low", 0)
            }
        except json.JSONDecodeError:
            return {"available": True, "raw": result["stdout"][:500]}

    # ========== 통합 분석 ==========

    def analyze(self) -> dict:
        """전체 분석 실행"""
        result = {
            "project_path": str(self.path),
            "language": self.language,
            "analysis": {}
        }

        if self.language == "python":
            result["analysis"] = {
                "correctness": {
                    "pytest": self._run_pytest(),
                    "coverage": self._run_coverage()
                },
                "maintainability": {
                    "pylint": self._run_pylint(),
                    "radon": self._run_radon()
                },
                "security": {
                    "bandit": self._run_bandit()
                }
            }

        elif self.language in ("javascript", "typescript"):
            result["analysis"] = {
                "correctness": {
                    "npm_test": self._run_npm_test()
                },
                "maintainability": {
                    "eslint": self._run_eslint()
                },
                "security": {
                    "npm_audit": self._run_npm_audit()
                }
            }

        else:
            result["analysis"] = {
                "message": f"Language '{self.language}' not fully supported"
            }

        # 정적 패턴 분석 추가 (patterns 모듈 사용 가능 시)
        if patterns:
            result["analysis"]["patterns"] = {
                "performance": patterns.analyze_performance(self.path),
                "security": patterns.analyze_security(self.path),
                "architecture": patterns.analyze_architecture(self.path),
                "ux": patterns.analyze_ux(self.path)
            }

        return result


def main():
    """메인 함수"""
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."

    if not Path(project_path).exists():
        print(json.dumps({"error": f"Path not found: {project_path}"}))
        sys.exit(1)

    analyzer = ProjectAnalyzer(project_path)
    result = analyzer.analyze()

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
