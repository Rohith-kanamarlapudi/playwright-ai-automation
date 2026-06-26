✅ FINAL BENCHMARK REPORT
Model Used:
DeepSeek V4 Flash


📊 Performance Results (3 runs):
Average Duration: 149.0 seconds
Average Throughput: 0.034 agents/sec
Memory Usage: ~3.8 MB (stable)
CPU Usage: 0% (API-based workload)


🧠 Observations:
Pipeline is stable across all runs
Memory usage is consistent
No crashes or failures observed
Performance is bounded by LLM API latency


⚡ Strengths:
Strong structured output from agents
Good integration with scraper
Stable multi-agent LangGraph execution
Clean context flow between agents


⚠️ Weaknesses:
High latency (~2.5 minutes per run)
Sequential execution only (no parallelism)
Some risk of hallucinated test cases if prompts not strict


🏁 Final Decision:
✔ DeepSeek V4 Flash is suitable for development and prototyping
⚠ Not optimized for real-time or high-throughput production