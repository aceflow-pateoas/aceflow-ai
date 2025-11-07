# AceFlow + Cline Integration Rules v3.0

> 🎯 **Core Purpose**: Enhance Cline AI Agent with AceFlow workflow management
> 📋 **Based on**: aceflow-spec_v3.0.md (Complete Specification)
> 🔄 **Focus**: AI-driven workflow with intelligent mode selection and cross-session continuity

---

## 🧠 Core Integration Principles

### 1. AceFlow Detection and Activation

**Auto-detect AceFlow projects by checking:**
```bash
# Priority check sequence
1. Check for .aceflow/config.yaml
2. Check for .aceflow/state.json
3. Check for aceflow_result/ directory
4. If all present → AceFlow project detected
```

**Activation triggers:**
- User mentions: "aceflow", "workflow", "start iteration", "continue development"
- Task descriptions: "implement feature", "fix bug", "develop module"
- Status inquiries: "what's the status", "where are we", "current progress"
- Workflow commands: "move to next stage", "complete current stage"

**Auto-activation behavior:**
```markdown
🔄 **AceFlow Project Detected**

**Current Status**:
- Mode: {minimal|standard|complete|smart}
- Stage: {current_stage}
- Progress: {percentage}%
- Iteration: {iteration_id}

**Available Actions**:
1. Continue current stage
2. Move to next stage
3. View detailed status
4. Adjust workflow mode

What would you like to do?
```

---

## 🎯 Intelligent Workflow Mode Selection

### Smart Mode Analysis (Recommended Default)

When user describes a task, **always** perform Smart Mode analysis:

```markdown
## 🧠 AceFlow Smart Mode Analysis

### Task Analysis
**Description**: {user_task_description}

### Complexity Evaluation (Score: {0-100})
- **Technical Complexity**: {score}/25 - {reasoning}
- **Business Complexity**: {score}/25 - {reasoning}
- **Team Capability**: {score}/20 - {reasoning}
- **Time Constraint**: {score}/15 - {reasoning}
- **Quality Requirement**: {score}/15 - {reasoning}

**Total Complexity Score**: {total}/100

### Mode Recommendation

**Recommended Mode**: {minimal|standard|complete}
**Confidence**: {percentage}%

**Reasoning**:
- {reason_1}
- {reason_2}
- {reason_3}

**Workflow Path**: {specific_stages}
**Estimated Duration**: {time_estimate}

**Alternative Options**:
- If time is critical → {alternative_mode_1}
- If quality is critical → {alternative_mode_2}

Shall I initialize **{recommended_mode}** mode for this task?
```

### Mode-Specific Behavior

#### 🚀 Minimal Mode (P→D→R)

**适用场景**:
- 1-3人团队
- 快速原型/Bug修复
- 0.5-2天周期
- 复杂度 ≤ 30

**执行行为**:
```markdown
🚀 **Minimal Mode Active**

**Current Stage**: {P|D|R}

**P - Planning** (2-4h):
- Quick analysis and simple design
- Output: aceflow_result/{iter}/minimal/planning/

**D - Development** (4-12h):
- Rapid coding with immediate testing
- Output: aceflow_result/{iter}/minimal/development/

**R - Review** (1-2h):
- Basic validation and simple documentation
- Output: aceflow_result/{iter}/minimal/review/

**Progress**: [{stage}] {percentage}%
**Next Action**: {recommended_action}
```

#### ⚙️ Standard Mode (P1→P2→D1→D2→R1)

**适用场景**:
- 3-10人团队
- 常规功能开发
- 3-7天周期
- 复杂度 31-60

**执行行为**:
```markdown
⚙️ **Standard Mode Active**

**Current Stage**: {P1|P2|D1|D2|R1}

**Stage Overview**:
- ✅ P1: Requirements Analysis - Detailed requirements & user stories
- ✅ P2: Technical Design - Architecture & API design
- 🔄 D1: Implementation - Core feature development
- ⏳ D2: Testing - Comprehensive testing & validation
- ⏳ R1: Release - Code review & deployment prep

**Current Focus**: {current_stage_name}
**Progress**: {stage_percentage}% of stage, {overall_percentage}% overall
**Output Path**: aceflow_result/{iter}/standard/{stage}/

**Key Deliverables**:
- {deliverable_1}
- {deliverable_2}

**Next Action**: {recommended_action}
```

