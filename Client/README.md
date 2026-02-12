# Auto.LLM Client

This is the client application for Auto.LLM, which allows an LLM to control a computer.

## Requirements

### Platform Support

- **Ubuntu with X11**: Fully supported.
- **Windows 11**: TODO (Planned support).
- **Wayland (Linux)**: Input injection may fail; X11 is recommended.

### Prerequisites

- Python 3.10+
- GGUF compatible model (text and optionally vision)

## Setup Instructions

### Linux (Ubuntu X11)

1. Install system dependencies:

   ```bash
   sudo apt-get install python3-tk python3-dev
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure the application:

   - Create/edit `config/client_config.json` with your model path.
   - Edit `config/info.txt` with your machine-specific information.

## Usage

Run the application from the project root using:

```bash
python3 -m Client.main
```

## Configuration

The `client_config.json` supports the following settings:
- `model_path`: Path to the GGUF model file.
- `model_directory`: Directory to search for models.
- `auto_start`: Boolean to enable/disable auto-start on login.
- `use_vision_model`: Boolean to use a separate vision model for screenshots.
- `vision_model_path`: Path to the vision GGUF model.
- `clip_model_path`: Path to the CLIP adapter model for vision capabilities.
- `context_size`: LLM context size.
- `n_gpu_layers`: Number of layers to offload to GPU.
