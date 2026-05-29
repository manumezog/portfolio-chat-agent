# Manuel Mezo — Side Projects and Independent Work

This document describes Manuel Mezo's independent AI, computer vision, and robotics projects built outside of his professional roles. All projects are publicly accessible and documented on his portfolio website (cv.manuelmezo.com) and GitHub (github.com/manumezog).

---

## Portfolio Chat Agent (This Project)

**Type:** Applied AI / RAG system | **Tech:** LangChain, ChromaDB, Gemini 2.5 Flash, FastAPI, Docker, Hugging Face Spaces | **GitHub:** manumezog/portfolio-chat-agent

An end-to-end Retrieval-Augmented Generation (RAG) system that answers questions about Manuel's background, professional experience, and projects. The agent is grounded in actual documents — CV, thesis reports, professional experience stories, and project descriptions — rather than relying on LLM memory alone.

The pipeline uses LangChain for document loading and chain orchestration, Google Gemini Embedding 001 for vector embeddings, ChromaDB as the vector store, and Gemini 2.5 Flash as the language model. The API is built with FastAPI, containerised with Docker, and deployed live on Hugging Face Spaces. The project demonstrates: RAG pipeline design, conversational memory with message history, production deployment via Docker, and REST API design for LLM applications.

---

## 3-Way Invoice Matching Agent (FastPay AI)

**Type:** Autonomous Accounts Payable back-office agent | **Tech:** Gemini 2.5 Flash, Next.js, Neon Postgres, full-stack TypeScript | **Live:** fastpay.mezapps.com

An autonomous agent that automates 3-way matching in Accounts Payable: it reads unstructured vendor invoices, cross-references them against Purchase Orders and WMS warehouse receipts, then approves, flags, or escalates discrepancies — with a full live reasoning trace visible to the user.

The project solves a real supply chain problem: manual invoice matching is slow, error-prone, and expensive. The agent uses structured LLM outputs to extract line items from messy PDFs, applies matching logic against structured database records, and produces audit-ready decisions. Built on an AI-powered SaaS architecture designed to be frugal, scalable, and secure.

---

## Omnichannel AI Customer Service Platform (Coffee Customer Service)

**Type:** Omnichannel AI customer service simulation | **Tech:** Retell.ai (voice), Voiceflow (web chat), Resend (email), Vercel | **Live:** coffee-cs.vercel.app

A full-stack omnichannel customer service simulation for a fictional coffee brand. Integrates three communication channels in one unified system: AI voice calls powered by Retell.ai, live web chat via Voiceflow, and automated email replies via Resend. All channels share real-time order lookup capability and unified conversation handling.

Demonstrates: multi-channel LLM orchestration, voice AI integration with real-time speech processing, webhook-based event handling across providers, and production deployment on Vercel.

---

## Forecasting Transportation Health Checks AI

**Type:** Multi-agent analytics automation | **Tech:** Google Agent Development Kit (ADK), Python, multi-agent framework | **GitHub:** manumezog/transportation-forecast-healthchecks-AI

A multi-agent framework that automates supply chain forecast oversight. Identifies version-over-version forecast spikes and historical accuracy gaps in European logistics networks. Agents autonomously detect anomalies, analyse root causes, and surface findings — replacing manual weekly review processes.

Built using Google's Agent Development Kit. Directly inspired by Manuel's professional experience in Amazon Transportation capacity planning, where identifying forecast anomalies and health-checking the weekly plan was a recurring manual task.

---

## SupplyChain Swarm Simulation

**Type:** Adversarial multi-agent simulation | **Tech:** Claude AI swarms (Anthropic), SQLite shared state, Python, multi-agent orchestration | **GitHub:** manumezog/SupplyChain-Swarm-Sim

An adversarial multi-agent supply chain simulation that uses Claude Code swarms to stress-test logistics resilience against synthetic "Black Swan" disruptions. Uses a turn-based, shared-state architecture with SQLite where parallel AI agents (Planner, Disruptor, and Market) compete: the Planner agent optimises the logistics network while the Disruptor agent attempts to destabilise it with synthetic shocks.

Demonstrates: multi-agent coordination, shared-state architecture for agent communication, adversarial simulation design, and the use of AI swarms for stress-testing business logic.

---

## X-Ray Medical Agent

**Type:** Autonomous diagnostic agent | **Tech:** Computer Vision, LLM reasoning, medical image analysis | **Live:** x-ray.mezapps.com

An autonomous diagnostic agent powered by computer vision for real-time medical image analysis. Analyses X-ray images and generates structured diagnostic observations. Demonstrates: medical image processing, LLM-powered clinical reasoning, and production deployment of a computer vision pipeline for a sensitive domain.

---

## VisionAI

**Type:** Real-time video analysis app | **Tech:** Gemini 2.5 Flash (multimodal), live video stream, natural language queries | **Live:** ai-vision.mezapps.com

Real-time video analysis application powered by Gemini 2.5 Flash. Detects and tracks objects in a live video feed via natural language queries — the user types what they want to find and the system returns live bounding boxes. Demonstrates: multimodal LLM integration, real-time video processing, and natural language interfaces to computer vision.

---

## MonumentScout

**Type:** Location-based AI discovery app | **Tech:** Geolocation APIs, AI-powered content generation | **Live:** monumentscout.mezapps.com

A location-based discovery app that uses the device's geolocation to identify nearby historical monuments and generate AI-powered explanations and context for each one. Demonstrates: geolocation API integration, LLM content generation, and mobile-first web app design.

---

## Voice Booking Agent

