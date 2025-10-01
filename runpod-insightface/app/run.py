#!/usr/bin/env python3
import os
import sys
import time
import pickle
import signal
import argparse
import threading
import numpy as np
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, TimeoutError
from insightface.app import FaceAnalysis
from typing import Dict, Any

# ---------------------------
# Configurable constants
# ---------------------------
CHECKPOINT_EVERY = 20000
CHECKPOINT_EVERY_SEC = 500
MAX_SHUTDOWN_WAIT = 5
FUTURE_TIMEOUT = 10            # Timeout for individual futures
THREAD_SHUTDOWN_TIMEOUT = 3    # Timeout for thread pool shutdown

# ---------------------------
# Global state
# ---------------------------
shutdown_requested = False
last_checkpoint_time = 0
processed_count = 0
total_to_process = 0
results_lock = threading.Lock()
new_results = {}

# ---------------------------
# Signal handler (debounced)
# ---------------------------
def signal_handler(signum, frame):
    global shutdown_requested
    if shutdown_requested:
        print("\n⏳ Shutdown already in progress...", file=sys.stderr)
        return
    print(f"\n\n🛑 Signal {signum} received. Stopping and saving...", file=sys.stderr)
    shutdown_requested = True

# ---------------------------
# Atomic save with timeout
# ---------------------------
def save_results_with_timeout(existing: Dict[str, Any], new: Dict[str, Any], output_path: str, timeout: int = 3):
    def _save():
        temp_path = output_path + ".tmp"
        try:
            final = {**existing, **new}
            with open(temp_path, 'wb') as f:
                pickle.dump(final, f, protocol=pickle.HIGHEST_PROTOCOL)
            os.replace(temp_path, output_path)
            print(f"✅ Checkpoint saved: {len(final)} results", file=sys.stderr)
            return True
        except Exception as e:
            print(f"❌ Save failed: {e}", file=sys.stderr)
            return False

    # Run save in a separate thread with timeout
    save_thread = threading.Thread(target=_save)
    save_thread.daemon = True
    save_thread.start()
    save_thread.join(timeout=timeout)
    
    if save_thread.is_alive():
        print(f"⚠️  Save timed out after {timeout}s", file=sys.stderr)
        return False
    return True

# ---------------------------
# Process one image
# ---------------------------
def process_image(img_path: str, app) -> Dict[str, Any]:
    try:
        img_array = np.fromfile(img_path, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            return {"error": "decode failed", "face_count": 0, "faces": []}

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces_raw = app.get(img_rgb)

        img_h, img_w = img.shape[:2]
        img_area = img_w * img_h
        faces = []

        for face in faces_raw:
            x1, y1, x2, y2 = face.bbox
            x1 = max(0, int(x1))
            y1 = max(0, int(y1))
            x2 = min(img_w - 1, int(x2))
            y2 = min(img_h - 1, int(y2))
            if x2 <= x1 or y2 <= y1:
                print("Clamp Bounding Boxes") #continue
            face_area = max(0, x2 - x1) * max(0, y2 - y1)
            rel_size = face_area / img_area if img_area > 0 else 0.0
            quality_score = float(face.det_score * np.sqrt(rel_size + 1e-6))

            faces.append({
                "det_score": float(face.det_score),
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                "quality_score": quality_score,
                "embedding": face.embedding.astype(np.float32)
            })

        return {"face_count": len(faces), "faces": faces}
    except Exception as e:
        return {"error": str(e), "face_count": 0, "faces": []}

# ---------------------------
# Get image paths
# ---------------------------
def get_image_paths(img_dir: str):
    exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    paths = []
    for root, _, files in os.walk(img_dir):
        for f in files:
            if os.path.splitext(f.lower())[1] in exts or True: #allw all format
                paths.append(os.path.join(root, f))
    return paths

# ---------------------------
# Main
# ---------------------------
def main():
    global shutdown_requested, last_checkpoint_time, processed_count, total_to_process, new_results

    parser = argparse.ArgumentParser()
    parser.add_argument("--img-dir", required=True)
    parser.add_argument("--output-pkl", required=True)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--gpu-id", type=int, default=0)

    args = parser.parse_args()

    if not os.path.isdir(args.img_dir):
        print(f"❌ Directory not found: {args.img_dir}", file=sys.stderr)
        sys.exit(1)

    # Setup signals
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Load existing
    existing_results = {}
    if os.path.exists(args.output_pkl):
        try:
            with open(args.output_pkl, 'rb') as f:
                existing_results = pickle.load(f)
            print(f"📥 Loaded {len(existing_results)} existing results", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  Failed to load: {e}. Starting fresh.", file=sys.stderr)

    # Get paths
    all_paths = get_image_paths(args.img_dir)
    existing_paths = set(existing_results.keys())
    remaining_paths = [p for p in all_paths if p not in existing_paths]
    total_to_process = len(remaining_paths)

    if total_to_process == 0:
        print("🎉 All done!", file=sys.stderr)
        return

    print(f"📁 Processing {total_to_process} images", file=sys.stderr)

    # Init model
    app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
    app.prepare(ctx_id=args.gpu_id, det_size=(640, 640))

    # Start processing
    start_time = time.time()
    last_checkpoint_time = start_time
    processed_count = 0
    new_results = {}

    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        future_to_path = {executor.submit(process_image, p, app): p for p in remaining_paths}
        
        # Process completed futures
        for future in as_completed(future_to_path):
            if shutdown_requested:
                print("🛑 Stopping submission...", file=sys.stderr)
                # Cancel remaining futures
                for f in future_to_path:
                    f.cancel()
                break

            img_path = future_to_path[future]
            try:
                # Use timeout for future result
                result = future.result(timeout=FUTURE_TIMEOUT)
                with results_lock:
                    new_results[img_path] = result
                processed_count += 1

                # Progress
                elapsed = time.time() - start_time
                speed = processed_count / elapsed  if elapsed > 0 else 0
                eta = (total_to_process - processed_count) / speed if speed > 0 else 0
                print(f"\r⏱️  {processed_count}/{total_to_process} ({speed:.1f} img/s) — ETA: {int(eta)}s",
                      end="", flush=True, file=sys.stderr)

                # Checkpoint?
                now = time.time()
                if (processed_count % CHECKPOINT_EVERY == 0) or (now - last_checkpoint_time > CHECKPOINT_EVERY_SEC):
                    print(f"\n💾 Auto-checkpoint...", file=sys.stderr)
                    save_results_with_timeout(existing_results, new_results, args.output_pkl, timeout=3)
                    last_checkpoint_time = now

            except TimeoutError:
                print(f"\n⏰ Timeout processing {img_path}", file=sys.stderr)
                with results_lock:
                    new_results[img_path] = {"error": "timeout", "face_count": 0, "faces": []}
                processed_count += 1
            except Exception as e:
                print(f"\n❌ Error on {img_path}: {e}", file=sys.stderr)
                with results_lock:
                    new_results[img_path] = {"error": str(e), "face_count": 0, "faces": []}
                processed_count += 1

    # --- Final save with timeout ---
    print(f"\n💾 Final save...", file=sys.stderr)
    save_results_with_timeout(existing_results, new_results, args.output_pkl, timeout=MAX_SHUTDOWN_WAIT)

    # Force exit if shutdown was requested
    if shutdown_requested:
        print("👋 Exiting.", file=sys.stderr)
        os._exit(0)

    print("✨ Done!", file=sys.stderr)

if __name__ == "__main__":
    main()
