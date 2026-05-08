"""
TC-07: End-to-End Acceptance Samples

Demonstrates complete workflows showing Task Card → Prompt → Export → Integration
"""

import json
import hashlib
from datetime import datetime


# ============================================================================
# ACCEPTANCE SAMPLE 1: 完整 Task Card 示例
# ============================================================================

SAMPLE_TASK_CARD = {
    "task_code": "AUTH-LOGIN-001",
    "task_card_version": "0.3",
    "task_type": "Feature Implementation",
    "background": [
        "系统当前缺少用户认证模块，仅支持 HTTP Basic Auth",
        "用户量增长，安全需求提升，需要强认证方案",
        "现有 API 客户端已有 1000+ 依赖，无法做 breaking changes",
        "团队已有 OAuth2 集成经验，可直接应用",
        "后续规划支持多租户，需要考虑隔离性"
    ],
    "goal": "实现用户登录认证系统，支持本地密码认证和 OAuth2，保证现有 API 完全兼容",
    "initial_state": {
        "auth_method": "HTTP Basic Auth (plaintext)",
        "database": "PostgreSQL 14, schema v2.1",
        "api_version": "v1.0",
        "active_users": 5000,
        "api_clients": 1200
    },
    "expected_behavior": {
        "primary": "用户可通过账号密码或 OAuth2 方式登录；登录成功返回 JWT token；Token 自动 1 小时刷新；现有 HTTP Basic Auth 继续有效",
        "secondary": [
            "登录接口支持 POST /auth/login?method=password|oauth2",
            "JWT token 包含 user_id, scope, expiration",
            "Token 刷新无需重新输入密码",
            "登出接口 DELETE /auth/logout 清除 token",
            "管理员可查看用户登录历史"
        ]
    },
    "acceptance_criteria": [
        "用户可通过账号密码成功登录，获得 JWT token",
        "用户可通过 OAuth2（Google/GitHub）方式登录",
        "登录后返回的 JWT token 可用于认证 API 请求",
        "Token 在 1 小时后自动过期，但可使用 refresh token 延期",
        "登录失败返回 400/401 HTTP 状态码和明确错误信息",
        "现有 HTTP Basic Auth 方式继续有效（向后兼容）",
        "登录审计日志完整记录（用户、时间、方式、IP）",
        "单元测试覆盖率 ≥90%，集成测试覆盖主要流程",
        "API 端到端响应时间 <200ms（p99）",
        "支持从 OAuth2 反向关联到本地账号"
    ],
    "relevant_files": [
        "src/auth/login.py",
        "src/auth/oauth2.py",
        "src/auth/token.py",
        "src/models/user.py",
        "src/models/session.py",
        "tests/test_auth_login.py",
        "tests/test_oauth2.py",
        "tests/integration_test_auth.py",
        "docs/auth_spec.md",
        "docs/api_v1_auth.md"
    ],
    "constraints": [
        "MUST: 不能修改现有 PostgreSQL schema（只可扩展）",
        "MUST: 密码必须使用 bcrypt 加密存储，不可逆转",
        "MUST: JWT token 采用 RS256 算法，公钥可用于验证",
        "MUST: 登录接口 p99 延迟 <200ms",
        "MUST: 不能暴露用户密码、token、或其他敏感信息",
        "SHOULD: 使用业界标准 OAuth2 库（python-social-auth 或 authlib）",
        "SHOULD: 实现登录速率限制（IP + 用户）防止暴力攻击",
        "SHOULD: 支持登录审计和可疑活动告警",
        "MUST NOT: 使用明文密码存储或可逆加密",
        "MUST NOT: 在日志中输出用户密码或 token",
        "MUST NOT: 支持 CORS 跨域认证（安全风险）"
    ],
    "test_method": {
        "strategy": "分层测试：单元测试 → 集成测试 → 端到端测试 → 性能测试",
        "steps": [
            "单元测试：测试密码哈希、token 生成、OAuth2 参数验证（pytest + unittest mock）",
            "集成测试：数据库操作、token 存储/验证、OAuth2 回调（pytest + test fixture）",
            "端到端测试：完整登录流程、刷新、退出（postman 或 behave）",
            "性能测试：100 并发登录，监测延迟和 CPU 使用率（locust）",
            "安全测试：SQL injection、密码暴力、token 篡改（OWASP Top 10）",
            "向后兼容测试：验证现有 HTTP Basic Auth 继续工作"
        ],
        "pass_signal": "所有测试通过，覆盖率 ≥90%，p99 延迟 <200ms，无 critical 安全漏洞"
    },
    "difficulty": "Large",
    "context_policy": {
        "allow_assumptions": False,
        "critical_unknowns": [
            "OAuth2 提供商选择：仅 Google + GitHub 还是需要更多？",
            "Token 过期时间：现在定为 1 小时，是否合理？",
            "支持账号绑定的复杂度如何评估？",
            "数据库迁移计划（current auth 到 new auth）"
        ],
        "handoff_readiness": "full_specification"
    },
    "suitable_experiments": [
        "workflow_comparison",  # 对比不同 prompt 生成策略
        "prompt_stability",     # 验证 prompt 生成稳定性
        "export_consistency",   # 验证 JSON/Markdown 导出一致
        "integration_load_test" # 集成加载测试
    ],
    "metadata": {
        "created_at": "2026-05-08T12:20:34+08:00",
        "created_by": "PM-Alice",
        "version_history": ["0.1-draft", "0.2-review", "0.3-approved"],
        "related_issues": ["ISSUE-42", "ISSUE-43"],
        "estimated_days": 10,
        "dependencies": ["INFRA-001 (OAuth2 setup)"]
    }
}


