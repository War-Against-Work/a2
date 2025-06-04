# Claude CLI Context & Tasking Prompt for Project A2

**Instructions for Human Developer (Aaron):**
1.  Before each session with the Claude CLI, copy the entirety of this document.
2.  **CRITICAL:** Update the "## CURRENT SESSION FOCUS & TASK" section with the specific details for what you want to achieve in *this particular interaction*.
3.  Provide this entire updated prompt to the Claude CLI at the beginning of your interaction.
4.  If referencing specific code files not provided in this prompt, be prepared to paste their content if Claude cannot access your local filesystem.

---

## I. STANDING PROJECT CONTEXT (A2 ROBOT)

**1. Project Name & Core Goal:**
   - **Project:** A2 Robotic Assistant
   - **Core Goal:** Develop an expressive head/neck robotic assembly capable of intelligent, responsive human-robot interaction. This involves a hybrid cloud-local architecture leveraging Large Language Models (LLMs) for reasoning/dialogue and a custom Conversational Speech Model (CSM) for Text-to-Speech (TTS).
   - **Current Phase:** Phase 1 (Essential Core) - focus on foundational pipeline and core technology POCs.

**2. Master Project Directory:**
   - `/Users/aaronlax/Projects/A2/`

**3. Key Architectural & Planning Documents (Primary Sources of Truth):**
   - Overall Architecture: `/Users/aaronlax/Projects/A2/a2-docs/a2_hybrid_architecture_overview.md`
   - Phase 1 Plan: `/Users/aaronlax/Projects/A2/a2-docs/a2_phase_1_implementation_priorities.md`
   - All other design documents are located within `/Users/aaronlax/Projects/A2/a2-docs/` and should be referenced by name as needed.

**4. Modular Repository Structure (Each is a separate Git repo):**
   - `/Users/aaronlax/Projects/A2/a2-core/`: Main documentation hub.
   - `/Users/aaronlax/Projects/A2/a2-llm-containers/`: Docker setups for cloud LLMs (Mistral 7B + LoRAs) & CSM TTS.
   - `/Users/aaronlax/Projects/A2/a2-csm-tts/`: (Placeholder for future CSM-specific development, possibly a fork of `SesameAILabs/csm` or custom integration code).
   - `/Users/aaronlax/Projects/A2/a2-ros-ws/`: ROS 2 workspace for all onboard robot software (Pi & local RTX 4080 interaction).
     - Key new packages within `a2-ros-ws/src/`: `a2_interfaces` (custom messages), `a2_cloud_integration` (Cloud Gateway), `a2_teensy_interface`, `a2_dynamixel_interface`, `a2_l16_control`, `a2_local_state_cache`, `a2_execution_router`, `a2_fast_path_reflex`, `a2_local_sensor_processing`, `a2_audio_playback`.
   - `/Users/aaronlax/Projects/A2/a2-teensy-firmware/`: PlatformIO project for Teensy 4.1 firmware.
   - `/Users/aaronlax/Projects/A2/a2-pi-system/`: Pi OS configurations, global setup scripts, host system setup notes.

**5. Technology Stack Summary:**
   - **Languages:** Python (ROS 2 nodes, cloud services, LLM/CSM integration), C++ (Teensy firmware via PlatformIO, performance-critical ROS 2 nodes).
   - **Frameworks/Platforms:** ROS 2 Humble, PlatformIO, Docker, Docker Compose, FastAPI (for cloud services), PyTorch (for LLMs/CSM).
   - **Key Libraries/Tools:** Redis (MSSS), `rclpy`/`rclcpp`, `requests`/`aiohttp`, `huggingface_hub`, `transformers`, specific CSM libraries, Dynamixel SDK, standard Linux tools.
   - **Cloud Provider:** RunPod (target for cloud services).

**6. Development & Documentation Standards:**
   - **Documentation-Driven:** Design documents in `/Users/aaronlax/Projects/A2/a2-docs/` are the primary reference. AI assistance should align with these.
   - **Complete Document Regeneration:** Updates to design documents should result in a fully regenerated document incorporating changes, not just diffs.
   - **Code Style:**
     - Python: PEP 8, `ament_flake8` for ROS 2 nodes.
     - C++: ROS 2 style guidelines, `ament_cpplint` for ROS 2 nodes. PlatformIO default C++ standards.
     - Consistent commenting and clear variable/function naming.
   - **Testing:** Unit tests for critical modules. Integration tests for component interactions. POC verification as per `a2_phase_1_implementation_priorities.md`.
   - **Git:** Meaningful commit messages. Work in feature branches where appropriate.

