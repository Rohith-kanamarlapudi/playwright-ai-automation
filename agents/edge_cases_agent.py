import json
from agents.state import AgentState
from agents.llm_client import get_llm
from performance.engine import PerformanceTracker



def edge_cases_agent(state: AgentState) -> AgentState:

    tracker = PerformanceTracker(label="edge_cases_agent")
    tracker.start()

    try:
        llm = get_llm()

        print("[Edge Cases Agent] Running...")

        task_plan = state.get("task_plan", [])
        

        LIVE_EDGE_CASE_PROMPT = """

What edge cases are unique to a live IoT dashboard?

- What if a sensor goes offline? (widget shows '--' or 'N/A')
- What if data hasn't refreshed yet? (stale timestamp)
- What if websocket disconnects? (fallback UI)
- What if a chart has no data? (empty state)
- What if a user navigates during a live refresh?


You are a QA Automation Expert for Live IoT dashboards.

Task Plan:
{task_plan}

Architecture:
{architecture_notes}

Target URL:
{target_url}

Generate exactly 6 execution-focused edge cases.

Focus on:

1. Sensor offline / null data
2. Network interruption during widget load
3. Stale timestamp / outdated data
4. Empty chart / empty table
5. Rapid navigation between dashboard pages
6. Widget rendering during live refresh

Rules

- Return ONLY a JSON array.
- One edge case per item.
- No markdown.
- No explanations.
"""

        prompt = LIVE_EDGE_CASE_PROMPT.format(
            task_plan="\n".join(task_plan),
            architecture_notes=state.get("architecture_notes", ""),
            target_url=state.get("target_url", ""),
        )

        response = llm.invoke(prompt)

        text = response.content if hasattr(response, "content") else str(response)
        
        
        

        

        try:

            edge_cases = json.loads(text)

            if not isinstance(edge_cases, list):
                raise ValueError("Expected JSON list")

            edge_cases = [
                str(case).strip()
                for case in edge_cases
                if str(case).strip()
            ]
            
            # Keep only the first 6 edge cases
            edge_cases = edge_cases[:6]

        except Exception:

            edge_cases = []

            for line in text.splitlines():

                line = line.strip()

                if not line:
                    continue

                line = line.lstrip("-•0123456789. ").strip()

                if line:
                    edge_cases.append(line)
                # Ensure exactly 6 edge cases
                edge_cases = edge_cases[:6]
                
                
                
                
                

        state["edge_cases"] = edge_cases

        print(f"[Edge Cases Agent] Generated {len(edge_cases)} edge cases.")

    except Exception as e:

        print("[Edge Cases Error]", e)

        state["edge_cases"] = [
            f"Edge case generation failed: {e}"
        ]

    finally:

        tracker.stop(agents_completed=1)
        tracker.save("reports/per_agent_perf.json")

    return state