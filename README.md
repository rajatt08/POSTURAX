# PosturaX

### Real-time posture monitoring system using ESP32, MPU6050, FastAPI, and a behavioural intervention engine to improve workplace ergonomics and posture awareness

![ESP32](https://img.shields.io/badge/ESP32-IoT-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![MPU6050](https://img.shields.io/badge/MPU6050-IMU-orange)
![Status](https://img.shields.io/badge/Project-Active-success)

PosturaX is an intelligent wearable posture monitoring system developed by **Team MOONGFALI**. The system continuously monitors a user's sitting posture using an MPU6050 sensor and ESP32 microcontroller, detects unhealthy posture patterns in real time, and provides progressive behavioural interventions to encourage healthier sitting habits.

The project aims to reduce posture-related health issues such as neck pain, back pain, shoulder strain, and long-term musculoskeletal disorders commonly experienced by students, office workers, programmers, and remote professionals.

---

# Problem Statement

Millions of people spend long hours sitting in front of computers and often develop poor posture habits without realizing it. Continuous slouching can lead to:

- Neck pain
- Back pain
- Shoulder strain
- Reduced productivity
- Long-term musculoskeletal disorders

Most existing solutions only monitor posture and provide simple alerts. They do not actively encourage behavioural correction.

---

# Our Solution

PosturaX combines wearable sensing, IoT connectivity, real-time analytics, and behavioural intervention techniques to create lasting posture awareness.

The system continuously monitors body orientation and classifies posture as:

- Good Posture
- Forward Slouching
- Backward Slouching

When prolonged poor posture is detected, PosturaX triggers a progressive intervention sequence:

### Level 1 – Reminder Notification
Gentle reminder to correct posture.

### Level 2 – Warning Alert
Strong warning if slouching continues.

### Level 3 – Critical Intervention
Screen overlay appears until posture is corrected.

---

# Key Features

## Real-Time Posture Monitoring
- Continuous posture tracking
- Pitch angle analysis
- Forward slouch detection
- Backward slouch detection

## Intelligent State Machine
- Continuous slouch duration tracking
- Recovery period validation
- False trigger prevention
- Behavioural intervention logic

## Web Dashboard
- Live posture telemetry
- Current pitch visualization
- Posture status display
- Slouch duration monitoring
- Warning history logs
- Hardware connection monitoring

## Behavioural Intervention System
- Browser notifications
- Warning alerts
- Screen overlay interventions
- Progressive escalation mechanism

---

# System Architecture

```text
MPU6050 Sensor
        │
        ▼
      ESP32
        │
     WiFi
        │
        ▼
     FastAPI
     Backend
        │
        ▼
 Posture Processor
        │
        ▼
  State Machine
        │
        ▼
Intervention Engine
        │
        ▼
 Web Dashboard
```

# Hardware Components

- ESP32 Development Board
- MPU6050 IMU Sensor
- Wearable Mounting Unit
- USB Power Supply

---

# Software Stack

## Backend
- FastAPI
- Python

## Frontend
- HTML
- CSS
- JavaScript
- Chart.js

## Embedded
- ESP32 Firmware
- MPU6050 Sensor Integration

---

# Repository Structure

```text
POSTURAX/
│
├── Backend/
│   ├── API services
│   └── Telemetry handling
│
├── Frontend/
│   ├── Dashboard UI
│   └── Real-time charts
│
├── Posture/
│   ├── calibrate.py
│   ├── posture_processor.py
│   ├── state_machine.py
│   └── __init__.py
│
├── Interventions/
│   └── Alert management
│
├── Esp32hardwarecode/
│   └── ESP32 firmware
│
└── README.md
```

# Applications

- Students
- Office Employees
- Remote Workers
- Software Developers
- Educational Institutions
- Corporate Workspaces
- Healthcare Monitoring

# Future Enhancements

- Mobile Application
- AI-Based Posture Prediction
- Cloud Analytics
- Personalized Health Reports
- Workplace Wellness Integration

# Author

Rajat Tripathi

Electronics Engineering (IOT)

J.C. Bose University of Science and Technology, YMCA, Faridabad
