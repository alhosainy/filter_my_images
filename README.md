# Face Recognition Studio

Face Recognition Studio is a tool for filtering images based on face recognition. It allows you to specify known images and scan a directory for images containing matching faces. You can also delete images after copying them to the output directory.

## Features

- Load known faces from a directory
- Scan a directory for images containing matching faces
- Copy matching images to an output directory
- Optionally delete images after copying
- GUI for easy configuration and execution

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/filter_my_images.git
    cd filter_my_images
    ```

2. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Command Line Interface (CLI)

To use the CLI, run the following command:

```sh
python face_recognition_cli.py --known <known_images_dir> --input <input_images_dir> --output <output_dir> [--tolerance <tolerance>] [--workers <num_workers>] [--delete-after-copy]
```

- `--known`: Directory with known images of you
- `--input`: Directory to scan for images
- `--output`: Directory to save matching images
- `--tolerance`: Tolerance for face matching (lower is stricter, default is 0.6)
- `--workers`: Number of worker processes for parallel processing (default is 4)
- `--delete-after-copy`: Delete the image after copying to the output directory

Example:

```sh
python face_recognition_cli.py --known known_people --input input_images --output output --tolerance 0.5 --delete-after-copy
```

### Graphical User Interface (GUI)

To use the GUI, run the following command:

```sh
python gui_wrapper.py
```

The GUI allows you to select directories, adjust settings, and start/stop the recognition process with ease.

## Configuration

The GUI saves the configuration to a `config.json` file in the project directory. You can manually edit this file or use the GUI to update the settings.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
