Markdown
# ♟️ Xiangqi AI Bot (Automated Chinese Chess Bot)

An automated Xiangqi (Chinese Chess) playing system that combines **Computer Vision** and a **Locally Hosted Large Language Model (LLM)**. The system automatically captures an Android screen, detects the board state using YOLO, enforces chess rules, prioritizes tactical opportunities, and executes optimal moves in real time.

---

## 🌟 Key Features

- **Real-Time Screen Capture:** Seamlessly mirrors Android screen frames to PC with ultra-low latency via `scrcpy`.
- **YOLO-Based Piece Detection:** Leverages Ultralytics YOLO to accurately detect, classify, and map Xiangqi pieces into a 10x9 matrix.
- **Robust Rule Engine & Move Filtering:**
  - Automatically filters out illegal moves (self-check, face-to-face King collisions).
  - Detects active checks and isolates only legal moves that resolve the check.
  - Prioritizes tactical opportunities: **⚡ CHECK > 🎯 CAPTURE > Normal Moves**.
- **Local LLM Decision Engine:** Connects to Ollama (e.g., `qwen2.5-coder:14b`) to evaluate positions and output structured JSON decisions along with natural language reasoning.
- **Auto-Execution:** Simulates screen touch events via ADB to execute moves directly on the target Android device.

---

## 🛠️ Tech Stack

| Component | Technology / Library | Description |
| :--- | :--- | :--- |
| **Screen Capture & Input** | [scrcpy](https://github.com/Genymobile/scrcpy) / ADB | Low-latency Android mirroring and touch event execution |
| **Computer Vision** | YOLO (Ultralytics) / OpenCV | Object detection, piece cropping, and matrix mapping |
| **AI Decision Engine** | [Ollama](https://ollama.com/) (`qwen2.5-coder:14b`) | Local LLM for strategic decision-making and structured JSON output |
| **Chess Rules Processing** | Python (Custom Engine) | Geometrical move validation, check detection, and move prioritization |

---

## 🏗️ System Architecture

```text
[ Android Device ] 
       │ (scrcpy / ADB Screen Capture)
       ▼
[ OpenCV / YOLO Detection ] ──► Converts visual state into a [10x9] Board Matrix
       │
       ▼
[ Chess Rules Engine ] ──────► Filters illegal moves & prioritizes tactical actions (Check/Capture)
       │
       ▼
[ Ollama (Qwen2.5-Coder) ] ──► Selects the optimal move index (Structured JSON response)
       │
       ▼
[ ADB Auto-Clicker ] ────────► Executes the touch gesture on the Android screen
📁 Project Structure
Plaintext
├── chess_rules.py        # Move validation, check detection, and priority sorting
├── agent.py              # LLM integration via Ollama and prompt handling
├── vision.py             # YOLO-based board recognition from screen frames
├── main.py               # Main control pipeline integrating vision, rules, LLM, and ADB
├── weights/
│   └── best.pt           # Custom trained YOLO model weights
└── README.md
📋 Prerequisites
Python 3.9+

Android Device: USB Debugging enabled.

scrcpy & ADB: Installed and added to system PATH.

Ollama: Installed locally with your target LLM model pulled:

Bash
ollama pull qwen2.5-coder:14b
🚀 Installation & Setup
1. Clone the Repository & Install Dependencies
Bash
git clone [https://github.com/your-username/xiangqi-ai-bot.git](https://github.com/your-username/xiangqi-ai-bot.git)
cd xiangqi-ai-bot

# Install required Python packages
pip install ultralytics opencv-python ollama
2. Connect Your Android Device
Connect your device via USB and verify the ADB connection:

Bash
adb devices
(Ensure your device appears as device, not unauthorized)

3. Run the Bot
Start the main pipeline:

Bash
python main.py
🤝 Contributing
Contributions regarding YOLO dataset optimizations, prompt improvements, or engine performance enhancements are welcome! Feel free to submit a Pull Request.

📄 License
Distributed under the MIT License.
