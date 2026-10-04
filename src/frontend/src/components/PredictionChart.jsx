import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function PredictionChart({ predictions }) {
  const chartData = predictions.slice(0, 20).map((item, index) => ({
    task: index + 1,
    actualCPU: Number(item.cpu_usage),
    predictedCPU: Number(item.predicted_cpu),
    actualMemory: Number(item.memory_usage),
    predictedMemory: Number(item.predicted_memory),
  }));

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis
            dataKey="task"
            label={{
              value: "Task",
              position: "insideBottom",
              offset: -5,
            }}
          />

          <YAxis />

          <Tooltip />

          <Legend />

          <Line
            type="monotone"
            dataKey="actualCPU"
            name="Actual CPU"
            stroke="#2563eb"
            dot={false}
          />

          <Line
            type="monotone"
            dataKey="predictedCPU"
            name="Predicted CPU"
            stroke="#ef4444"
            dot={false}
          />

          <Line
            type="monotone"
            dataKey="actualMemory"
            name="Actual Memory"
            stroke="#16a34a"
            dot={false}
          />

          <Line
            type="monotone"
            dataKey="predictedMemory"
            name="Predicted Memory"
            stroke="#f59e0b"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PredictionChart;