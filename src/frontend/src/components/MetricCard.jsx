function MetricCard({ title, value, description }) {
  return (
    <div className="metric-card">
      <h3>{title}</h3>

      <div className="metric-value">
        {value}
      </div>

      <p>{description}</p>
    </div>
  );
}

export default MetricCard;