# ============================================================================
# ACCEPTANCE SAMPLE 2: 生成的 Prompt（Final 规范）
# ============================================================================

GENERATED_PROMPT = """# Task Prompt: AUTH-LOGIN-001

## 1. Role
You are a Senior Backend Engineer specializing in authentication systems, API design, and security.

## 2. Mission
[Feature Implementation] Implement a comprehensive user authentication system supporting both local password-based and OAuth2 login methods while maintaining 100% backward compatibility with existing HTTP Basic Auth clients.

## 3. Background
- Current system lacks proper authentication; only HTTP Basic Auth (plaintext) supported
- User growth increasing security requirements; need stronger authentication
- 1000+ existing API clients cannot tolerate breaking changes
- Team has OAuth2 integration experience; can be directly applied
- Future multi-tenancy support requires authentication isolation
- Database is PostgreSQL 14, schema v2.1

## 4. Initial State
- Auth Method: HTTP Basic Auth (plaintext)
- Database: PostgreSQL 14, schema v2.1
- API Version: v1.0
- Active Users: 5,000
- API Clients: 1,200

## 5. Target Behavior
Primary: Users can login via password or OAuth2; successful login returns JWT token; token auto-refreshes within 1 hour; existing HTTP Basic Auth remains functional.

Secondary behaviors:
- POST /auth/login?method=password|oauth2 endpoint
- JWT token contains user_id, scope, expiration
- Token refresh without password re-entry
- DELETE /auth/logout clears token
- Admin can view user login history

## 6. Hard Constraints

### MUST (Non-negotiable)
- Cannot modify existing PostgreSQL schema (extension only)
- Passwords must use bcrypt encryption (irreversible)
- JWT tokens use RS256 algorithm (asymmetric)
- Login endpoint p99 latency <200ms
- Cannot expose passwords, tokens, or sensitive data
- No plaintext password storage or reversible encryption
- Never output passwords/tokens to logs

### SHOULD (Priority)
- Use industry-standard OAuth2 libraries (python-social-auth or authlib)
- Implement rate limiting (IP + user) against brute force
- Support login audit and suspicious activity alerts

### MUST NOT (Forbidden)
- Support CORS-based authentication (security risk)

## 7. Acceptance Criteria

1. Users can login with password; receive JWT token
2. Users can login via OAuth2 (Google/GitHub)
3. Returned JWT token authenticates API requests
4. Token expires in 1 hour; can be extended via refresh token
5. Failed login returns 400/401 with clear error message
6. Existing HTTP Basic Auth remains functional (backward compatible)
7. Complete audit logs: user, time, method, IP
8. Unit test coverage ≥90%; integration tests cover main flows
9. API p99 response time <200ms
10. Support reverse-linking OAuth2 to local accounts

## 8. Execution Plan Guardrails

**Difficulty: Large**

Strongly recommend phased execution:

**Phase 1 (Days 1-3): Core Authentication System**
- Design database schema extension (users, sessions, oauth_links)
- Implement password hashing (bcrypt) and JWT generation
- Create login/logout endpoints with HTTP Basic Auth
- Risks: JWT implementation errors, token expiration edge cases

**Phase 2 (Days 4-7): OAuth2 Integration**
- Integrate OAuth2 providers (Google, GitHub)
- Implement account linking logic
- Create session management
- Risks: Provider API changes, token revocation, scope misalignment

**Phase 3 (Days 8-10): Testing & Hardening**
- Complete test coverage (unit + integration + E2E)
- Performance testing (latency, throughput)
- Security review (OWASP Top 10)
- Deployment & rollback planning

## 9. Test Method

Strategy: Layered testing approach

Steps:
1. Unit tests: password hashing, token generation, OAuth2 validation
2. Integration tests: database operations, token storage/validation, OAuth2 callbacks
3. E2E tests: complete login flow, refresh, logout
4. Performance tests: 100 concurrent logins, latency monitoring
5. Security tests: SQL injection, brute force, token tampering
6. Backward compatibility: verify existing HTTP Basic Auth still works

Pass Signal: All tests pass, coverage ≥90%, p99 latency <200ms, no critical security issues

## 10. Deliverables

Core files:
- src/auth/login.py (login logic)
- src/auth/oauth2.py (OAuth2 integration)
- src/auth/token.py (JWT token management)
- src/models/user.py (user model)
- src/models/session.py (session model)

Testing:
- tests/test_auth_login.py
- tests/test_oauth2.py
- tests/integration_test_auth.py

Documentation:
- docs/auth_spec.md (specification)
- docs/api_v1_auth.md (API reference)

---

**Context Policy:**
- No assumptions allowed; critical unknowns must be clarified:
  - OAuth2 providers: Google + GitHub only, or more?
  - Token expiration: 1 hour appropriate?
  - Account linking complexity assessment?
  - Migration plan (old auth to new auth)?

**Dependencies:** INFRA-001 (OAuth2 setup) must complete first
**Estimated Duration:** 10 days
"""


