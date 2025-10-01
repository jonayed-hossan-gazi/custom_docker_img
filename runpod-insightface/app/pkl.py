import pickle, sys
import random

with open(sys.argv[1], "rb") as f:
    data = pickle.load(f)
print(f"Loaded {len(data)} results")

# Get one example (first image)
if data:
    img_path, result = next(iter(data.items()))
    img_path, result = random.choice(list(data.items()))

    print(f"📄 Example image: {img_path}")
    print(f"   Face count: {result['face_count']}")
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
    elif result["faces"]:
        face = result["faces"][0]  # first face
        print(f"   👤 First face:")
        print(f"      - Detection score: {face['det_score']:.4f}")
        print(f"      - Bounding box: {face['bbox']}")  # [x1, y1, x2, y2]
        print(f"      - Quality score: {face['quality_score']:.4f}")
        print(f"      - Embedding shape: {face['embedding'].shape}")
        print(f"      - Embedding dtype: {face['embedding'].dtype}")
        print(f"      - Embedding (first 5 values): {face['embedding'][:5]}")
    else:
        print("   🚫 No faces detected")
else:
    print("⚠️  No results found!")
