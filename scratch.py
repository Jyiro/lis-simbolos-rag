import json
import glob
import sys

def load_results(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data['results']

qwen_path = "results/20260806_155911_qwen3.5-2b_llama_cpp_nothink/results.json"
gemma_path = "results/20260806_163023_gemma-4b_llama_cpp_nothink/results.json"

qwen_res = { (r['fragment_id'], r['condition_label']): r for r in load_results(qwen_path) }
gemma_res = { (r['fragment_id'], r['condition_label']): r for r in load_results(gemma_path) }

fragments = sorted(list(set(k[0] for k in qwen_res.keys())))
conditions = [
    "LIMPIO    | sin tabla",
    "DOC CORR  | sin tabla",
    "LATEX     | sin tabla",
    "CON TABLA | plain",
    "I1-A      | énfasis simple",
    "I1-B      | override semántico",
    "I1-C      | rol simulado en user",
    "I1-D      | system message real"
]

for frag in fragments:
    print(f"\n{'='*80}")
    print(f"FRAGMENTO: {frag}")
    print(f"{'='*80}")
    for cond in conditions:
        print(f"\n--- {cond} ---")
        q = qwen_res.get((frag, cond))
        g = gemma_res.get((frag, cond))
        
        q_ans = q['response'].strip() if q else 'N/A'
        g_ans = g['response'].strip() if g else 'N/A'
        
        print(f"QWEN 2B : {q_ans}")
        print(f"GEMMA 4B: {g_ans}")