#### 🏗️ Complete Mode (S1→S2→...→S8)

**适用场景**:
- 10+人团队
- 大型关键系统
- 1-4周周期
- 复杂度 > 60

**执行行为**:
```markdown
🏗️ **Complete Mode Active**

**8-Stage Enterprise Workflow**

**Stage Progress**:
- ✅ S1: User Stories (100%)
- ✅ S2: Task Breakdown (100%)
- ✅ S3: Test Design (100%)
- 🔄 S4: Implementation (65%) ← Current
- 🔄 S5: Testing (循环中)
- ⏳ S6: Code Review
- ⏳ S7: Demo & Feedback
- ⏳ S8: Summary & Archive

**Current Task**: {task_id} - {task_name}
**Overall Progress**: {percentage}%

**Quality Gates**:
- DG1 (After S3): {PASSED|PENDING}
- DG2 (After S5): {PASSED|PENDING}
- DG3 (After S7): {PENDING}

**S4-S5 Development Loop**:
```python
while has_pending_tasks():
    # S4: Implement task
    implement_task(current_task)

    # S5: Test and validate
    if tests_pass():
        mark_completed()
        next_task()
    else:
        fix_issues()
        retest()
```

**Output Path**: aceflow_result/{iter}/{stage_folder}/
**Next Action**: {recommended_action}
```

---

## 📝 Cross-Session Memory Management

### Memory Storage Strategy

**Always store these types of information:**

```markdown
## Memory Categories

### 1. Requirements Memory (REQ-{id}.md)
**When to store**:
- User provides new requirements
- Requirements change or clarification
- Acceptance criteria defined

**Format**:
```markdown
# REQ-{timestamp}-{hash}

## Original Requirement
{user_requirement}

## Refined Requirement
{clarified_requirement}

## Acceptance Criteria
- [ ] {criterion_1}
- [ ] {criterion_2}

## Related User Stories
- US-001, US-002

## Tags
{feature_type}, {priority}, {module}
```

### 2. Decision Memory (DEC-{id}.md)
**When to store**:
- Architecture decisions made
- Technology choices
- Design pattern selections
- Trade-off decisions

**Format**:
```markdown
# DEC-{timestamp}-{hash}

## Context
{what_decision_was_needed}

## Options Considered
1. {option_1}: {pros_and_cons}
2. {option_2}: {pros_and_cons}

## Decision
Selected: {chosen_option}

## Reasoning
{detailed_reasoning}

## Impact
- {impact_1}
- {impact_2}

## Tags
{architecture}, {design}, {priority}
```

### 3. Pattern Memory (PATTERN-{id}.md)
**When to store**:
- Reusable code patterns created
- Problem-solving approaches
- Optimization techniques

### 4. Issue Memory (ISSUE-{id}.md)
**When to store**:
- Bugs encountered and fixed
- Problems and solutions
- Workarounds applied

### 5. Learning Memory (LEARN-{id}.md)
**When to store**:
- Lessons learned from iteration
- Best practices identified
- Things to avoid next time

### Memory Recall Before Actions

**Before starting any stage, ALWAYS recall relevant memories:**

```markdown
## 🧠 Memory Recall

**Searching memory pool for**: {current_stage_context}

**Found Relevant Memories**:

📋 **Requirements** (3 items):
- REQ-001: User authentication requirements
- REQ-005: Password policy requirements
- REQ-012: Session management requirements

🎯 **Decisions** (2 items):
- DEC-003: Use JWT for authentication (chosen over session cookies)
- DEC-007: Implement bcrypt for password hashing

🔧 **Patterns** (1 item):
- PATTERN-002: Authentication middleware pattern

⚠️ **Known Issues** (1 item):
- ISSUE-004: Session timeout edge case (resolved)

💡 **Lessons Learned** (1 item):
- LEARN-001: Always validate token expiry before use

**Applying memories to current task...**
```

---

## 🚦 Decision Gates (Quality Gates)

### Gate Evaluation Protocol

**Before advancing to next major phase:**

```markdown
## 🚦 Decision Gate Evaluation: DG{number}

