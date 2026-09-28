from client import AgentDeadlockLivelossLoopDetector
import json

def main():
    detector = AgentDeadlockLivelossLoopDetector()
    res = detector.run_benchmark_loop_detector()
    print("Loop Detector Benchmark Result:")
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
