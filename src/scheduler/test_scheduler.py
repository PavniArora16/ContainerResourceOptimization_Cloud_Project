from src.scheduler.priority_manager import (
    Priority,
    assign_priority
)

from src.scheduler.resource_allocator import (
    allocate_resources
)

# -----------------------------------------
# Example predicted workloads
# -----------------------------------------

workloads = [

    {
        "task_id": "container_A",
        "priority": Priority.CRITICAL,
        "predicted_cpu": 4,
        "predicted_memory": 8
    },

    {
        "task_id": "container_B",
        "priority": Priority.MEDIUM,
        "predicted_cpu": 3,
        "predicted_memory": 4
    },

    {
        "task_id": "container_C",
        "priority": Priority.LOW,
        "predicted_cpu": 2,
        "predicted_memory": 3
    }
]


# -----------------------------------------
# Allocate resources
# -----------------------------------------

allocations = allocate_resources(
    workloads,
    total_cpu=6,
    total_memory=10
)


# -----------------------------------------
# Display results
# -----------------------------------------

print("--------------------------------")
print("RESOURCE ALLOCATION")
print("--------------------------------")

for allocation in allocations:

    print(
        f"\nTask: {allocation['task_id']}"
    )

    print(
        f"Priority: {allocation['priority'].name}"
    )

    print(
        f"Predicted CPU: "
        f"{allocation['predicted_cpu']}"
    )

    print(
        f"Allocated CPU: "
        f"{allocation['allocated_cpu']}"
    )

    print(
        f"Predicted Memory: "
        f"{allocation['predicted_memory']}"
    )

    print(
        f"Allocated Memory: "
        f"{allocation['allocated_memory']}"
    )