### Gate Information
**Current Stage**: {stage_name}
**Next Stage**: {next_stage_name}
**Gate Type**: {DG1|DG2|DG3}

### Completion Criteria Check

#### DG1: Development Readiness (After S3)
- [ ] All user stories have acceptance criteria
- [ ] Tasks broken down to ≤8 hours each
- [ ] Test cases cover ≥80% scenarios
- [ ] Dependencies identified and resolved
- [ ] Technical risks assessed

**Score**: {score}/5

#### DG2: Implementation Quality (After S5 each task)
- [ ] All tests passing
- [ ] Code coverage ≥80%
- [ ] Code review completed
- [ ] Performance benchmarks met
- [ ] Documentation updated

**Score**: {score}/5

#### DG3: Release Readiness (After S7)
- [ ] User acceptance testing passed
- [ ] User satisfaction ≥8/10
- [ ] All critical issues resolved
- [ ] Deployment plan reviewed
- [ ] Rollback plan tested

**Score**: {score}/5

### Quality Metrics
- **Code Coverage**: {percentage}%
- **Test Pass Rate**: {percentage}%
- **Code Quality Score**: {score}/10
- **Documentation Completeness**: {percentage}%

### Decision
**Result**: {PASS|REVIEW_NEEDED|BLOCK}

**Reasoning**: {detailed_reasoning}

### Actions Required
{if BLOCK or REVIEW_NEEDED}:
1. {required_action_1}
2. {required_action_2}

{if PASS}:
✅ Ready to proceed to {next_stage}

Shall I proceed?
```

---

## 📁 Output Management Standards

### Standardized Directory Structure

```
project_root/
├── aceflow_result/              # All AceFlow outputs
│   ├── iter_001/                # Iteration 1
│   │   ├── minimal/             # For Minimal mode
│   │   │   ├── planning/
│   │   │   ├── development/
│   │   │   └── review/
│   │   ├── standard/            # For Standard mode
│   │   │   ├── P1_requirements/
│   │   │   ├── P2_design/
│   │   │   ├── D1_implementation/
│   │   │   ├── D2_testing/
│   │   │   └── R1_release/
│   │   └── S1_user_stories/     # For Complete mode
│   │       S2_tasks/
│   │       S3_testing/
│   │       S4_implementation/
│   │       S5_testing/
│   │       S6_review/
│   │       S7_demo/
│   │       S8_summary/
│   └── iter_002/                # Iteration 2
└── .aceflow/                    # AceFlow configuration
    ├── config.yaml
    ├── state.json
    ├── templates/
    └── memory/
```

### Output File Naming Conventions

```markdown
## File Naming Standards

### Document Files
- Requirements: `{stage}_requirements_{topic}.md`
- Design: `{stage}_design_{component}.md`
- Implementation: `{stage}_impl_{task_id}.md`
- Testing: `{stage}_test_{task_id}.md`
- Review: `{stage}_review_{aspect}.md`

### Examples
- `P1_requirements_authentication.md`
- `P2_design_api_specification.md`
- `D1_impl_TASK-001_user_registration.md`
- `D2_test_TASK-001_results.md`
- `R1_review_code_quality.md`

### Metadata in Headers
Every output file should start with:
```markdown
---
iteration: {iteration_id}
stage: {stage_id}
mode: {minimal|standard|complete}
created: {timestamp}
author: Cline AI + Human
status: {draft|review|final}
---
```
```

---

## 🔧 Helper Scripts Integration

### Available Commands

```bash
# 1. Initialize new AceFlow project
python .aceflow/scripts/init.py --mode {minimal|standard|complete|smart}

# 2. Check current status
python .aceflow/scripts/state_manager.py status --detailed

# 3. Update progress
python .aceflow/scripts/state_manager.py update {stage_id} {percentage}

# 4. Complete stage
python .aceflow/scripts/state_manager.py complete {stage_id}

# 5. Analyze iteration
python .aceflow/scripts/analyze.py --iteration {iteration_id}

# 6. Fix memory/state issues
python .aceflow/scripts/fix_memory.py --validate --repair
```

### When to Use Scripts

```markdown
## Script Usage Triggers

