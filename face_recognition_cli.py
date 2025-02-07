import os
import argparse
import shutil
import logging
import concurrent.futures
import signal

import face_recognition

from tqdm import tqdm
# Attempt to import tqdm for a progress bar; if unavailable, proceed without it
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

import sys

import logging

# Configure logging to flush immediately
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

sys.stdout.reconfigure(line_buffering=True)  # Force unbuffered stdout output

stop_signal = False

def signal_handler(sig, frame):
    global stop_signal
    stop_signal = True
    logging.info("Stop signal received. Terminating process...")

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def load_known_faces(known_dir):
    """
    Load and encode known faces from the given directory.
    If an image file is corrupt or no face is detected, log the issue and skip the file.
    """
    known_encodings = []
    for filename in os.listdir(known_dir):
        if filename.lower().split(".")[-1] not in ["jpg", "jpeg", "png"]:
            continue
        image_path = os.path.join(known_dir, filename)
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if not encodings:
                logging.warning(f"No faces found in {filename}. Skipping...")
                continue
            known_encodings.append(encodings[0])  # Use the first detected face
        except Exception as e:
            logging.error(f"Error processing file {filename}: {e}")
    if not known_encodings:
        raise ValueError("No valid face encodings found in known directory")
    return known_encodings

def process_image(image_path, known_encodings, tolerance=0.6):
    """
    Check if the given image contains any face that matches one of the known encodings.
    Returns True if a match is found, False otherwise.
    """
    try:
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        for encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=tolerance)
            if any(matches):
                return True
    except Exception as e:
        logging.error(f"Error processing image {image_path}: {e}")
    return False

def process_image_wrapper(filename, input_dir, known_encodings, tolerance):
    global stop_signal
    if stop_signal:
        return filename, False
    image_path = os.path.join(input_dir, filename)
    match = process_image(image_path, known_encodings, tolerance)
    return filename, match

def main():
    global stop_signal
    # Set up command-line arguments
    parser = argparse.ArgumentParser(description="Filter images containing your face")
    parser.add_argument("--known", required=True, help="Directory with known images of you")
    parser.add_argument("--input", required=True, help="Directory to scan for images")
    parser.add_argument("--output", required=True, help="Directory to save matching images")
    parser.add_argument("--tolerance", type=float, default=0.6, help="Tolerance for face matching (lower is stricter)")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker processes for parallel processing")
    parser.add_argument("--delete-after-copy", action="store_true", help="Delete the image after copying to output directory")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Create the output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    logging.info("Loading known faces...")
    known_encodings = load_known_faces(args.known)

    # Get list of image files in the input directory
    image_files = [f for f in os.listdir(args.input) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    total_images = len(image_files)
    logging.info(f"Found {total_images} images in input directory.")

    # Set up progress bar if tqdm is available
    progress_bar = tqdm(total=total_images, desc="Processing images") if tqdm else None

    # Use ProcessPoolExecutor to process images in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(process_image_wrapper, filename, args.input, known_encodings, args.tolerance): filename
            for filename in image_files
        }
        for future in concurrent.futures.as_completed(futures):
            if stop_signal:
                break
            filename, match = future.result()
            if match:
                input_path = os.path.join(args.input, filename)
                output_path = os.path.join(args.output, filename)
                try:
                    shutil.copy(input_path, output_path)
                    logging.info(f"Match found and copied: {filename}")
                except Exception as e:
                    logging.error(f"Error copying image {filename}: {e}")
                if args.delete_after_copy:
                    try:
                        os.remove(input_path)
                        logging.info(f"Deleted image: {filename}")
                    except Exception as e:
                        logging.error(f"Error deleting image {filename}: {e}")
            if progress_bar:
                progress_bar.update(1)

    if progress_bar:
        progress_bar.close()
    logging.info(f"Done! Matching images saved to {args.output}")

if __name__ == "__main__":
    main()

# run the script

# python face_recognition_cli.py --known known_people --input input_images --output output --tolerance 0.5


# python face_filter.py \
# --known known_people \
# --input input_images \
# --output output \
# --tolerance 0.5