# ============================================================================
# ACCEPTANCE SAMPLE 3: JSON 导出示例
# ============================================================================

EXPORTED_JSON = {
    "task_code": "AUTH-LOGIN-001",
    "task_card_version": "0.3",
    "task_type": "Feature Implementation",
    "goal": "实现用户登录认证系统",
    "background": SAMPLE_TASK_CARD["background"],
    "initial_state": SAMPLE_TASK_CARD["initial_state"],
    "expected_behavior": SAMPLE_TASK_CARD["expected_behavior"],
    "acceptance_criteria": SAMPLE_TASK_CARD["acceptance_criteria"],
    "relevant_files": SAMPLE_TASK_CARD["relevant_files"],
    "constraints": SAMPLE_TASK_CARD["constraints"],
    "test_method": SAMPLE_TASK_CARD["test_method"],
    "difficulty": SAMPLE_TASK_CARD["difficulty"],
    "context_policy": SAMPLE_TASK_CARD["context_policy"],
    "suitable_experiments": SAMPLE_TASK_CARD["suitable_experiments"],
    "metadata": SAMPLE_TASK_CARD["metadata"],
    "export_metadata": {
        "exported_at": datetime.now().isoformat(),
        "exported_by": "system",
        "format_version": "1.0",
        "checksum": hashlib.sha256(
            json.dumps(SAMPLE_TASK_CARD, sort_keys=True).encode()
        ).hexdigest()
    }
}


# ============================================================================
# ACCEPTANCE SAMPLE 4: Workflow Execution Record
# ============================================================================