**Use init.py when**:
- Starting a new iteration
- User explicitly requests initialization
- No existing AceFlow state found

**Use state_manager.py when**:
- Checking project status
- Updating stage progress
- Completing stages
- User asks "what's the status"

**Use analyze.py when**:
- Iteration completed
- User requests analysis
- Generating reports
- End of S8/R stage

**Use fix_memory.py when**:
- State seems inconsistent
- Memory recall fails
- User reports workflow issues
```

---

## 🎪 Conversation Flow Examples

### Example 1: New Feature with Smart Mode

```
User: I need to add a user management system

Cline: 🧠 **AceFlow Smart Mode Analysis**

**Task**: Add user management system

**Complexity Evaluation**:
- Technical: 15/25 (Standard CRUD + auth)
- Business: 18/25 (User roles, permissions logic)
- Team: 16/20 (Assuming 5-person team)
- Time: 10/15 (No urgent deadline mentioned)
- Quality: 12/15 (Standard quality expected)

**Total Score**: 71/100

**Recommendation**: ⚙️ **Standard Mode**
**Confidence**: 88%

**Reasoning**:
- Medium complexity user management
- Requires proper design (auth, roles)
- Testing critical for security
- Standard mode provides good balance

**Workflow Path**: P1 → P2 → D1 → D2 → R1
**Estimated Duration**: 4-6 days

**Alternative**: If timeline < 3 days, consider Minimal mode

Shall I initialize Standard Mode and start P1 (Requirements Analysis)?
```

### Example 2: Continue Existing Workflow

```
User: continue

Cline: 🔄 **Resuming AceFlow Workflow**

**Current Status**:
- Mode: Standard
- Stage: D1 (Implementation)
- Progress: 65% of stage, 52% overall
- Iteration: iter_001

**Stage D1 Progress**:
- ✅ User model implemented
- ✅ CRUD operations complete
- 🔄 Role-based access control (in progress)
- ⏳ Audit logging (pending)
- ⏳ Unit tests (pending)

**Memory Recall**:
📋 Applied design patterns from P2
🎯 Using JWT authentication (DEC-003)
⚠️ Remember: Hash passwords with bcrypt (LEARN-001)

**Next Actions**:
1. Complete RBAC middleware
2. Implement audit logging
3. Write unit tests

**Current Output**: `aceflow_result/iter_001/standard/D1_implementation/`

Ready to continue with RBAC implementation?
```

### Example 3: Problem Detection and Resolution

```
User: The tests are failing

Cline: 🚨 **Issue Detected During AceFlow D2 Stage**

**Context**:
- Stage: D2 (Testing)
- Affected: User registration tests
- Impact: Blocks D2 completion

**Memory Recall**:
⚠️ ISSUE-004: Similar test failure in iter_prev
💡 Solution: Token expiry validation was missing

**Analysis**:
1. Running test suite to identify failures...
2. Checking recent code changes...
3. Comparing with test design (S3)...

**Findings**:
- 3 tests failing in `test_user_auth.py`
- Root cause: JWT token validation logic
- Quick fix available (15 min estimate)

**Recommended Action**:
1. Document issue: `ISSUE-{new_id}.md`
2. Apply fix based on previous learning
3. Rerun tests
4. Update DG2 gate status
5. Continue D2 if tests pass

**Output**: `aceflow_result/iter_001/standard/D2_testing/issues/`

Shall I proceed with the fix?
```

### Example 4: Decision Gate Block

```
User: move to next stage

Cline: 🚦 **Decision Gate DG2 Evaluation**

**Attempting to advance**: S5 → S6

**Completion Criteria Check**:
- ✅ All tests passing (100%)
- ❌ Code coverage 72% (Target: ≥80%)
- ✅ Code review completed
- ⚠️ Performance: 2 benchmarks not met
- ✅ Documentation updated

**Score**: 3.5/5

**Quality Metrics**:
- Code Coverage: 72% ❌
- Test Pass Rate: 100% ✅
- Code Quality Score: 8.5/10 ✅
- Performance: 80% met ⚠️

**Decision**: 🛑 **REVIEW_NEEDED**

**Reasoning**:
- Code coverage below threshold (72% < 80%)
- 2 performance benchmarks need attention
- Must meet quality gates before S6

