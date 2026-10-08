import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from "recharts";

function AllocationChart({ allocations = [] }) {
  const statusData = [
    {
      name: "FULL",
      value: allocations.filter(
        (item) => item.allocation_status === "FULL"
      ).length,
      fill: "#0088FE"
    },
    {
      name: "PARTIAL",
      value: allocations.filter(
        (item) => item.allocation_status === "PARTIAL"
      ).length,
      fill: "#00C49F"
    },
    {
      name: "UNMET",
      value: allocations.filter(
        (item) => item.allocation_status === "NOT_ALLOCATED"
      ).length,
      fill: "#FF8042"
    },
  ];

  const resourceData = allocations
    .slice(0, 15)
    .map((item, index) => ({
      task: `T${index + 1}`,
      cpu: Number(item.allocated_cpu || 0),
      memory: Number(item.allocated_memory || 0),
    }));

  return (
    <div className="allocation-charts">

      {/* Allocation Status */}
      <div className="chart-card">
        <h3>Allocation Status</h3>

        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={statusData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={90}
              label
            >
              {statusData.map((entry, index) => (
                <Cell key={index} />
              ))}
            </Pie>

            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* CPU vs Memory */}
      <div className="chart-card">
        <h3>Allocated CPU vs Memory</h3>

        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={resourceData}>
            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="task" />

            <YAxis />

            <Tooltip />

            <Legend />

            <Bar
              dataKey="cpu"
              name="CPU"
              fill="#8884d8"
            />

            <Bar
              dataKey="memory"
              name="Memory"
              fill="#82ca9d"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
}

export default AllocationChart;