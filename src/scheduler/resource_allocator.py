from src.scheduler.priority_manager import priority_score


def allocate_resources(workloads, total_cpu, total_memory):
    """
    Allocate available CPU and memory to workloads
    based on priority and predicted resource demand.
    """

    # Higher priority workloads are processed first
    workloads = sorted(
        workloads,
        key=lambda x: priority_score(x["priority"]),
        reverse=True
    )

    allocations = []

    remaining_cpu = total_cpu
    remaining_memory = total_memory

    for workload in workloads:

        requested_cpu = float(
            workload["predicted_cpu"]
        )

        requested_memory = float(
            workload["predicted_memory"]
        )

        # Allocate only what is currently available
        allocated_cpu = min(
            requested_cpu,
            remaining_cpu
        )

        allocated_memory = min(
            requested_memory,
            remaining_memory
        )

        # Calculate unmet demand
        unmet_cpu = (
            requested_cpu - allocated_cpu
        )

        unmet_memory = (
            requested_memory - allocated_memory
        )

        # Determine allocation status
        if (
            allocated_cpu >= requested_cpu
            and allocated_memory >= requested_memory
        ):
            status = "FULL"

        elif (
            allocated_cpu > 0
            or allocated_memory > 0
        ):
            status = "PARTIAL"

        else:
            status = "NOT_ALLOCATED"

        allocations.append({

            "task_id": workload["task_id"],

            "priority": workload["priority"],

            "predicted_cpu": requested_cpu,

            "predicted_memory": requested_memory,

            "allocated_cpu": allocated_cpu,

            "allocated_memory": allocated_memory,

            "unmet_cpu": unmet_cpu,

            "unmet_memory": unmet_memory,

            "allocation_status": status
        })

        # Update remaining resources
        remaining_cpu -= allocated_cpu
        remaining_memory -= allocated_memory

    return allocations