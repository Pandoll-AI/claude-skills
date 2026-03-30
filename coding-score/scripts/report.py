#!/usr/bin/env python3
"""
코드 품질 리포트 생성 모듈
analyze.py의 JSON 출력을 받아 Markdown 리포트 생성
"""

import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime


class ScoreCalculator:
    """영역별 점수 계산기"""

    # 가중치 (합계 1.0)
    WEIGHTS = {
        "correctness": 0.20,
        "performance": 0.15,
        "security": 0.20,
        "maintainability": 0.20,
        "architecture": 0.15,
        "ux": 0.10
    }

    @staticmethod
    def calculate_correctness(analysis: Dict) -> Dict[str, Any]:
        """기능적 정확성 점수 계산"""
        score = 10.0
        details = []

        # pytest 결과
        pytest_data = analysis.get("correctness", {}).get("pytest", {})
        if pytest_data.get("available"):
            pass_rate = pytest_data.get("pass_rate", 0)
            if pass_rate == 100:
                details.append(f"테스트 100% 통과")
            elif pass_rate >= 80:
                score -= 1
                details.append(f"테스트 통과율: {pass_rate}%")
            elif pass_rate >= 50:
                score -= 3
                details.append(f"테스트 통과율 낮음: {pass_rate}%")
            else:
                score -= 5
                details.append(f"테스트 대부분 실패: {pass_rate}%")
        else:
            score -= 2
            details.append("테스트 프레임워크 미설치 또는 테스트 없음")

        # 커버리지
        coverage_data = analysis.get("correctness", {}).get("coverage", {})
        if coverage_data.get("available") and coverage_data.get("percentage"):
            cov = coverage_data["percentage"]
            if cov >= 90:
                details.append(f"커버리지 우수: {cov}%")
            elif cov >= 70:
                score -= 1
                details.append(f"커버리지: {cov}%")
            elif cov >= 50:
                score -= 2
                details.append(f"커버리지 낮음: {cov}%")
            else:
                score -= 3
                details.append(f"커버리지 매우 낮음: {cov}%")

        # npm test (JS)
        npm_test = analysis.get("correctness", {}).get("npm_test", {})
        if npm_test.get("available"):
            if npm_test.get("returncode") == 0:
                details.append("npm test 통과")
            elif npm_test.get("message") == "no test script defined":
                score -= 2
                details.append("테스트 스크립트 미정의")
            else:
                score -= 3
                details.append("npm test 실패")

        # 패턴 분석 - TODO/FIXME
        patterns = analysis.get("patterns", {}).get("architecture", {})
        todo_count = len([f for f in patterns.get("findings", []) if f.get("pattern") == "todo_fixme"])
        if todo_count > 10:
            score -= 1
            details.append(f"미완성 항목 다수: {todo_count}개 TODO/FIXME")

        return {
            "score": max(0, min(10, round(score, 1))),
            "details": details
        }

    @staticmethod
    def calculate_performance(analysis: Dict) -> Dict[str, Any]:
        """성능 점수 계산"""
        score = 10.0
        details = []

        patterns = analysis.get("patterns", {}).get("performance", {})
        findings = patterns.get("findings", [])

        # 중첩 루프
        nested_loops = [f for f in findings if "nested_loop" in f.get("pattern", "")]
        if nested_loops:
            penalty = min(3, len(nested_loops) * 0.5)
            score -= penalty
            details.append(f"중첩 루프 {len(nested_loops)}개 발견")

        # N+1 쿼리
        n_plus_one = [f for f in findings if "n_plus_one" in f.get("pattern", "")]
        if n_plus_one:
            penalty = min(3, len(n_plus_one) * 1)
            score -= penalty
            details.append(f"N+1 쿼리 패턴 {len(n_plus_one)}개 발견")

        # 루프 내 DB 저장
        loop_db = [f for f in findings if "loop_db" in f.get("pattern", "")]
        if loop_db:
            score -= min(2, len(loop_db) * 0.5)
            details.append(f"루프 내 DB 작업 {len(loop_db)}개")

        if not findings:
            details.append("성능 이슈 패턴 발견되지 않음")

        return {
            "score": max(0, min(10, round(score, 1))),
            "details": details,
            "findings": findings[:5]  # 상위 5개만
        }

    @staticmethod
    def calculate_security(analysis: Dict) -> Dict[str, Any]:
        """보안 점수 계산"""
        score = 10.0
        details = []

        # 도구 기반 분석
        bandit = analysis.get("security", {}).get("bandit", {})
        if bandit.get("available"):
            high = bandit.get("high", 0)
            medium = bandit.get("medium", 0)
            if high > 0:
                score -= min(5, high * 2)
                details.append(f"Bandit HIGH 취약점: {high}개")
            if medium > 0:
                score -= min(2, medium * 0.5)
                details.append(f"Bandit MEDIUM 취약점: {medium}개")
            if high == 0 and medium == 0:
                details.append("Bandit 검사 통과")

        npm_audit = analysis.get("security", {}).get("npm_audit", {})
        if npm_audit.get("available"):
            critical = npm_audit.get("critical", 0)
            high = npm_audit.get("high", 0)
            if critical > 0:
                score -= min(4, critical * 2)
                details.append(f"npm audit CRITICAL: {critical}개")
            if high > 0:
                score -= min(3, high * 1)
                details.append(f"npm audit HIGH: {high}개")
            if critical == 0 and high == 0:
                details.append("npm audit 통과")

        # 패턴 기반 분석
        patterns = analysis.get("patterns", {}).get("security", {})
        findings = patterns.get("findings", [])

        high_severity = [f for f in findings if f.get("severity") == "high"]
        medium_severity = [f for f in findings if f.get("severity") == "medium"]

        if high_severity:
            penalty = min(4, len(high_severity) * 1.5)
            score -= penalty
            details.append(f"고위험 보안 패턴 {len(high_severity)}개 발견")

        if medium_severity:
            penalty = min(2, len(medium_severity) * 0.5)
            score -= penalty
            details.append(f"중위험 보안 패턴 {len(medium_severity)}개 발견")

        if not findings and not bandit.get("available") and not npm_audit.get("available"):
            details.append("보안 검사 도구 미설치 (패턴 분석만 수행)")

        return {
            "score": max(0, min(10, round(score, 1))),
            "details": details,
            "findings": findings[:5]
        }

    @staticmethod
    def calculate_maintainability(analysis: Dict) -> Dict[str, Any]:
        """유지보수성 점수 계산"""
        score = 10.0
        details = []

        # pylint
        pylint = analysis.get("maintainability", {}).get("pylint", {})
        if pylint.get("available"):
            errors = pylint.get("errors", 0)
            warnings = pylint.get("warnings", 0)
            if errors > 0:
                score -= min(3, errors * 0.3)
                details.append(f"Pylint 에러: {errors}개")
            if warnings > 10:
                score -= min(2, (warnings - 10) * 0.1)
                details.append(f"Pylint 경고: {warnings}개")
            if errors == 0 and warnings <= 10:
                details.append("Pylint 검사 양호")

        # eslint
        eslint = analysis.get("maintainability", {}).get("eslint", {})
        if eslint.get("available") and eslint.get("errors") is not None:
            errors = eslint.get("errors", 0)
            warnings = eslint.get("warnings", 0)
            if errors > 0:
                score -= min(3, errors * 0.2)
                details.append(f"ESLint 에러: {errors}개")
            if warnings > 20:
                score -= min(2, (warnings - 20) * 0.05)
                details.append(f"ESLint 경고: {warnings}개")
            if errors == 0 and warnings <= 20:
                details.append("ESLint 검사 양호")

        # radon 복잡도
        radon = analysis.get("maintainability", {}).get("radon", {})
        if radon.get("available"):
            avg = radon.get("average", 0)
            max_cc = radon.get("max", 0)
            high_cc = radon.get("high_complexity_functions", 0)
            if max_cc > 20:
                score -= 2
                details.append(f"매우 높은 복잡도 함수 존재 (CC={max_cc})")
            elif max_cc > 10:
                score -= 1
                details.append(f"높은 복잡도 함수 존재 (CC={max_cc})")
            if high_cc > 5:
                score -= 1
                details.append(f"복잡도 10 초과 함수: {high_cc}개")

        # 코드 통계
        stats = analysis.get("patterns", {}).get("architecture", {}).get("stats", {})
        large_files = stats.get("large_files", [])
        if large_files:
            score -= min(1, len(large_files) * 0.2)
            details.append(f"300줄 초과 파일: {len(large_files)}개")

        return {
            "score": max(0, min(10, round(score, 1))),
            "details": details
        }

    @staticmethod
    def calculate_architecture(analysis: Dict) -> Dict[str, Any]:
        """아키텍처 점수 계산"""
        score = 10.0
        details = []

        patterns = analysis.get("patterns", {}).get("architecture", {})
        findings = patterns.get("findings", [])

        # 비RESTful URL
        non_rest = [f for f in findings if f.get("pattern") == "non_restful_url"]
        if non_rest:
            score -= min(2, len(non_rest) * 0.5)
            details.append(f"비RESTful URL 패턴: {len(non_rest)}개")

        # 매직 넘버
        magic = [f for f in findings if f.get("pattern") == "magic_number"]
        if len(magic) > 10:
            score -= 1
            details.append(f"매직 넘버 다수: {len(magic)}개")

        # 거대 함수
        god_funcs = [f for f in findings if f.get("pattern") == "god_function"]
        if god_funcs:
            score -= min(2, len(god_funcs) * 0.5)
            details.append(f"50줄 초과 함수: {len(god_funcs)}개")

        # console.log / print
        debug_logs = [f for f in findings if f.get("pattern") in ("console_log", "print_debug")]
        if len(debug_logs) > 20:
            score -= 1
            details.append(f"디버그 출력문 다수: {len(debug_logs)}개")

        if not findings:
            details.append("아키텍처 이슈 패턴 발견되지 않음")

        return {
            "score": max(0, min(10, round(score, 1))),
            "details": details
        }

    @staticmethod
    def calculate_ux(analysis: Dict) -> Dict[str, Any]:
        """UX 점수 계산"""
        score = 10.0
        details = []

        patterns = analysis.get("patterns", {}).get("ux", {})
        findings = patterns.get("findings", [])

        # 접근성
        missing_alt = [f for f in findings if f.get("pattern") == "missing_alt"]
        if missing_alt:
            score -= min(2, len(missing_alt) * 0.3)
            details.append(f"alt 속성 누락 이미지: {len(missing_alt)}개")

        # 에러 메시지
        generic_error = [f for f in findings if f.get("pattern") == "generic_error"]
        if generic_error:
            score -= min(1, len(generic_error) * 0.2)
            details.append(f"일반적 에러 메시지: {len(generic_error)}개")

        # 스택 트레이스 노출
        stack_trace = [f for f in findings if f.get("pattern") == "stack_trace_exposed"]
        if stack_trace:
            score -= min(2, len(stack_trace) * 0.5)
            details.append(f"스택 트레이스 노출 가능성: {len(stack_trace)}개")

        if not findings:
            details.append("UX 이슈 패턴 발견되지 않음")

        return {
            "score": max(0, min(10, round(score, 1))),
            "details": details
        }

    @classmethod
    def calculate_all(cls, analysis: Dict) -> Dict[str, Any]:
        """모든 영역 점수 계산"""
        scores = {
            "correctness": cls.calculate_correctness(analysis),
            "performance": cls.calculate_performance(analysis),
            "security": cls.calculate_security(analysis),
            "maintainability": cls.calculate_maintainability(analysis),
            "architecture": cls.calculate_architecture(analysis),
            "ux": cls.calculate_ux(analysis)
        }

        # 종합 점수 (가중 평균)
        total = sum(
            scores[k]["score"] * cls.WEIGHTS[k]
            for k in cls.WEIGHTS
        )

        return {
            "total_score": round(total, 1),
            "scores": scores
        }