---

## II. CURRENT SESSION FOCUS & TASK

**1. Current Sprint (from `/Users/aaronlax/Projects/A2/a2-docs/a2_phase_1_implementation_priorities.md`):**
   - "Sprint 1: Onboard Foundation, Safety & CI Setup (Weeks 1-4)"

**2. Specific Component/Module & Repository for this Session:**
   - Component: "Teensy Firmware: Core Project Setup, RTOS Tasks, and Basic UART Communication Logic"
   - Repository: `/Users/aaronlax/Projects/A2/a2-teensy-firmware/`

**3. Detailed Task Description for this Session:**
   -The overall goal for this session is to establish the foundational elements of the Teensy 4.1 firmware project. This includes:
    1.  Initialize/confirm the PlatformIO project structure within the `/Users/aaronlax/Projects/A2/a2-teensy-firmware/` repository. This includes creating a `platformio.ini` file configured for Teensy 4.1 and FreeRTOS.
    2.  In `/Users/aaronlax/Projects/A2/a2-teensy-firmware/src/main.cpp`, implement the basic FreeRTOS task stubs for `safetyMonitorTask`, `actuatorFeedbackTask`, `imuProcessingTask`, `serialCommunicationTask`, and `heartbeatTask` as outlined in `/Users/aaronlax/Projects/A2/a2-docs/teensy_firmware_design.md` (Section 3.1). Ensure tasks are created and the scheduler is started.
    3.  Create header (`.h`) and source (`.cpp`) files for a UART communications module (e.g., `serial_comms.h`, `serial_comms.cpp` in `/Users/aaronlax/Projects/A2/a2-teensy-firmware/src/` or a `lib/` subdirectory).
    4.  In this UART module, define the UART packet structure (start bytes, length, command ID, payload, checksum) as per `/Users/aaronlax/Projects/A2/a2-docs/teensy_firmware_design.md` (Section 4.1). Implement helper functions for packet creation (populating fields, calculating CRC16-CCITT checksum) and basic packet validation (checking start bytes, length, checksum).
    5.  Implement the `serialCommunicationTask` to handle sending packets from a FreeRTOS queue and receiving bytes from UART into a buffer for later parsing. Initially, it does not need to fully parse complex incoming packets, just detect potential start of packets.
    6.  Implement the `heartbeatTask` to blink an LED (e.g., `LED_BUILTIN`) and prepare a simple status/version packet (e.g., `CMD_TEENSY_FIRMWARE_VERSION` or a basic `CMD_TEENSY_TELEMETRY_PACKET` with placeholder data) to be sent via the `serialCommunicationTask` periodically (e.g., every 1 second).

**4. Primary Design Document(s) to Reference for THIS TASK (absolute paths):**
   - `/Users/aaronlax/Projects/A2/a2-docs/teensy_firmware_design.md` (Especially Sections 3.1 "RTOS Tasks", 4.1 "Frame Structure", 4.2 "Message Types")
   - `/Users/aaronlax/Projects/A2/a2-docs/a2_phase_1_implementation_priorities.md` (For Sprint 1 goals)

**5. Relevant Code File(s) to Create/Modify for THIS TASK (absolute paths):**
   - Create/Modify: `/Users/aaronlax/Projects/A2/a2-teensy-firmware/platformio.ini`
   - Create/Modify: `/Users/aaronlax/Projects/A2/a2-teensy-firmware/src/main.cpp`
   - Create: `/Users/aaronlax/Projects/A2/a2-teensy-firmware/src/serial_comms.h` (or `include/serial_comms.h`)
   - Create: `/Users/aaronlax/Projects/A2/a2-teensy-firmware/src/serial_comms.cpp`
   - Create: `/Users/aaronlax/Projects/A2/a2-teensy-firmware/src/config.h` (for constants like LED pin, UART settings - optional, good practice)

