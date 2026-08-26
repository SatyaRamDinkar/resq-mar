# Chapter 1: Introduction

## 1.1 Background and Motivation
The frequency and intensity of natural disasters have seen a global increase, placing unprecedented strain on emergency response infrastructures. According to the United Nations Office for Disaster Risk Reduction (UNDRR), climate-related disasters have surged, necessitating highly coordinated, rapid response mechanisms. Sri Lanka remains particularly vulnerable to a spectrum of natural hazards, including localized flooding, landslides, and seismic aftershocks. Current emergency response systems often rely on centralized, manual dispatch protocols that suffer from severe bottlenecks during peak crisis periods. These legacy systems are heavily cloud-dependent, rendering them fragile when local communication infrastructure is compromised by the disaster itself. Consequently, there is an urgent need for an intelligent, decentralized, and resilient emergency response framework capable of real-time coordination without absolute reliance on external cloud services.

## 1.2 Problem Statement
Existing Computer-Aided Dispatch (CAD) systems exhibit several critical failure points during large-scale disasters. First, they fail catastrophically when internet connectivity drops, as they depend on cloud-hosted routing and decision engines. Second, traditional static vehicle routing algorithms cannot adapt to dynamic disaster conditions, such as sudden road blockages, leading to vast computational waste when continuously re-solving routes. Third, fully automated AI systems lack necessary human oversight in life-or-death decisions, presenting severe ethical and operational risks. Finally, modern emergency logistics lack multi-modal resource coordination, specifically the symbiotic deployment of ground vehicles (trucks) and aerial units (drones) to bypass physical infrastructure failures.

## 1.3 Research Questions
This project seeks to address the aforementioned gaps through the following research questions:
- RQ1: How can agentic Retrieval-Augmented Generation (RAG) improve Standard Operating Procedure (SOP) retrieval accuracy and plan completeness over naive single-pass RAG?
- RQ2: How can Adaptive Event-Triggered (AET) routing reduce computational overhead compared to continuous optimization models?
- RQ3: How can truck-drone collaborative dispatch algorithms improve geographic coverage in areas with severed road networks?
- RQ4: How can the deployment of Edge Small Language Models (SLMs) provide system resilience when cloud connectivity is unavailable?

## 1.4 Objectives
The primary objective of this capstone project is to design, implement, and evaluate ResQ-MAR, an AI-Powered Multi-Agent Emergency Response System. Specific objectives include:
- Building a modular, multi-agent system utilizing specialized AI agents (Intake, Metadata, Planner, Router, Comms) using the AutoGen AG2 framework.
- Implementing an iterative, 4-step agentic RAG pipeline featuring assessment and re-retrieval mechanisms.
- Designing an AET adaptive routing engine powered by Google OR-Tools to minimize redundant solver calls.
- Developing a collaborative truck-drone dispatch model to guarantee last-mile access.
- Deploying edge-capable SLMs (e.g., Phi-3-mini) for resilient, offline operation.
- Creating a real-time Streamlit dashboard with a Human-in-the-Loop approval panel for safe operational oversight.

## 1.5 Scope and Limitations
The scope of this project is confined to the software architecture, multi-agent coordination logic, and simulation-based evaluation of the ResQ-MAR system within a synthesized Sri Lankan geographic context (Colombo and surrounding districts). 
Limitations include the absence of real hardware deployment (actual vehicles and drones) and the use of simulated LLM responses for the high-volume benchmarks due to local compute constraints. Furthermore, the incident datasets are synthetic, although they are modeled closely on real 911 dispatch transcripts.

## 1.6 Report Organization
This report is organized into six primary chapters. Chapter 1 introduces the context, problem, and objectives. Chapter 2 reviews the existing literature on multi-agent systems, RAG, and vehicle routing. Chapter 3 details the architectural design and philosophy of the ResQ-MAR system. Chapter 4 documents the step-by-step implementation phases and software engineering practices employed. Chapter 5 presents the quantitative evaluation, benchmarks, and results. Finally, Chapter 6 summarizes the contributions, acknowledges limitations, and proposes directions for future research.
