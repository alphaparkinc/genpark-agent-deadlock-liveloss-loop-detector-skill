import sys, json
from client import AgentDeadlockLivelossLoopDetector

def main():
    detector = AgentDeadlockLivelossLoopDetector()
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try:
            req = json.loads(line)
            method = req.get("method")
            rid = req.get("id")
            params = req.get("params", {})

            if method == "tools/list":
                res = {
                    "tools": [
                        {"name": "record_action", "description": "Record action and check loop.", "inputSchema": {"type": "object", "properties": {"tool_name": {"type": "string"}, "args": {"type": "object"}}, "required": ["tool_name", "args"]}},
                        {"name": "run_benchmark_loop_detector", "description": "Run benchmark.", "inputSchema": {"type": "object"}}
                    ]
                }
            elif method == "tools/call":
                tname = params.get("name")
                args = params.get("arguments", {})
                if tname == "record_action":
                    out = detector.record_action(args.get("tool_name", ""), args.get("args", {}))
                elif tname == "run_benchmark_loop_detector":
                    out = detector.run_benchmark_loop_detector()
                else:
                    out = {"error": f"Unknown tool {tname}"}
                res = {"content": [{"type": "text", "text": json.dumps(out)}]}
            else:
                res = {"error": "Unsupported method"}
            print(json.dumps({"jsonrpc": "2.0", "id": rid, "result": res}), flush=True)
        except Exception as e:
            print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}), flush=True)

if __name__ == "__main__":
    main()