**Type:** AI voice assistant for calendar booking | **Tech:** Web Speech API, LLM orchestration, Google Calendar API | **Live:** reservas.mezapps.com

An AI voice assistant that books and manages Google Calendar appointments through natural language voice conversation. The user speaks their request; the agent parses intent, checks availability, and creates calendar events — entirely through voice. Demonstrates: Web Speech API integration, intent extraction from spoken input, Google Calendar API, and conversational task completion.

---

## WMS Prototype (Warehouse Management System)

**Type:** Mobile-first inventory management | **Tech:** On-device camera vision, Firebase real-time sync, barcode scanning | **Live:** mez-wms.mezapps.com | **GitHub:** manumezog/WMS

A mobile-first warehouse management system that uses the device camera for barcode scanning and syncs inventory in real time via Firebase. Designed as a proof-of-concept for a lean, camera-first WMS that requires no dedicated scanning hardware — relevant to Manuel's professional background in Amazon's 3PL and External Fulfillment operations. Demonstrates: on-device computer vision, real-time database sync with Firebase, and mobile-first UX for operational tools.

---

## YOLOv8 Custom Object Detection Pipeline (Parts I & II)

**Type:** Computer vision — fine-tuned detection and tracking | **Tech:** YOLOv8 (Ultralytics), Roboflow, ByteTrack, OpenCV, Python | **GitHub:** manumezog/vision-yolo-finetune

A two-part computer vision project:

**Part I — Custom YOLOv8 Fine-Tuning:** Built a custom object detection pipeline for a robot conveyor belt use case. Annotated a video-frame dataset in Roboflow with augmentation for motion blur and lighting variance. Fine-tuned YOLOv8n over 100 epochs, achieving approximately 97% mAP@50. Implemented real-time multi-object tracking.

**Part II — Spatial Logic with ByteTrack + OpenCV:** Added advanced spatial intelligence on top of the tracking engine. Implemented virtual polygon pick-zones using point-in-polygon logic and vertical throughput tripwires to count and register items on a moving conveyor. Demonstrates: the gap between training a model and deploying it with meaningful business logic.

---

## YOLOv8 Inference API — Production Deployment

**Type:** Production API for computer vision | **Tech:** YOLOv8, FastAPI, async task queue, Docker, Hugging Face Spaces | **Portfolio page:** yolo-async-api.html

Productionised the YOLOv8 model as a cloud REST API with production-grade engineering: an async task queue for multi-user concurrency, daemon-thread memory management to prevent container OOM crashes, Docker containerisation, and live deployment on Hugging Face Spaces. Demonstrates the full path from trained model to production API handling concurrent users.

---

## Realtime Traffic Data Logger and Analyzer

**Type:** Browser-based computer vision dashboard | **Tech:** YOLOv8, OpenCV, WebSocket, real-time telemetry

A browser dashboard displaying a live video feed where virtual gates can be defined to track, classify, and count vehicles and pedestrians in real time. Features live telemetry graphs and CSV export of counting data. Demonstrates: real-time CV + web integration, configurable spatial zones, and live data streaming.

---

## 3D Printed Robotic Arm with VLA Reasoning

**Type:** Physical robotics + AI reasoning | **Tech:** 4-axis robotic arm (3D printed), Gemini 1.5 Pro (Vision-Language-Action), servo control, Python | **Portfolio page:** robotic-arm-vla-project.html

A physical 4-axis robotic arm integrated with a cloud-based Vision-Language-Action (VLA) reasoning engine. Translates natural language voice commands through Gemini 1.5 Pro into precise local mechanical movements. The VLA model interprets the visual scene (via camera) and the verbal instruction to determine the correct servo positions. Demonstrates: physical robotics construction, servo control, vision-language-action models, and bridging cloud AI with local hardware actuation.

---

## Self-Balancing Robot — Simulation (ROS2 + Gazebo)

**Type:** Robotics simulation | **Tech:** ROS2, Gazebo, PID control, sensor modelling, Python | **GitHub:** manumezog/self-balancing-robot-ros2-simulation

A ROS2 simulation of a self-balancing robot built in Gazebo. Focuses on sensor modelling, odometry, and control loop tuning for the inverted-pendulum balancing problem. Built as the simulation precursor to a physical hardware deployment.

---

## Self-Balancing Robot — Real Hardware (Arduino + ROS2)

**Type:** Physical robotics | **Tech:** Arduino, IMU, PID control, motor actuation, ROS2 | **GitHub:** manumezog/self-balancing-robot-ros2-real

Physical deployment of the simulation: implements PID control, IMU sensor filtering, and motor actuation on real Arduino hardware. Demonstrates the translation from simulation to real-world deployment including hardware calibration, noise filtering, and real-time control loop constraints.

---

## ROS2 Wall Follower Robot

**Type:** Autonomous navigation | **Tech:** ROS2, Python, multithreading, LIDAR | **GitHub:** manumezog/ROS2-course-wall-follower-robot

Autonomous navigation logic using Python and multithreading to parse LIDAR sensor data and autonomously follow walls in a simulated environment. Built as part of ROS2 certification coursework and extended with additional experimentation.

---

## Personal Portfolio Website (cv.manuelmezo.com)

**Type:** Interactive web CV | **Tech:** HTML, CSS, JavaScript, Firebase hosting

An AI-developed interactive portfolio website showcasing Manuel's professional experience, education, projects, and interests. Sections cover: professional timeline (Amazon, McKinsey), GenAI projects, computer vision projects, robotics projects, and personal interests. Designed and developed using AI-assisted coding. Demonstrates: modern web development, responsive design, and AI-assisted software development workflows.

---
