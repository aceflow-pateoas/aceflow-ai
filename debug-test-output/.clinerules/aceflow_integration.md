# AceFlow + AI Agent Integration Rules v3.0

> 🎯 **Core Purpose**: Enhance AI Agent with AceFlow workflow management  
> 📋 **Based on**: aceflow-spec_v3.0.md (Core Specification)  
> 🔄 **Focus**: Flow-driven development with cross-session continuity
> 📁 **项目**: debug-test-project
> 🔄 **模式**: STANDARD

## 📖 规范依据

本AI Agent的工作基于以下官方规范：
- **AceFlow v3.0 规范**: 详见 `aceflow/aceflow-spec_v3.0.md`
- **SPEC核心摘要**: 详见 `.clinerules/spec_summary.md`
- **核心原则**: 严格遵循SPEC中定义的工作流程和质量标准
- **冲突处理**: 如有疑问，以官方SPEC为准

## 🔄 工作原则

1. **规范优先**: 所有工作必须符合AceFlow v3.0规范
2. **SPEC查阅**: 遇到不确定的情况时，主动查阅SPEC文档
3. **标准执行**: 按照SPEC定义的标准执行每个阶段
4. **状态一致性**: 确保所有操作符合SPEC定义的状态管理规则
5. **质量门控**: 严格执行SPEC中定义的决策门检查

## 🧠 Core Integration Principles

### 1. AceFlow Detection and Activation

**Auto-detect AceFlow projects by checking:**
```bash
# Check if current directory has AceFlow structure
if [ -f ".aceflow/state/project_state.json" ]; then
    echo "AceFlow project detected"
    # Load current state and continue workflow
fi
```

**Activation triggers:**
- User mentions: "start", "continue", "workflow", "aceflow"
- Task descriptions matching development patterns
- Project status inquiries
- Quality gate evaluations

### 2. Workflow State Management

**Always check current state before responding:**
```markdown
## Current AceFlow Status Check
1. Read `.aceflow/state/project_state.json`
2. Identify current stage (S1-S8 or P→D→R)
3. Check progress percentage
4. Review pending deliverables
5. Load relevant memories from `.aceflow/memory/`
```

**State-aware response format:**
```markdown
🔄 **AceFlow Status**: Currently in {current_stage} ({progress}% complete)
📋 **Next Action**: {recommended_next_step}
📁 **Output Location**: aceflow-result/{iteration_id}/{stage_folder}/
```

## 🎯 Workflow Mode Integration

### Smart Mode Selection

When user describes a task, automatically analyze and recommend:

```markdown
## Task Analysis for AceFlow Mode Selection

**Task**: {user_description}

**Analysis**:
- Complexity: {low|medium|high}
- Team Size: {estimated_from_context}
- Urgency: {normal|high|emergency}
- Type: {feature|bug_fix|refactor|emergency}

**Recommended Mode**: {minimal|standard|complete|emergency}
**Reasoning**: {explanation_based_on_aceflow_spec}

**Workflow Path**: {specific_stages_sequence}

Shall I initialize this workflow mode?
```

### Mode-Specific Behavior

#### Minimal Mode (P→D→R)
```markdown
🚀 **Minimal Mode Active**
- **P (Planning)**: Quick analysis, simple design (2-4 hours)
- **D (Development)**: Rapid coding with immediate testing (4-12 hours)  
- **R (Review)**: Basic validation and documentation (1-2 hours)

**Current Stage**: {current_stage}
**Output**: aceflow-result/{iteration_id}/minimal/{stage}/
```

#### Standard Mode (P1→P2→D1→D2→R1)
```markdown
🏢 **Standard Mode Active**
- **P1**: Requirements analysis with user stories
- **P2**: Technical design and architecture
- **D1**: Core feature implementation
- **D2**: Testing and validation
- **R1**: Code review and release preparation

**Current Stage**: {current_stage}
**Output**: aceflow-result/{iteration_id}/standard/{stage}/
```

#### Complete Mode (S1→S8)
```markdown
🎯 **Complete Mode Active**
Full enterprise workflow with all 8 stages:
S1→S2→S3→S4→S5→S6→S7→S8

**Current Stage**: {current_stage}
**Progress**: {overall_progress}%
**Output**: aceflow-result/{iteration_id}/{stage_folder}/
```

## 📝 Cross-Session Memory Management

### Memory Storage Rules

**Always store important information:**
```markdown
## Memory Update
**Category**: {requirements|decisions|patterns|issues|learning}
**Content**: {key_information}
**Importance**: {0.1-1.0}
**Tags**: {relevant_tags}
**Timestamp**: {current_time}

Stored to: `.aceflow/memory/{category}/{timestamp}_{hash}.md`
```

### Memory Recall

**Before starting any stage, recall relevant memories:**
```markdown
## Relevant Memories Found
📚 **Requirements**: {relevant_requirements}
🎯 **Previous Decisions**: {past_decisions}
🔧 **Patterns Used**: {code_patterns}
⚠️ **Known Issues**: {potential_problems}
💡 **Lessons Learned**: {insights}
```

