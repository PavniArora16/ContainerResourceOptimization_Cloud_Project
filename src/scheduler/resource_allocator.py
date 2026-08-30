from src.scheduler.priority_manager import priority_score

def allocate_resources(workloads, total_cpu, total_memory):
    """
    Allocate available CPU and memory to workloads
    based on predicted demand and priority.
    """

    workloads = sorted(
        workloads,
        key=lambda x: priority_score(x["priority"]),
        reverse=True
    )

    allocations = []

    remaining_cpu = total_cpu
    remaining_memory = total_memory

    for workload in workloads:

        requested_cpu = workload["predicted_cpu"]
        requested_memory = workload["predicted_memory"]

        allocated_cpu = min(
            requested_cpu,
            remaining_cpu
        )

        allocated_memory = min(
            requested_memory,
            remaining_memory
        )

        allocations.append({
            "task_id": workload["task_id"],
            "priority": workload["priority"],
            "predicted_cpu": requested_cpu,
            "predicted_memory": requested_memory,
            "allocated_cpu": allocated_cpu,
            "allocated_memory": allocated_memory
        })

        remaining_cpu -= allocated_cpu
        remaining_memory -= allocated_memory

    return allocations