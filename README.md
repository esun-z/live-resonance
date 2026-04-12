## Live Resonance

**English** | [中文](README_zh.md)

Play Blue Protocol: Star Resonance virtual instruments live with any MIDI device.

### Features

Live Resonance gets MIDI input from a MIDI device, and plays the corresponding keyboard events to the system. It is designed to help play in-game virtual instruments live using a MIDI device, bypassing the limitations of using a computer keyboard.

Core Features:

- Real-time MIDI input message listening and keyboard event output.
- Highly configurable MIDI to keyboard mapping and conflict resolution algorithms.
- Built-in presets for Blue Protocol: Star Resonance virtual instruments.
- Input filtering by channels, note pitch, and velocity.
- MIDI output re-routing to other MIDI devices.

### Installation

1. Download the latest release from the [Releases](https://github.com/esun-z/live-resonance/releases) page.
2. Extract the downloaded archive to a desired location.
3. Run `LiveResonance.exe` as an administrator to start the application.

### License

This project is licensed under GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

It is prohibited to package this project as closed-source software for sale. If you find any violations, please report it to the platform.

### TODOs

- [x] General MIDI Drum presets for in-game drum mapping.
- [ ] More control key support for guitar and bass mapping.
- [ ] Localization.

### Development

Astral uv is used for dependency management. Please [install Astral uv](https://docs.astral.sh/uv/getting-started/installation/) before proceeding.

1. Clone the repository:

    ```bash
    git clone https://github.com/esun-z/live-resonance.git
    cd live-resonance
    ```

2. Install dependencies:

    ```bash
    uv sync
    ```

3. Compile UI forms:
    ```bash
    uv run scripts/ui_compile.py
    ```

4. Run the application:

    ```bash
    uv run main.py
    ```

### Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

### Acknowledgements

Though this project is developed independently, it draws inspiration from the following projects:

- [MaaFreamework](https://github.com/MaaXYZ/MaaFramework)