class ReportGenerator:
    """Markdown 리포트 생성기"""

    AREA_NAMES = {
        "correctness": "기능적 정확성",
        "performance": "성능 및 효율성",
        "security": "보안 취약점",
        "maintainability": "유지보수성",
        "architecture": "아키텍처",
        "ux": "사용자 경험"
    }

    @staticmethod
    def get_status_emoji(score: float) -> str:
        """점수에 따른 상태 표시"""
        if score >= 8:
            return "우수"
        elif score >= 6:
            return "양호"
        elif score >= 4:
            return "개선 필요"
        else:
            return "미흡"

    @classmethod
    def generate(cls, data: Dict, scores: Dict) -> str:
        """Markdown 리포트 생성"""
        lines = []

        # 헤더
        lines.append("# 코드 품질 평가 리포트")
        lines.append("")
        lines.append(f"**생성 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**프로젝트 경로**: `{data.get('project_path', 'N/A')}`")
        lines.append(f"**언어**: {data.get('language', 'unknown').upper()}")
        lines.append("")

        # 종합 점수
        total = scores["total_score"]
        lines.append(f"## 종합 점수: {total}/10")
        lines.append("")

        # 점수표
        lines.append("| 영역 | 점수 | 상태 |")
        lines.append("|------|------|------|")
        for key in ["correctness", "performance", "security", "maintainability", "architecture", "ux"]:
            score = scores["scores"][key]["score"]
            status = cls.get_status_emoji(score)
            name = cls.AREA_NAMES[key]
            lines.append(f"| {name} | {score}/10 | {status} |")
        lines.append("")

        # 상세 분석
        lines.append("---")
        lines.append("")
        lines.append("## 상세 분석")
        lines.append("")

        for i, key in enumerate(["correctness", "performance", "security", "maintainability", "architecture", "ux"], 1):
            score_data = scores["scores"][key]
            name = cls.AREA_NAMES[key]
            score = score_data["score"]
            details = score_data.get("details", [])
            findings = score_data.get("findings", [])

            lines.append(f"### {i}. {name} ({score}/10)")
            lines.append("")

            if details:
                for detail in details:
                    lines.append(f"- {detail}")
                lines.append("")

            if findings:
                lines.append("**발견된 이슈:**")
                lines.append("")
                for f in findings[:5]:
                    file_loc = f"{f.get('file', '?')}:{f.get('line', '?')}"
                    desc = f.get('description', '')
                    lines.append(f"- `{file_loc}` - {desc}")
                lines.append("")

        # 개선 권고
        lines.append("---")
        lines.append("")
        lines.append("## 개선 권고")
        lines.append("")

        recommendations = cls._generate_recommendations(scores)
        if recommendations:
            for rec in recommendations:
                lines.append(f"1. {rec}")
        else:
            lines.append("현재 코드 품질이 양호합니다. 지속적인 모니터링을 권장합니다.")

        lines.append("")
        lines.append("---")
        lines.append("*이 리포트는 Coding Score Skill에 의해 자동 생성되었습니다.*")

        return "\n".join(lines)

    @classmethod
    def _generate_recommendations(cls, scores: Dict) -> list:
        """점수 기반 개선 권고 생성"""
        recs = []
        score_data = scores["scores"]

        # 점수가 낮은 영역 순으로 권고
        sorted_areas = sorted(
            score_data.items(),
            key=lambda x: x[1]["score"]
        )

        for area, data in sorted_areas[:3]:  # 상위 3개만
            if data["score"] >= 8:
                continue

            name = cls.AREA_NAMES[area]
            if area == "correctness":
                recs.append(f"**{name}**: 테스트 커버리지를 높이고 엣지 케이스 테스트를 추가하세요")
            elif area == "performance":
                recs.append(f"**{name}**: 중첩 루프와 N+1 쿼리 패턴을 최적화하세요")
            elif area == "security":
                recs.append(f"**{name}**: 발견된 보안 취약점을 즉시 수정하고 의존성을 업데이트하세요")
            elif area == "maintainability":
                recs.append(f"**{name}**: 린트 에러를 수정하고 복잡한 함수를 분리하세요")
            elif area == "architecture":
                recs.append(f"**{name}**: RESTful 규약을 준수하고 매직 넘버를 상수로 추출하세요")
            elif area == "ux":
                recs.append(f"**{name}**: 접근성 속성을 추가하고 에러 메시지를 개선하세요")

        return recs


def main():
    """메인 함수 - stdin에서 JSON 읽기 또는 파일 경로로 읽기"""
    # stdin 또는 파일에서 데이터 읽기
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    analysis = data.get("analysis", data)

    # 점수 계산
    scores = ScoreCalculator.calculate_all(analysis)

    # 리포트 생성
    report = ReportGenerator.generate(data, scores)

    print(report)


if __name__ == "__main__":
    main()