WORKFLOW_EXECUTION_RECORD = {
    "task_code": "AUTH-LOGIN-001",
    "task_card_version": "0.3",
    "record_type": "workflow_execution",
    "created_at": datetime.now().isoformat(),
    "agent_or_person": "GPT-4-Agent-v1.2",
    "status": "completed",
    "task_card_checksum": hashlib.sha256(
        json.dumps(SAMPLE_TASK_CARD, sort_keys=True).encode()
    ).hexdigest(),
    "verification_checklist": [
        "task_code: OK",
        "task_card_version: OK",
        "task_type: OK",
        "background: OK (5 items)",
        "goal: OK",
        "initial_state: OK",
        "expected_behavior: OK",
        "acceptance_criteria: OK (10 items)",
        "relevant_files: OK (10 files)",
        "constraints: OK (11 items)",
        "test_method: OK",
        "difficulty: OK (Large)"
    ],
    # Workflow specific
    "workflow_id": "WF-2026-0508-001",
    "execution_id": "EXE-AUTH-LOGIN-001-001",
    "prompt_strategy": "final",
    "generated_prompt": GENERATED_PROMPT[:500] + "...",  # 截断以简洁
    "agent_version": "GPT-4-Agent-v1.2",
    "start_time": "2026-05-08T10:00:00+08:00",
    "end_time": "2026-05-08T12:15:00+08:00",
    "duration_seconds": 8100,
    "output_path": "outputs/AUTH-LOGIN-001/implementation/",
    "result_summary": "核心认证系统完成，密码登录和 OAuth2 集成成功；所有验收标准通过；测试覆盖率 93%；p99 延迟 145ms",
    "success": True,
    "error_message": None,
    "artifacts": {
        "code_files": 8,
        "test_files": 3,
        "doc_files": 2,
        "total_lines": 2450,
        "test_coverage": 0.93,
        "p99_latency_ms": 145
    }
}


# ============================================================================
# ACCEPTANCE SAMPLE 5: Handoff Record
# ============================================================================

HANDOFF_RECORD = {
    "task_code": "AUTH-LOGIN-001",
    "task_card_version": "0.3",
    "record_type": "handoff",
    "created_at": datetime.now().isoformat(),
    "agent_or_person": "GPT-4-Agent-v1.2",
    "status": "completed",
    "task_card_checksum": WORKFLOW_EXECUTION_RECORD["task_card_checksum"],
    "verification_checklist": WORKFLOW_EXECUTION_RECORD["verification_checklist"],
    # Handoff specific
    "from_entity": "GPT-4-Agent",
    "to_entity": "Senior Code Reviewer (Bob)",
    "handoff_reason": "quality_review",
    "exported_format": "both",
    "exported_files": {
        "json": "AUTH-LOGIN-001.task_card.json",
        "markdown": "AUTH-LOGIN-001.task_card.md"
    },
    "handoff_time": "2026-05-08T12:30:00+08:00",
    "decision": "approved",
    "decision_time": "2026-05-08T14:45:00+08:00",
    "decision_reason": "实现完整，测试覆盖充分（93%），安全检查通过，无关键缺陷。代码风格良好，注释清晰。",
    "notes": "建议：1) 添加审计日志中的 logout 事件记录；2) 考虑集成 IP 白名单以增强安全性；3) OAuth2 token 过期时间可考虑设置为 2 小时（当前 1 小时较短）。",
    "reviewer_name": "Bob",
    "reviewer_email": "bob@example.com"
}


# ============================================================================
# ACCEPTANCE SAMPLE 6: Experiment Record
# ============================================================================

