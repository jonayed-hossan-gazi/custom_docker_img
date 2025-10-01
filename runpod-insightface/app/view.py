import pickle
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import os

def analyze_pkl_results(pkl_path):
    # Load the data
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
    
    print(f"📊 COMPREHENSIVE ANALYSIS OF FACE RECOGNITION RESULTS")
    print(f"=====================================================")
    print(f"Total records: {len(data):,}")
    
    # Basic statistics
    face_counts = []
    detection_scores = []
    quality_scores = []
    successful_detections = 0
    failed_detections = 0
    
    for image_path, result in data.items():
        if isinstance(result, dict) and 'faces' in result:
            face_count = len(result['faces'])
            face_counts.append(face_count)
            
            if face_count > 0:
                successful_detections += 1
                for face in result['faces']:
                    if 'det_score' in face:
                        detection_scores.append(face['det_score'])
                    if 'quality' in face:
                        quality_scores.append(face['quality'])
            else:
                failed_detections += 1
    
    print(f"\n🎯 FACE DETECTION SUMMARY:")
    print(f"   Successful detections: {successful_detections:,} ({successful_detections/len(data)*100:.1f}%)")
    print(f"   Failed detections: {failed_detections:,} ({failed_detections/len(data)*100:.1f}%)")
    print(f"   Total faces detected: {sum(face_counts):,}")
    
    if face_counts:
        face_count_dist = Counter(face_counts)
        print(f"\n👥 FACES PER IMAGE DISTRIBUTION:")
        for count, freq in sorted(face_count_dist.items()):
            percentage = (freq / len(data)) * 100
            print(f"   {count} face(s): {freq:,} images ({percentage:.1f}%)")
    
    if detection_scores:
        print(f"\n📈 DETECTION SCORE STATISTICS:")
        print(f"   Average: {np.mean(detection_scores):.3f}")
        print(f"   Std Dev: {np.std(detection_scores):.3f}")
        print(f"   Min: {np.min(detection_scores):.3f}")
        print(f"   Max: {np.max(detection_scores):.3f}")
        print(f"   Median: {np.median(detection_scores):.3f}")
        
        # Score distribution
        bins = [0, 0.3, 0.5, 0.7, 0.9, 1.0]
        hist, _ = np.histogram(detection_scores, bins=bins)
        print(f"\n   Detection Score Ranges:")
        for i in range(len(hist)):
            print(f"   {bins[i]:.1f}-{bins[i+1]:.1f}: {hist[i]:,} faces ({hist[i]/len(detection_scores)*100:.1f}%)")
    
    if quality_scores:
        print(f"\n🎭 QUALITY SCORE STATISTICS:")
        print(f"   Average: {np.mean(quality_scores):.3f}")
        print(f"   Std Dev: {np.std(quality_scores):.3f}")
        print(f"   Min: {np.min(quality_scores):.3f}")
        print(f"   Max: {np.max(quality_scores):.3f}")
        print(f"   Median: {np.median(quality_scores):.3f}")
        
        # Quality distribution
        quality_bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
        quality_hist, _ = np.histogram(quality_scores, bins=quality_bins)
        print(f"\n   Quality Score Ranges:")
        for i in range(len(quality_hist)):
            print(f"   {quality_bins[i]:.1f}-{quality_bins[i+1]:.1f}: {quality_hist[i]:,} faces ({quality_hist[i]/len(quality_scores)*100:.1f}%)")
    
    # Analyze embedding properties
    embedding_shapes = []
    embedding_dtypes = []
    
    for image_path, result in data.items():
        if isinstance(result, dict) and 'faces' in result:
            for face in result['faces']:
                if 'embedding' in face and face['embedding'] is not None:
                    embedding = face['embedding']
                    embedding_shapes.append(embedding.shape)
                    embedding_dtypes.append(str(embedding.dtype))
    
    if embedding_shapes:
        unique_shapes = Counter(embedding_shapes)
        unique_dtypes = Counter(embedding_dtypes)
        
        print(f"\n🔢 EMBEDDING ANALYSIS:")
        print(f"   Total embeddings: {len(embedding_shapes):,}")
        print(f"   Shape distribution:")
        for shape, count in unique_shapes.items():
            print(f"     {shape}: {count:,}")
        print(f"   Data types:")
        for dtype, count in unique_dtypes.items():
            print(f"     {dtype}: {count:,}")
    
    # Sample analysis of first few entries
    print(f"\n🔍 SAMPLE ANALYSIS (first 5 successful detections):")
    sample_count = 0
    for image_path, result in list(data.items())[:50]:  # Check first 50
        if sample_count >= 5:
            break
        if isinstance(result, dict) and 'faces' in result and len(result['faces']) > 0:
            face = result['faces'][0]
            print(f"   {os.path.basename(image_path)}:")
            print(f"     Detection: {face.get('det_score', 'N/A'):.3f}")
            print(f"     Quality: {face.get('quality_score', 'N/A')}")
            if 'embedding' in face and face['embedding'] is not None:
                emb = face['embedding']
                print(f"     Embedding: shape{emb.shape}, norm: {np.linalg.norm(emb):.3f}")
            sample_count += 1

# Run the analysis
import sys
if __name__ == "__main__":
    pkl_path = sys.argv[1]
    analyze_pkl_results(pkl_path)