**(Optional) Paste RELEVANT snippets of existing code from the files above if needed for specific modifications:**
   ```text
   // No existing code yet for these new files.
   ```

**6. Specific Questions or Assistance Needed from Claude for THIS TASK:**
   - "Provide a well-structured `platformio.ini` file for a Teensy 4.1 project using FreeRTOS. Include common/useful build flags and library dependency management if any standard libraries are good for CRC or FreeRTOS itself."
   - "Suggest C++ struct(s) or class(es) for representing the UART packet and for the `CMD_TEENSY_FIRMWARE_VERSION` payload. Include a function for calculating CRC16-CCITT checksum over a buffer."
   - "Outline the C++ code structure for `serial_comms.h` and `serial_comms.cpp`, including function prototypes for initializing UART, sending a prepared packet (e.g., from a buffer/struct), and a non-blocking receive function to be called by `serialCommunicationTask`."
   - "Provide the FreeRTOS task creation calls in `main.cpp` for all five tasks, along with basic task function skeletons (loops with `vTaskDelayUntil` or similar for periodicity)."
   - "Show an example implementation of the `heartbeatTask` that toggles `LED_BUILTIN` and queues a version packet for sending by `serialCommunicationTask` using a FreeRTOS queue."
   - "Illustrate the core loop of `serialCommunicationTask`, showing how it might check a FreeRTOS queue for outgoing packets and check the UART for incoming bytes, buffering them for parsing (actual parsing of incoming can be a later step)."

---

## III. AI ASSISTANT (CLAUDE) RESPONSIBILITIES FOR THIS SESSION

1.  **Acknowledge Context:** Briefly confirm you have processed the "STANDING PROJECT CONTEXT" and the "CURRENT SESSION FOCUS & TASK."
2.  **Adhere to Design:** Base all code suggestions, architectural advice, and problem-solving on the A2 project's established design documents (especially those listed under "Primary Design Document(s) for THIS TASK") and the Phase 1 simplifications.
3.  **Code Generation:** Provide clean, well-commented, robust, and idiomatic C++ for PlatformIO/Teensy with FreeRTOS.
4.  **Iterative Refinement:** Be prepared to discuss, critique, and refine solutions.
5.  **Documentation Impact Assessment:** If the work done in this session implies changes or clarifications to ANY existing design documents, **you MUST explicitly list:**
    *   Which document(s) need updating (full path).
    *   The specific section(s) and suggested textual changes or additions.
6.  **Testing Guidance:** Briefly suggest how the implemented code/feature could be tested (e.g., "Connect Teensy to a PC serial terminal. Verify LED blinks and version packets are received. Send a known byte sequence to test basic receive buffering on Teensy via debug prints.").
7.  **Human Developer's Next Micro-Steps:** Conclude your main response by suggesting 1-3 immediate, actionable micro-steps for the human developer based on the output of this session.
8.  **"Pass the Torch" - Concluding Handoff:** End your *entire response* with the following strictly formatted section to ensure context for the next AI assistant instance or a future session:

    ```text
    ---
    **Next Step for Next AI Assistant:**
    *   **Previous Session (with this AI) Summary:** [AI: Concisely summarize what was specifically accomplished or decided in *this* interaction with you. E.g., "Generated platformio.ini, main.cpp with FreeRTOS task stubs, initial serial_comms.h/.cpp with UART packet structures, CRC16 function, and a basic heartbeatTask sending version packets. Discussed FreeRTOS queue usage for TX/RX buffers in serialCommunicationTask."]
    *   **Suggested Next Development Task for A2 Project:** [AI: Based on the completed work and Sprint 1 priorities, propose the *next logical, specific, and actionable coding/development task*. Reference relevant design document sections and file paths. E.g., "Flesh out the `serialCommunicationTask` in `/Users/aaronlax/Projects/A2/a2-teensy-firmware/src/serial_comms.cpp` to fully implement sending packets from its FreeRTOS queue and receiving bytes into a ring buffer, including start byte detection and checksum validation for incoming data, as per `/Users/aaronlax/Projects/A2/a2-docs/teensy_firmware_design.md` Sections 4.1 and 4.3."]
    ---
    ```