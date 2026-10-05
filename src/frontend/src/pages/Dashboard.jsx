import { useEffect, useState } from "react";

import Navbar from "../components/Navbar";
import MetricCard from "../components/MetricCard";
import PredictionChart from "../components/PredictionChart";
import AllocationChart from "../components/AllocationChart";
import AllocationTable from "../components/AllocationTable";

import {
  getMetrics,
  getPredictions,
  getAllocations,
  runOptimization,
} from "../services/api";

function Dashboard() {

  const [metrics, setMetrics] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [allocations, setAllocations] = useState([]);

  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [optimizationStatus, setOptimizationStatus] = useState("");

  // ---------------------------------------
  // Load dashboard data
  // ---------------------------------------

  const loadDashboard = async () => {

    try {

      setLoading(true);
      setError("");

      const [
        metricsData,
        predictionsData,
        allocationsData,
      ] = await Promise.all([
        getMetrics(),
        getPredictions(),
        getAllocations(),
      ]);

      setMetrics(metricsData);

      setPredictions(
        predictionsData.predictions || []
      );

      setAllocations(
        allocationsData.allocations || []
      );

    } catch (err) {

      console.error(err);

      setError(
        "Unable to connect to the backend."
      );

    } finally {

      setLoading(false);

    }
  };

  // ---------------------------------------
  // Initial load
  // ---------------------------------------

  useEffect(() => {

    loadDashboard();

  }, []);

  // ---------------------------------------
  // Run optimization
  // ---------------------------------------

const handleOptimization = async () => {

  if (!selectedFile) {
    setError("Please select a CSV dataset first.");
    return;
  }

  try {

    setOptimizing(true);
    setError("");
    setOptimizationStatus("Uploading dataset...");

    const formData = new FormData();

    formData.append("file", selectedFile);

    const response = await runOptimization(formData);

    const jobId = response.job_id;

    if (!jobId) {
      throw new Error("Backend did not return a job ID.");
    }

    setOptimizationStatus(
      "Dataset uploaded. Optimization is running..."
    );

    // Wait for the background optimization job
    let completed = false;

    while (!completed) {

      await new Promise((resolve) =>
        setTimeout(resolve, 2000)
      );

      const statusResponse = await fetch(
        `http://127.0.0.1:8000/optimization-status/${jobId}`
      );

      if (!statusResponse.ok) {
        throw new Error(
          "Unable to check optimization status."
        );
      }

      const statusData = await statusResponse.json();
      console.log("OPTIMIZATION STATUS:", statusData);


      if (statusData.status === "completed") {

        completed = true;

        setOptimizationStatus(
          "Optimization completed successfully."
        );

        setOptimizing(false);

        await loadDashboard();

      }

      else if (statusData.status === "failed") {

        throw new Error(
          statusData.message ||
          "Optimization pipeline failed."
        );

      }

      else {

        setOptimizationStatus(
          "Optimization is running..."
        );

      }
    }

  } catch (err) {

    console.error(err);

    setError(
      err.message ||
      "Optimization failed. Check the backend."
    );

    setOptimizationStatus("");

  } finally {

    setOptimizing(false);

  }
};

  // ---------------------------------------
  // Loading
  // ---------------------------------------

  if (loading) {

    return (
      <div>
        <Navbar />

        <main className="dashboard">

          <div className="loading-message">
            Loading optimization data...
          </div>

        </main>
      </div>
    );
  }

  // ---------------------------------------
  // Metrics
  // ---------------------------------------

  const totalTasks =
    metrics?.total_tasks ?? 0;

  const cpuUtilization =
    metrics?.cpu?.utilization_percent ?? 0;

  const memoryUtilization =
    metrics?.memory?.utilization_percent ?? 0;

  const fullAllocations =
    metrics?.allocation_status?.FULL ?? 0;

  const partialAllocations =
    metrics?.allocation_status?.PARTIAL ?? 0;

  const unmetAllocations =
    metrics?.allocation_status?.NOT_ALLOCATED ?? 0

  return (

    <div>

      <Navbar />

      <main className="dashboard">

        {/* -------------------------------- */}
        {/* Header */}
        {/* -------------------------------- */}

        <div className="dashboard-header">

          <div>

            <h1>
              Container Resource Optimization
            </h1>

            <p>
              AI-powered workload prediction and
              intelligent resource allocation
            </p>

          </div>

          <div className="optimization-controls">

            <label className="file-upload">

              <span>
                {selectedFile
                  ? selectedFile.name
                  : "Choose CSV Dataset"}
              </span>

              <input
                type="file"
                accept=".csv"
                onChange={(e) => {
                  setSelectedFile(e.target.files[0] || null);
                }}
                disabled={optimizing}
              />

            </label>

            <button
              className="optimization-button"
              onClick={handleOptimization}
              disabled={optimizing || !selectedFile}
            >

              {optimizing
                ? "Running..."
                : "Run Optimization"}

            </button>

          </div>

        </div>

        {/* -------------------------------- */}
        {/* Error */}
        {/* -------------------------------- */}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {/* -------------------------------- */}
        {/* Metrics */}
        {/* -------------------------------- */}

        <section className="metrics-grid">

          <MetricCard
            title="Total Tasks"
            value={totalTasks}
            description="Tasks analyzed"
          />

          <MetricCard
            title="CPU Utilization"
            value={`${cpuUtilization.toFixed(2)}%`}
            description="Cluster CPU usage"
          />

          <MetricCard
            title="Memory Utilization"
            value={`${memoryUtilization.toFixed(2)}%`}
            description="Cluster memory usage"
          />

          <MetricCard
            title="Full Allocations"
            value={fullAllocations}
            description="Successfully allocated"
          />

        </section>

        {/* -------------------------------- */}
        {/* Allocation summary */}
        {/* -------------------------------- */}

        <section className="allocation-summary">

          <div className="summary-item full">
            <span>FULL</span>
            <strong>{fullAllocations}</strong>
          </div>

          <div className="summary-item partial">
            <span>PARTIAL</span>
            <strong>{partialAllocations}</strong>
          </div>

          <div className="summary-item unmet">
            <span>UNMET</span>
            <strong>{unmetAllocations}</strong>
          </div>

        </section>

        {/* -------------------------------- */}
        {/* Predictions */}
        {/* -------------------------------- */}

        <section className="dashboard-section">

          <h2>
            Resource Predictions
          </h2>

          <div className="chart-container">

            <PredictionChart
              predictions={predictions}
            />

          </div>

        </section>

        {/* -------------------------------- */}
        {/* Allocations */}
        {/* -------------------------------- */}

        <section className="dashboard-section">

          <h2>
            Resource Allocations
          </h2>

          <AllocationChart
            allocations={allocations}
          />

        </section>

        {/* -------------------------------- */}
        {/* Allocation table */}
        {/* -------------------------------- */}

        <section className="dashboard-section">

          <h2>
            Task Allocations
          </h2>

          <AllocationTable
            allocations={allocations}
          />

        </section>

      </main>

    </div>
  );
}

export default Dashboard;