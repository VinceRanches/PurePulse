# PurePulse: An End-to-End Workflow for ML-Powered Air Quality Prediction and Alerting

## Overview

PurePulse is an integrated system designed to predict urban air quality and issue timely public alerts using machine learning (ML) techniques. The system addresses the growing public health concerns associated with particulate matter (PM) pollution, which is linked to increased cardiovascular and respiratory diseases. By leveraging real-time data from multiple sources and advanced ML models, PurePulse provides accurate one-hour and one-day-ahead air quality predictions, enabling proactive measures by city authorities and raising public awareness through targeted notifications.

This project is developed as part of a thesis titled **"An End-to-End Workflow for ML-Powered Air Quality Prediction and Alerting"**. The system integrates standalone solutions into a cohesive pipeline, facilitating real-time data ingestion, processing, prediction, alerting, and feedback for continuous improvement.

## Thesis Abstract

Poor air quality and particulate matter (PM) pollution have been associated with increased cardiovascular and respiratory diseases, with scientists expecting a further increase in PM concentrations due to climate change. This thesis aims to integrate existing standalone solutions for urban air quality prediction into a single end-to-end system capable of handling the complete prediction workflow and providing tools for public awareness and environmental policy-making. The system facilitates:

1. **Real-time data gathering and cleaning** from multiple open sources, including air quality and PM sensors, traffic patterns, weather forecasts, urban agglomeration/design, industrial emissions, and out-of-distribution events from news items.
2. **ML-powered predictions** using pre-trained Long Short-Term Memory (LSTM) Neural Networks.
3. **Public notification channels** such as social networks and targeted alerts.
4. **A feedback loop** to improve LSTM predictions.

The integrated system enables timely notifications to citizens about increased PM concentrations (one-hour and one-day-ahead forecasts) and empowers city authorities to implement proactive measures, such as traffic regulation and public advisories, to mitigate the adverse effects of air pollution and safeguard public health.

## System Architecture

PurePulse is built as a microservices-based architecture, orchestrated using Docker Compose. The system comprises the following key components:

- **Shared Infrastructure**:
  - **TimescaleDB**: A time-series database for storing air quality, traffic, weather, and other relevant data.
  - **Kafka & Zookeeper**: A messaging system for real-time data streaming between services.
  
- **Microservices**:
  - **API Gateway**: The single entry point for external requests, routing them to appropriate microservices.
  - **ETL Service**: Collects, cleans, and processes real-time data from open sources—e.g., air-quality sensors, and weather APIs—then transforms it for storage and model input.
  - **Model Service**: Runs pre-trained LSTM models for air quality predictions.
  - **Alerting Service**: Manages notifications via social networks and targeted alerts.
  - **Feedback Service**: Collects feedback to refine and improve prediction models.

- **Networks**:
  - `purepulse_net`: Internal network for communication between services.

- **Volumes**:
  - Persistent storage for TimescaleDB data.
  - Shared code and data volumes for microservices.

The system is containerized using Docker, ensuring scalability, portability, and ease of deployment.

## Project Structure

The project is organized as follows:

```
purepulse/
├── alerting-service/           # Manages notifications and alerts
│   ├── app/                   # Core application code
│   ├── Dockerfile             # Docker configuration
│   └── requirements.txt       # Python dependencies
├── api_gateway/               # Single entry point for external requests
│   ├── app/                   # Core application code
│   ├── Dockerfile             # Docker configuration
│   └── requirements.txt       # Python dependencies
├── etl-service/               # Data processing and transformation
│   ├── app/                   # Core application code
│   ├── Dockerfile             # Docker configuration
│   └── requirements.txt       # Python dependencies
├── feedback-service/          # Manages feedback for model improvement
│   ├── app/                   # Core application code
│   ├── Dockerfile             # Docker configuration
│   └── requirements.txt       # Python dependencies
├── model-service/             # Runs LSTM-based prediction models
│   ├── app/                   # Core application code
│   ├── Dockerfile             # Docker configuration
│   └── requirements.txt       # Python dependencies
├── shared/                    # Shared code and utilities
├── timescaledb/               # Database initialization scripts
│   └── init/
│       └── 01-init.sql        # SQL script for database setup
├── docker-compose.yml         # Orchestrates microservices
└── README.md                  # Project documentation
```

Each microservice follows a modular structure with subdirectories for controllers, routes, models, services, and helpers to ensure clean code organization.

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Git

### Installation Steps
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd purepulse
   ```

2. **Build and Run the Services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the API Gateway**:
   The API gateway is exposed on `http://localhost:8000`. Refer to the API documentation (to be implemented in `api_gateway/app/routes`) for available endpoints.

4. **Database Setup**:
   TimescaleDB is automatically initialized using the `01-init.sql` script in the `timescaledb/init` directory.

5. **Verify Services**:
   - TimescaleDB: `http://localhost:5432`
   - Kafka: `http://localhost:9092`
   - Microservices: Ports `8010` (etl), `8020` (model), `8030` (alerting), `8040` (feedback)

## Usage

1**Data Processing**:
   - The `etl-service` Collects real-time data from configured open sources—e.g., air-quality sensors and weather APIs—and cleans and transforms the raw data for model consumption.

2**Prediction**:
   - The `model-service` uses pre-trained LSTM models to generate one-hour and one-day-ahead PM concentration predictions.

3**Alerting**:
   - The `alerting-service` sends notifications via social networks (e.g., X Platform) and targeted channels when PM levels exceed thresholds.

4**Feedback Loop**:
   - The `feedback-service` collects user feedback and observed air quality data to refine the LSTM models.

## Future Work

- **API Documentation**: Complete Swagger/OpenAPI documentation for the API gateway.
- **Model Optimization**: Explore additional ML models (e.g., Transformer-based models) for improved accuracy.
- **Scalability**: Implement horizontal scaling for high-traffic scenarios.
- **Public Interface**: Develop a user-facing web or mobile application for real-time air quality updates.
