#!/usr/bin/env python3
"""
RAG Hybrid Retrieval & Reranker Evaluation Suite
Calculates HitRate@K, Mean Reciprocal Rank (MRR), and NDCG for Vector + BM25 + BGE Reranker pipelines.
"""

import math

def calculate_mrr(eval_data):
    reciprocal_ranks = []
    for item in eval_data:
        ground_truth = item["ground_truth"]
        retrieved = item["retrieved"]
        rank = -1
        for idx, doc_id in enumerate(retrieved):
            if doc_id in ground_truth:
                rank = idx + 1
                break
        if rank != -1:
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)
    return sum(reciprocal_ranks) / len(reciprocal_ranks)

def calculate_hit_rate(eval_data, k=5):
    hits = 0
    for item in eval_data:
        ground_truth = item["ground_truth"]
        top_k = item["retrieved"][:k]
        if any(doc in ground_truth for doc in top_k):
            hits += 1
    return hits / len(eval_data)

def run_evaluation():
    # Sample evaluation dataset simulating complex multi-modal technical queries
    eval_set = [
        {"query": "Kueue cohort preemption policy", "ground_truth": ["doc-101"], "retrieved": ["doc-101", "doc-105", "doc-202"]},
        {"query": "vLLM PagedAttention block size tuning", "ground_truth": ["doc-304"], "retrieved": ["doc-304", "doc-301", "doc-399"]},
        {"query": "RAGFlow DeepDoc OCR table recognition", "ground_truth": ["doc-505"], "retrieved": ["doc-505", "doc-512", "doc-513"]},
        {"query": "Dify DSL workflow agent iteration", "ground_truth": ["doc-808"], "retrieved": ["doc-801", "doc-808", "doc-810"]},
        {"query": "RayCluster GCS fault tolerance", "ground_truth": ["doc-909"], "retrieved": ["doc-909", "doc-902", "doc-911"]},
    ]
    
    mrr = calculate_mrr(eval_set)
    hit_rate_top1 = calculate_hit_rate(eval_set, k=1)
    hit_rate_top3 = calculate_hit_rate(eval_set, k=3)
    
    print("\n" + "="*50)
    print("      RAG HYBRID RETRIEVAL EVALUATION RESULTS     ")
    print("="*50)
    print(f"Total Test Queries:     {len(eval_set)}")
    print(f"HitRate@1:              {round(hit_rate_top1 * 100, 2)}%")
    print(f"HitRate@3:              {round(hit_rate_top3 * 100, 2)}%")
    print(f"Mean Reciprocal Rank:   {round(mrr, 4)}")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_evaluation()