EXPERIMENT_RECORD = {
    "task_code": "AUTH-LOGIN-001",
    "task_card_version": "0.3",
    "record_type": "experiment",
    "created_at": datetime.now().isoformat(),
    "agent_or_person": "Test Framework v2.0",
    "status": "completed",
    "task_card_checksum": WORKFLOW_EXECUTION_RECORD["task_card_checksum"],
    "verification_checklist": WORKFLOW_EXECUTION_RECORD["verification_checklist"],
    # Experiment specific
    "experiment_type": "prompt_stability",
    "experiment_id": "EXP-AUTH-LOGIN-001-STABILITY-001",
    "hypothesis": "Final Prompt 规范生成的 Prompt 具有高度稳定性，100 次生成的输出结构和关键内容一致，满足 workflow/handoff 的可复现性要求",
    "start_time": "2026-05-08T15:00:00+08:00",
    "end_time": "2026-05-08T15:30:00+08:00",
    "iterations": 100,
    "metrics": {
        "consistency_score": 0.98,
        "pass_rate": 1.0,
        "avg_prompt_length": 1847,
        "std_prompt_length": 12,
        "section_order_consistency": 1.0,
        "constraint_expression_consistency": 0.98,
        "acceptance_criteria_consistency": 1.0
    },
    "findings": [
        "100 次生成中，99 次输出完全相同（99% 一致性）",
        "1 次偏差源于 metadata.created_at 时间戳差异（预期行为）",
        "所有 10 个 section 的顺序始终一致",
        "约束分层（MUST/SHOULD/MUST NOT）表达一致",
        "验收标准编号和顺序完全一致",
        "平均 prompt 长度 1847 字符，标准差 12 字符（非常稳定）"
    ],
    "conclusion": "假设验证成功。Final Prompt 规范生成的 Prompt 具有高度稳定性和可复现性，完全满足 workflow/handoff/实验记录的要求。可以放心用于生产。",
    "next_steps": [
        "集成到生产 workflow 系统",
        "建立 prompt 稳定性监控告警",
        "计划后续 A/B 对比实验（Final vs Candidate-B）"
    ],
    "statistical_summary": {
        "mean_consistency": 0.98,
        "min_consistency": 0.96,
        "max_consistency": 1.0,
        "confidence_level": 0.99
    }
}


# ============================================================================
# 输出示例
# ============================================================================

def print_sample_1():
    print("=" * 80)
    print("ACCEPTANCE SAMPLE 1: 完整 Task Card")
    print("=" * 80)
    print(json.dumps(SAMPLE_TASK_CARD, ensure_ascii=False, indent=2)[:1000])
    print("... (truncated)")
    print()


def print_sample_2():
    print("=" * 80)
    print("ACCEPTANCE SAMPLE 2: 生成的 Prompt（Final 规范）")
    print("=" * 80)
    print(GENERATED_PROMPT[:1200])
    print("... (truncated)")
    print()


def print_sample_3():
    print("=" * 80)
    print("ACCEPTANCE SAMPLE 3: JSON 导出")
    print("=" * 80)
    print(json.dumps(EXPORTED_JSON, ensure_ascii=False, indent=2)[:1000])
    print("... (truncated)")
    print()


def print_sample_4():
    print("=" * 80)
    print("ACCEPTANCE SAMPLE 4: Workflow Execution Record")
    print("=" * 80)
    print(json.dumps(WORKFLOW_EXECUTION_RECORD, ensure_ascii=False, indent=2)[:1200])
    print("... (truncated)")
    print()


def print_sample_5():
    print("=" * 80)
    print("ACCEPTANCE SAMPLE 5: Handoff Record")
    print("=" * 80)
    print(json.dumps(HANDOFF_RECORD, ensure_ascii=False, indent=2)[:1000])
    print("... (truncated)")
    print()


def print_sample_6():
    print("=" * 80)
    print("ACCEPTANCE SAMPLE 6: Experiment Record")
    print("=" * 80)
    print(json.dumps(EXPERIMENT_RECORD, ensure_ascii=False, indent=2)[:1200])
    print("... (truncated)")
    print()


if __name__ == "__main__":
    print("\n[INFO] Task Card v0.3 End-to-End Acceptance Samples\n")
    
    print_sample_1()
    print_sample_2()
    print_sample_3()
    print_sample_4()
    print_sample_5()
    print_sample_6()
    
    # 导出完整的样例到 JSON 文件
    all_samples = {
        "sample_task_card": SAMPLE_TASK_CARD,
        "generated_prompt": GENERATED_PROMPT,
        "exported_json": EXPORTED_JSON,
        "workflow_execution_record": WORKFLOW_EXECUTION_RECORD,
        "handoff_record": HANDOFF_RECORD,
        "experiment_record": EXPERIMENT_RECORD,
        "summary": {
            "total_samples": 6,
            "task_card_fields": len(SAMPLE_TASK_CARD),
            "prompt_length": len(GENERATED_PROMPT),
            "checksum": WORKFLOW_EXECUTION_RECORD["task_card_checksum"]
        }
    }
    
    with open("acceptance_samples_complete.json", "w", encoding="utf-8") as f:
        json.dump(all_samples, f, ensure_ascii=False, indent=2)
    
    print("\n[OK] All samples printed; complete samples exported to acceptance_samples_complete.json\n")
