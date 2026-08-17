# 🎯 Fake News Detection App

An intelligent web application for detecting fake English-language news articles using machine learning (ML) techniques and large language models (LLMs). The application enables users to identify misinformation and manage classification models with comprehensive analytics.

## 🛠 Technologies

- **Python** — Backend programming language
- **Django** — Web framework
- **PostgreSQL** — Database management system
- **Docker & Docker Compose** — Containerization and orchestration
- **XGBoost** — Gradient boosting classifier
- **Google Gemini text-embedding-004** — LLM for text embeddings
- **scikit-learn** — ML library
- **pandas** — Data processing and analysis
- **Bootstrap 5** — Frontend styling

## ✨ Features

- **Fake News Detection** — Accurately identify fake English-language news using ML models
- **Multi-Model Support** — Create, use and configure different trained models
- **User Authentication** — Manage user accounts (via django-allauth)
- **Model Management** — Create and configure classification models
    - **Feature Engineering** — Select and manage features used in model training
    - **Parameter Configuration** — Adjust model parameters for optimal performance
- **Analytics Dashboard** — Track model accuracy and detection statistics
- **Attempt History** — View and analyze previous detection attempts

## 💡 The Project

This application was developed as a bachelor's thesis project aimed at improving fake news detection accuracy of existing approaches. The solution combines the power of LLMs with classical ML approaches to create a robust fake news detection system.

The application allows users to:
- Submit news articles for fake news classification
- Evaluate classification models
- Manage and configure models with different feature and parameter sets
- Generate analytical reports on model performance

The system leverages Google Gemini's text-embedding-004 model to generate semantic embeddings of news content, which are then processed through XGBoost classifiers for accurate fake news identification.

## 🚀 Running the Project

### Prerequisites
- Docker and Docker Compose installed
- Environment variables configured (.env file)

### Quick Start

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd Fake-News-Detection-App
   ```

2. Configure environment variables: create a `.env` file in the project root and fill it out according to .env.dist

3. Build and run with Docker Compose
   ```bash
   docker-compose up --build
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```