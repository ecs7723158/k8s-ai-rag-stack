#!/usr/bin/env python3
"""
vLLM High-Throughput & TTFT Latency Benchmark Suite
Evaluates Time-To-First-Token (TTFT), Inter-Token Latency (ITL), and Request Concurrency.
"""

import time
import argparse
import statistics
import concurrent.futures

def simulate_vllm_request(req_id: int, prompt_len: int, gen_len: int):
    start = time.time()
    # Simulate TTFT (PagedAttention prefill phase)
    ttft = 0.015 + (prompt_len / 1000) * 0.02
    time.sleep(ttft)
    
    # Simulate Token Generation (Continuous batching decode phase)
    itl = 0.008
    for _ in range(gen_len):
        time.sleep(itl)
        
    total_time = time.time() - start
    tokens_per_sec = gen_len / total_time
    return {
        "id": req_id,
        "ttft_ms": round(ttft * 1000, 2),
        "total_time_s": round(total_time, 4),
        "tokens_per_sec": round(tokens_per_sec, 2),
        "status": "SUCCESS"
    }

def run_benchmark(concurrency: int = 10, total_requests: int = 50):
    print(f"[*] Starting vLLM Benchmark: {total_requests} requests at concurrency {concurrency}...")
    results = []
    start_all = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(simulate_vllm_request, i, 512, 128) for i in range(total_requests)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())
            
    elapsed = time.time() - start_all
    ttft_list = [r["ttft_ms"] for r in results]
    tps_list = [r["tokens_per_sec"] for r in results]
    
    print("\n" + "="*50)
    print("           BENCHMARK RESULTS SUMMARY           ")
    print("="*50)
    print(f"Total Requests:         {total_requests}")
    print(f"Concurrency Level:      {concurrency}")
    print(f"Total Elapsed Time:     {round(elapsed, 2)} s")
    print(f"Average TTFT:           {round(statistics.mean(ttft_list), 2)} ms")
    print(f"P95 TTFT:               {round(statistics.quantiles(ttft_list, n=20)[18], 2)} ms")
    print(f"P99 TTFT:               {round(statistics.quantiles(ttft_list, n=100)[98], 2)} ms")
    print(f"Throughput (Tokens/s):  {round(sum(tps_list), 2)} tokens/sec")
    print("="*50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="vLLM Inference Benchmark")
    parser.add_argument("--concurrency", type=int, default=8, help="Concurrent workers")
    parser.add_argument("--requests", type=int, default=40, help="Total requests to fire")
    args = parser.parse_args()
    run_benchmark(concurrency=args.concurrency, total_requests=args.requests)
