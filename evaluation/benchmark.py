# evaluation/benchmark.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import matplotlib.pyplot as plt
from datetime import datetime
from agent.graph import run_agent

# Benchmark Tasks
TASKS = [
    {
        "id": 1,
        "task": "Write a Python function to check if a number is prime",
        "keywords": ["def", "prime", "return"]
    },
    {
        "id": 2,
        "task": "Write a Python function to reverse a string",
        "keywords": ["def", "return", "[::-1]"]
    },
    {
        "id": 3,
        "task": "Write a Python function to find the factorial of a number using recursion",
        "keywords": ["def", "factorial", "return", "recursive"]
    },
    {
        "id": 4,
        "task": "Write a Python function to perform binary search on a sorted list",
        "keywords": ["def", "binary", "return", "mid"]
    },
    {
        "id": 5,
        "task": "Write a Python class for a Stack with push, pop and peek methods",
        "keywords": ["class", "def push", "def pop", "def peek"]
    },
    {
        "id": 6,
        "task": "Write a Python function to find all duplicate elements in a list",
        "keywords": ["def", "return", "duplicate"]
    },
    {
        "id": 7,
        "task": "Write a Python function to flatten a nested list",
        "keywords": ["def", "return", "flatten"]
    },
    {
        "id": 8,
        "task": "Write a Python function to count word frequency in a string",
        "keywords": ["def", "return", "count"]
    },
    {
        "id": 9,
        "task": "Write a Python function to check if a string is a palindrome",
        "keywords": ["def", "return", "palindrome"]
    },
    {
        "id": 10,
        "task": "Write a Python function to merge two sorted lists",
        "keywords": ["def", "return", "merge", "sorted"]
    }
]


# Evaluation Functions

def evaluate_task(task_obj: dict) -> dict:
    """Run agent on one task and evaluate the result."""
    print(f"\n{'='*50}")
    print(f"Task {task_obj['id']}/10: {task_obj['task']}")
    print(f"{'='*50}")

    start_time = time.time()

    try:
        result = run_agent(task_obj["task"])
        elapsed = round(time.time() - start_time, 2)

        # Check 1: did code execute successfully?
        execution_success = result["result"].get("success", False)

        # Check 2: does code contain expected keywords?
        code_lower = result["code"].lower()
        keyword_hits = sum(1 for kw in task_obj["keywords"] if kw.lower() in code_lower)
        keyword_score = keyword_hits / len(task_obj["keywords"])
        keyword_pass = keyword_score >= 0.5  # at least 50% keywords present

        # Overall pass = execution success + keyword check
        passed = execution_success and keyword_pass

        return {
            "id": task_obj["id"],
            "task": task_obj["task"],
            "passed": passed,
            "execution_success": execution_success,
            "keyword_score": round(keyword_score, 2),
            "attempts": result["attempts"],
            "time_seconds": elapsed,
            "code_length": len(result["code"]),
        }

    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        print(f"❌ Agent crashed: {e}")
        return {
            "id": task_obj["id"],
            "task": task_obj["task"],
            "passed": False,
            "execution_success": False,
            "keyword_score": 0,
            "attempts": 0,
            "time_seconds": elapsed,
            "code_length": 0,
        }


def run_benchmark() -> dict:
    """Run all tasks and collect results."""
    print(f"\n🚀 Starting AutoCoder Benchmark")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total Tasks: {len(TASKS)}\n")

    results = []
    for task_obj in TASKS:
        result = evaluate_task(task_obj)
        results.append(result)
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"\n{status} | Task {result['id']} | Time: {result['time_seconds']}s | Attempts: {result['attempts']}")

    return results


def calculate_metrics(results: list) -> dict:
    """Calculate overall benchmark metrics."""
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    pass_rate = round((passed / total) * 100, 1)
    avg_attempts = round(sum(r["attempts"] for r in results) / total, 2)
    avg_time = round(sum(r["time_seconds"] for r in results) / total, 2)

    return {
        "total_tasks": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": pass_rate,
        "avg_attempts": avg_attempts,
        "avg_time_seconds": avg_time
    }


def save_results(results: list, metrics: dict) -> None:
    """Save results to JSON file."""
    output = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": metrics,
        "results": results
    }
    path = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
    with open(path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n💾 Results saved to evaluation/benchmark_results.json")


def plot_results(results: list, metrics: dict) -> None:
    """Plot benchmark results as a bar chart."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f"AutoCoder Agent Benchmark Results\nPass Rate: {metrics['pass_rate']}%", 
                 fontsize=14, fontweight="bold")

    # Plot 1: Pass/Fail per task
    task_ids = [f"T{r['id']}" for r in results]
    colors = ["#2ecc71" if r["passed"] else "#e74c3c" for r in results]
    keyword_scores = [r["keyword_score"] for r in results]

    axes[0].bar(task_ids, keyword_scores, color=colors)
    axes[0].set_title("Keyword Score per Task\n(Green=Pass, Red=Fail)")
    axes[0].set_xlabel("Task")
    axes[0].set_ylabel("Keyword Score (0-1)")
    axes[0].set_ylim(0, 1.2)
    axes[0].axhline(y=0.5, color="orange", linestyle="--", label="Pass threshold")
    axes[0].legend()

    # Plot 2: Summary pie chart
    labels = ["Passed", "Failed"]
    sizes = [metrics["passed"], metrics["failed"]]
    colors_pie = ["#2ecc71", "#e74c3c"]
    axes[1].pie(sizes, labels=labels, colors=colors_pie, autopct="%1.1f%%", startangle=90)
    axes[1].set_title(f"Overall Pass Rate\n({metrics['passed']}/{metrics['total_tasks']} tasks passed)")

    plt.tight_layout()

    # Save chart
    chart_path = os.path.join(os.path.dirname(__file__), "benchmark_chart.png")
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    print(f"Chart saved to evaluation/benchmark_chart.png")
    plt.show()


# Main

if __name__ == "__main__":
    # Run benchmark
    results = run_benchmark()

    # Calculate metrics
    metrics = calculate_metrics(results)

    # Print summary
    print(f"\n{'='*50}")
    print(f"📊 BENCHMARK SUMMARY")
    print(f"{'='*50}")
    print(f"✅ Passed:        {metrics['passed']}/{metrics['total_tasks']}")
    print(f"📈 Pass Rate:     {metrics['pass_rate']}%")
    print(f"🔄 Avg Attempts:  {metrics['avg_attempts']}")
    print(f"⏱️  Avg Time:      {metrics['avg_time_seconds']}s")
    print(f"{'='*50}")

    # Save + plot
    save_results(results, metrics)
    plot_results(results, metrics)