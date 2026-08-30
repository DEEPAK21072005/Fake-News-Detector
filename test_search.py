import sys
sys.path.insert(0, '.')
from backend.app.services.realtime_search_service import fetch_live_evidence, extract_search_query

claim = "Narendra Modi is alive and serving as Prime Minister of India"
q = extract_search_query(claim)
print(f"Query extracted: '{q}'")

results = fetch_live_evidence(claim, top_k=5)
print(f"\nTotal results: {len(results)}")
for r in results:
    print(f"  [{r['stance']:14}] [{r.get('_source_type','?'):12}] {r['title'][:80]}")
    print(f"               cred={r['credibility_score']:.2f} adj={r['adjusted_score']:.2f} url={r['url'][:60]}")