## 🚦 Decision Gates Integration

### Intelligent Gate Evaluation

**Before proceeding to next stage:**
```markdown
## Decision Gate Evaluation: DG{number}

**Current Stage**: {stage_name}
**Completion Criteria**:
- [ ] {criterion_1}
- [ ] {criterion_2}
- [ ] {criterion_3}

**Quality Metrics**:
- Code Coverage: {percentage}%
- Documentation: {complete|partial|missing}
- Testing: {passed|failed|pending}

**Decision**: {PASS|REVIEW_NEEDED|BLOCK}
**Reasoning**: {explanation}

**Next Action**: {recommended_action}
```

## 📁 Output Management

### Standardized Output Structure

**All deliverables go to aceflow-result:**
```
aceflow-result/
├── iter_{timestamp}/
│   ├── {mode}_{stage}/
│   │   ├── deliverable_1.md
│   │   ├── deliverable_2.md
│   │   └── artifacts/
│   └── summary.md
```

### Stage-Specific Outputs

**For each stage, create appropriate deliverables:**
```markdown
## Stage Output Template

**Stage**: {stage_name}
**Mode**: {workflow_mode}
**Duration**: {actual_time_spent}
**Quality Score**: {0-100}

**Deliverables**:
- Primary: {main_deliverable}
- Supporting: {additional_files}
- Artifacts: {code_samples|diagrams|tests}

**Next Stage Preparation**:
- Prerequisites: {what_needs_to_be_ready}
- Estimated Time: {time_estimate}
```

## 🔧 Helper Scripts Integration

### Project Initialization

When starting new AceFlow project:
```bash
# Initialize AceFlow structure
python scripts/init_project.py --mode {selected_mode} --description "{task_description}"
```

### Memory Recovery

When memory seems inconsistent:
```bash
# Fix memory and state
python scripts/fix_memory.py --validate --repair
```

### Status Check

Regular status verification:
```bash
# Comprehensive status check
python scripts/status_check.py --detailed --suggest-actions
```

## 🎪 Conversation Examples

### Example 1: New Feature Development
```
User: I need to add user authentication to my web app

AI Agent: 🔄 **AceFlow Detection**: No existing workflow found
📋 **Task Analysis**: 
- Type: New feature development
- Complexity: Medium (auth system)
- Recommended Mode: Standard (P1→P2→D1→D2→R1)
- Estimated Time: 3-5 days

🚀 **Initializing Standard Mode Workflow**

**P1 - Requirements Analysis** (Starting now)
- Analyzing authentication requirements
- Creating user stories
- Defining acceptance criteria

Output location: `aceflow-result/iter_{timestamp}/standard/P1_requirements/`

Shall I proceed with requirements analysis?
```

### Example 2: Continuing Existing Workflow
```
User: What's the current status?

AI Agent: 🔄 **AceFlow Status Check**

📊 **Current State**:
- Mode: Standard
- Stage: D1 (Implementation) - 60% complete
- Started: 2 days ago
- Remaining: ~1 day

📋 **Progress Summary**:
- ✅ P1: Requirements completed
- ✅ P2: Design completed  
- 🔄 D1: Core features 60% done
- ⏳ D2: Testing pending
- ⏳ R1: Review pending

🎯 **Next Actions**:
1. Complete user registration module
2. Implement password hashing
3. Add session management

📁 **Current Output**: `aceflow-result/iter_{timestamp}/standard/D1_implementation/`

Ready to continue implementation?
```

### Example 3: Problem Resolution
```
User: The login feature isn't working properly

AI Agent: 🚨 **Issue Detected in Active AceFlow**

📋 **Context Analysis**:
- Current Stage: D2 (Testing)
- Issue Type: Functional bug
- Impact: Blocks workflow progression

🧠 **Memory Recall**:
- Similar issue resolved in iter_{previous_timestamp}: session timeout problem
- Previous solution: Updated session configuration

🔧 **Recommended Approach**:
1. Document issue in current stage
2. Apply emergency fix pattern
3. Update test cases
4. Continue D2 stage

📁 **Issue Documentation**: `aceflow-result/iter_{timestamp}/standard/D2_testing/issues/login_bug_{timestamp}.md`

Shall I start the debugging workflow?
```

## 🎯 Key Success Factors

1. **Always check for existing AceFlow state first**
2. **Follow aceflow-spec_v3.0.md religiously**
3. **Maintain cross-session continuity through state files**
4. **Store all outputs in aceflow-result directory**
5. **Use helper scripts when needed**
6. **Keep memory updated with important decisions**
7. **Respect workflow stage boundaries and decision gates**

---

**Remember**: AceFlow enhances AI Agent by adding structured workflow management, not by replacing core capabilities. The goal is seamless integration that makes development more organized and continuous across sessions.

*Generated by AceFlow v3.0 MCP Server - Integration Rules*
*项目: debug-test-project | 模式: STANDARD | 创建时间: 2025-08-06 18:02:24*
