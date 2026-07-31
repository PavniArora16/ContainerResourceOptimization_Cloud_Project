# AI-Based Container Resource Optimization Framework for Smart Factory Applications using Predictive Autonomous Scheduling

## Team Members
- Pavni Arora
- Priyanshi Kapoor

## Problem Statement
Smart factories run mixed, unpredictable container workloads — deadline-critical control and sensor tasks alongside batch tasks like analytics and ML inference — on constrained, heterogeneous edge-cloud infrastructure. Existing AI-based container scheduling frameworks (reinforcement learning schedulers, hybrid autoscalers) are designed and validated for generic cloud or edge workloads, typically optimize a single resource dimension such as CPU alone, and react to load rather than predicting it. Existing smart-factory and IIoT container orchestration work, on the other hand, focuses on deployment and connectivity (Kubernetes edge clusters, MQTT/OPC-UA integration) but includes no learning-based scheduling intelligence. As a result, there is no framework that combines predictive, AI-driven scheduling with the deadline and resource constraints specific to smart factory workloads — leading to inefficient resource utilization, delayed response to demand spikes, and risk to time-critical industrial processes.

## Objectives
1. Develop a supervised ML model (Random Forest / LSTM) to predict container-level CPU and memory demand for smart factory workloads using historical usage data.
2. Design a priority-tagging mechanism that classifies containers as deadline-critical or batch, based on the workload's role in factory operations.
3. Integrate prediction output with Kubernetes autoscaling (HPA/VPA) to trigger earlier, demand-aware scaling decisions instead of purely reactive ones.
4. Evaluate the framework's improvement in resource utilization, scaling response time, and critical-task reliability compared to default Kubernetes scheduling.
5. Document an AWS-based deployment architecture (EKS, Lambda, SageMaker, CloudWatch) for the proposed framework.

## Proposed Architecture/Framework
The framework ingests sensor and machine data from the factory floor through AWS IoT Core, secured via Cognito and IAM. Incoming data is stored in Amazon S3 and used to train and run an Amazon SageMaker model that predicts near-term container resource demand. Predictions are passed to an AWS Lambda function, which acts as the scheduling trigger — translating predicted demand and task priority (deadline-critical vs. batch) into scaling decisions applied to an Amazon EKS-managed Kubernetes cluster. Cluster and container-level metrics are continuously monitored through Amazon CloudWatch, which triggers Amazon SNS notifications when anomalies or scaling events occur. This design layers predictive, priority-aware intelligence on top of Kubernetes' native autoscaling rather than replacing it — keeping the system realistic to implement while addressing the reactive-only and priority-blind limitations found across existing scheduling literature.

## Technology Stack
- **Containers/Orchestration:** Docker, Kubernetes (Minikube for local development, Amazon EKS for cloud deployment)
- **AI/ML:** Python, scikit-learn / TensorFlow (Random Forest or LSTM for demand prediction)
- **Cloud (AWS):** IoT Core, S3, SageMaker, Lambda, EKS, CloudWatch, SNS, IAM, Cognito
- **Backend:** Python (Flask/FastAPI) — to be finalized during implementation
- **Frontend:** React (or plain HTML/CSS/JS) — to be finalized during implementation
- **Database:** Amazon RDS or DynamoDB — to be finalized during implementation

## Dataset Details
A public cluster/workload trace dataset will be used to train and evaluate the resource demand prediction model — candidates include the Google Cluster Usage Traces and the Bitbrain dataset, both of which are established benchmarks used in prior scheduling and workload-prediction research reviewed in the literature survey. Dataset name, source, size, number of records/features, license, and required preprocessing steps will be finalized and documented in `dataset/dataset_description.pdf` once selection is complete.