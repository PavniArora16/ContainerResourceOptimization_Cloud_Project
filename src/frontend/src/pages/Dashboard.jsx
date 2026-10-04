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

    try {

      setOptimizing(true);
      setError("");

      await runOptimization();

      await loadDashboard();

    } catch (err) {

      console.error(err);

      setError(
        "Optimization failed. Check the backend."
      );

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
    metrics?.allocation_status?.UNMET ?? 0;

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

          <button
            className="optimization-button"
            onClick={handleOptimization}
            disabled={optimizing}
          >

            {optimizing
              ? "Running..."
              : "Run Optimization"}

          </button>

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