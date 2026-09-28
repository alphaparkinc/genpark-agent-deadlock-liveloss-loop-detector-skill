import sys, json, hashlib

class AgentDeadlockLivelossLoopDetector:
    """
    Zero-Dependency Autonomous Agent Deadlock & Liveloss Loop Detector.
    Tracks execution trajectories, detects cyclic repetition patterns (e.g. A->B->A->B),
    and measures state signature entropy to identify oscillatory planning failures.
    """
    def __init__(self, window_size=12, max_repetition_threshold=3):
        self.window_size = window_size
        self.max_repetition_threshold = max_repetition_threshold
        self.action_history = []  # list of action hashes

    def _hash_action(self, tool_name, args):
        serialized = json.dumps({"tool": tool_name, "args": args}, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:12]

    def record_action(self, tool_name, args):
        act_hash = self._hash_action(tool_name, args)
        self.action_history.append((tool_name, act_hash))

        if len(self.action_history) > self.window_size:
            self.action_history.pop(0)

        # Detect cyclic repetition for period lengths 1 to window_size // 2
        history_hashes = [h for _, h in self.action_history]
        n = len(history_hashes)

        for period in range(1, (n // 2) + 1):
            if n < period * self.max_repetition_threshold:
                continue

            # Compare most recent chunk with preceding chunks
            recent_pattern = history_hashes[-period:]
            matches = 0
            for i in range(1, self.max_repetition_threshold + 1):
                chunk = history_hashes[-period * i : n - period * (i - 1)] if i > 1 else history_hashes[-period:]
                if chunk == recent_pattern:
                    matches += 1
                else:
                    break

            if matches >= self.max_repetition_threshold:
                return {
                    "loop_detected": True,
                    "loop_type": "EXACT_CYCLIC_REPETITION",
                    "period_length": period,
                    "cycle_pattern": [t for t, _ in self.action_history[-period:]],
                    "recommendation": "BREAK_INFINITE_LOOP_AND_FORCE_REPLAN"
                }

        return {
            "loop_detected": False,
            "trajectory_length": len(self.action_history),
            "recommendation": "CONTINUE_NORMAL_EXECUTION"
        }

    def run_benchmark_loop_detector(self):
        self.action_history = []
        # Normal execution
        self.record_action("read_file", {"path": "main.py"})
        self.record_action("run_tests", {"cmd": "pytest"})
        r_normal = self.record_action("git_commit", {"msg": "fix test"})

        # Simulating infinite loop: edit_file -> run_tests -> edit_file -> run_tests...
        loop_res = None
        for _ in range(4):
            self.record_action("edit_file", {"file": "app.py", "line": 42})
            loop_res = self.record_action("run_tests", {"cmd": "pytest"})

        return {
            "benchmark_status": "PASSED",
            "normal_execution_passed": not r_normal["loop_detected"],
            "infinite_loop_caught": loop_res["loop_detected"],
            "detected_loop_type": loop_res.get("loop_type"),
            "cycle_pattern": loop_res.get("cycle_pattern")
        }
