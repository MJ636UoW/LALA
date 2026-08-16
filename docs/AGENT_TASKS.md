# LALA Agent Task Lifecycle & Execution Limits

System Identity: **LALA**  
Target User: **Mandar**

---

## 📋 Task Lifecycle & Execution Caps

```text
Goal -> TaskPlanner -> TaskPlan -> Security Engine Authorization -> Step Execution -> TaskVerifier -> Recovery Manager -> Output
```

- **Task Plan Limit**: `MAX_AGENT_STEPS = 8`
- **Sub-step Tool Limit**: `MAX_TOOL_ITERATIONS = 5`
- **Max Retries**: `MAX_RETRIES = 2` (Refuses retries for security permission denials or destructive operations).
