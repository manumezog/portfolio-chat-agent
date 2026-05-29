# Manuel Mezo — Technical Skills

This document lists Manuel Mezo's technical skills with evidence from real projects. Skills are grouped by domain.

---

## AI and Large Language Models

- **LLM APIs:** Claude (Anthropic), Gemini 2.5 Flash/Pro, GPT-4. Used in production for chat agents, RAG pipelines, and multi-agent orchestration.
- **Retrieval-Augmented Generation (RAG):** Built the RAG pipeline powering this portfolio chat agent using LangChain, ChromaDB, and Gemini Embedding 001. Understands chunking strategies, embedding model selection, retriever configuration, and conversational memory.
- **LangChain:** Proficient with LCEL chains, document loaders (PDF, DOCX, Markdown), text splitters, retrievers, prompt templates, `RunnableWithMessageHistory` for multi-turn conversations, `create_history_aware_retriever`, and `create_retrieval_chain`.
- **Multi-agent systems:** Built a multi-agent supply chain simulation featuring anomaly detection and autonomous agent coordination.
- **Voice AI:** Built voice-first interfaces using Retell.ai and Voiceflow for automated workflows.
- **Prompt engineering:** Designs system prompts that constrain LLM behaviour to facts-only answering, persona consistency, and concise professional tone.
- **Structured outputs:** Experience with tool use and JSON-schema constrained LLM outputs.

## Machine Learning and Forecasting

- **Time series forecasting:** Designed and built multiple production forecasting models at Amazon from scratch, including a 52-week rolling loads forecast for Transportation CAPEX (covering 130+ domiciles, 7 flows, 3.5 million truckload entries), and a long-term transportation forecast prototype that achieved comparable accuracy to an ML model (Prophet) while being fully explainable.
- **Model evaluation and backtesting:** Conducted systematic backtests comparing manual statistical models vs. ML baselines, quantifying accuracy at multiple granularity levels and communicating uncertainty ranges to business stakeholders.
- **Computer vision:** Fine-tuned a custom YOLOv8 object detection pipeline using an annotated dataset created in Roboflow. Applied custom spatial logic for tracking and real-time inference.
- **scikit-learn / Python ML stack:** Familiar with standard regression, classification, and statistical methods for applied analytics problems.

## Programming

- **Python:** Primary language for all AI and analytics work. Used for data processing (pandas, numpy), ML pipelines, API services (FastAPI), LangChain chains, embeddings, automation scripts, and notebook-based data analysis.
- **SQL:** Extensive professional use at Amazon writing custom queries against large-scale internal databases (QuickSight, Redshift-compatible systems). Independently built new analytical datasets from scratch when none existed.
- **Excel / VBA:** Advanced use for capacity modelling, financial models, and scenario simulation tools (built for McKinsey client engagements). Delivered a six-plant capacity planning simulation model for a pharma manufacturer.

## Data and BI Engineering

- **Amazon QuickSight:** Built, maintained, and redesigned the complete BI reporting infrastructure for Amazon EU External Fulfillment — 185 nodes, 400 staff users. Migrated from multi-platform fragmented stack to a unified QS architecture.
- **Tableau:** Used at Amazon for WHT operational dashboards; delivered Tableau interface for McKinsey pharma client tool.
- **ETL / data pipelines:** Designed query pipelines for large-scale operational reporting, including automated node-addition logic, metric-alignment across reports, and MBR automation saving ~6h/month.
- **ChromaDB:** Vector store used in production for this portfolio chat agent.
- **Firebase:** Used for real-time inventory sync in WMS camera-vision project.

## Cloud and Infrastructure

- **Docker:** Containerised the portfolio chat agent API (this project) for Hugging Face Spaces deployment.
- **FastAPI:** Backend framework for the portfolio chat agent REST API and other AI services.
- **Hugging Face Spaces:** Deployed production Docker containers for public-facing AI demos.
- **HuggingFace models:** Used `sentence-transformers/all-MiniLM-L6-v2` for production embeddings; experience with the Hugging Face Hub for model hosting.
- **Google Cloud / Gemini API:** Production use of Gemini 2.5 Flash for LLM inference and Gemini Embedding 001 for vector embeddings.

## Robotics and Engineering Tools

- **ROS2 (Robot Operating System 2):** Certified in ROS2 Basics (Python) via The Construct Robotics Institute (2026). Applied in robotics and autonomous systems projects.
- **Engineering simulation:** MSc-level experience with spacecraft trajectory modelling, Doppler data simulation, and closed-loop control system analysis.
- **MATLAB / Python for engineering:** Used in academic thesis research for spacecraft tracking data modelling.

## Operational Analytics Tools (Amazon-specific)

- **Minerva (Amazon internal):** Operational analysis and process improvement tool. Led EF's full integration into Minerva including development coordination, training, and rollout to hundreds of users.
- **Stay Clean (Amazon internal):** Operational health monitoring tool. Led EF integration process end-to-end.
- **WMS / AFT / FOS / TRB:** Worked directly with warehouse management systems and Amazon Transportation systems for technical integration of multi-item shipping capability at 3PL sites.

---

## Certifications and Education

- **MSc Aerospace Engineering** — Universidad Carlos III de Madrid + TU Delft (exchange). Thesis: "Open- and closed-loop Doppler data modelling for spacecraft tracking."
- **BSc Aerospace Engineering** — Universidad de León. Thesis: "Technical feasibility study for installation of a small-turbojet test bench."
- **BSc Mechanical Engineering** — Universidad de León. Thesis: "Preliminary design of the Electrical Power System of a spacecraft for an ISS mission."
- **Certificate of Proficiency: ROS2 Basics (Python)** — The Construct Robotics Institute, 2026.
- **Python for Data Science** — Microsoft certification, 2016.