**Required Actions**:
1. Add tests to increase coverage to ≥80%
2. Optimize slow API endpoints:
   - GET /api/users (current: 450ms, target: <200ms)
   - POST /api/auth/login (current: 320ms, target: <200ms)

**Estimated Time**: 2-3 hours

Would you like me to:
A) Add missing tests and optimize performance
B) Request gate override (not recommended)
C) Review detailed metrics first
```

### Example 5: Smart Mode Adjustment

```
User: This is taking too long, can we simplify?

Cline: 🔄 **AceFlow Smart Mode Adjustment**

**Current Situation**:
- Mode: Standard (P1→P2→D1→D2→R1)
- Current Stage: D1 (Day 3 of estimated 1-2 days)
- Progress: 40%
- Issue: Timeline pressure detected

**Adjustment Analysis**:
- Original estimate: 5-6 days
- Actual pace: Likely 8-9 days
- User constraint: Faster delivery needed

**Recommendation**: Switch to **Minimal Mode**

**What Changes**:
- ❌ Skip detailed design documents (already have P2)
- ✅ Keep core implementation (D1 → D)
- ❌ Reduce testing depth (D2 → part of D)
- ✅ Basic review only (R1 → R)

**Trade-offs**:
- ✅ Faster: 2-3 days remaining
- ❌ Less documentation
- ❌ Reduced test coverage (aim for 70% vs 80%)

**New Path**: Complete D1 → Quick D+R → Done
**Risk**: Lower quality assurance

**Alternative**: Keep Standard but:
- Focus on MVP features only
- Defer nice-to-have items
- Parallel testing

Which approach do you prefer?
```

---

## 🎯 Key Success Factors

### Critical Rules for Cline

1. **Always Check State First**
   - Read `.aceflow/state.json` before responding
   - Understand current mode and stage
   - Load relevant memories

2. **Follow Spec Religiously**
   - Respect stage boundaries
   - Honor decision gates
   - Use correct output paths

3. **Maintain Continuity**
   - Store important decisions in memory
   - Reference previous iterations
   - Learn from past issues

4. **Be Context-Aware**
   - Tailor responses to current stage
   - Provide stage-appropriate suggestions
   - Respect workflow mode constraints

5. **Smart Mode First**
   - Default to Smart mode analysis
   - Recommend appropriate workflow
   - Adjust dynamically if needed

6. **Quality Gates Matter**
   - Don't skip gate evaluations
   - Block progression if criteria not met
   - Document gate decisions

7. **Output Standards**
   - Use correct directory structure
   - Follow naming conventions
   - Include metadata headers

### Common Pitfalls to Avoid

❌ **Don't**:
- Skip state checks
- Ignore decision gates
- Mix output locations
- Forget to update state
- Lose cross-session context
- Override gates without reason

✅ **Do**:
- Check state before every response
- Evaluate gates thoroughly
- Organize outputs properly
- Update state after actions
- Recall relevant memories
- Document important decisions

---

## 📚 Quick Reference

### Mode Selection Criteria

```
Complexity Score → Mode Recommendation
≤ 30          → Minimal
31-60         → Standard
> 60          → Complete
Uncertain     → Smart (let AI decide)
```

### Stage Codes Quick Reference

**Minimal**: P, D, R
**Standard**: P1, P2, D1, D2, R1
**Complete**: S1, S2, S3, S4, S5, S6, S7, S8

### Decision Gates

- **DG1**: After S3 (Complete mode) - Development readiness
- **DG2**: After each S5 (Complete mode) - Task completion check
- **DG3**: After S7 (Complete mode) - Release readiness

### Memory Types

- **REQ**: Requirements
- **DEC**: Decisions
- **PATTERN**: Code patterns
- **ISSUE**: Problems/solutions
- **LEARN**: Lessons learned

---

**Remember**: AceFlow enhances Cline by adding structured, intelligent workflow management. The goal is seamless integration that makes development more organized, continuous, and quality-driven across sessions while leveraging AI's decision-making capabilities.

**Version**: 3.0.0
**Last Updated**: 2025-11-06
**Based on**: aceflow-spec_v3.0.md
