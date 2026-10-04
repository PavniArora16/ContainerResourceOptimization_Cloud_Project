function AllocationTable({ allocations = [] }) {
  return (
    <div className="table-wrapper">

      <table className="allocation-table">

        <thead>
          <tr>
            <th>Task ID</th>
            <th>Priority</th>
            <th>Predicted CPU</th>
            <th>Predicted Memory</th>
            <th>Allocated CPU</th>
            <th>Allocated Memory</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>

          {allocations.map((item, index) => (
            <tr key={`${item.task_id}-${index}`}>

              <td>{item.task_id}</td>

              <td>
                <span className="priority-badge">
                  {item.priority}
                </span>
              </td>

              <td>
                {Number(item.predicted_cpu || 0).toFixed(4)}
              </td>

              <td>
                {Number(item.predicted_memory || 0).toFixed(4)}
              </td>

              <td>
                {Number(item.allocated_cpu || 0).toFixed(4)}
              </td>

              <td>
                {Number(item.allocated_memory || 0).toFixed(4)}
              </td>

              <td>
                <span
                  className={`status-badge ${
                    item.allocation_status?.toLowerCase()
                  }`}
                >
                  {item.allocation_status}
                </span>
              </td>

            </tr>
          ))}

        </tbody>

      </table>

    </div>
  );
}

export default AllocationTable;