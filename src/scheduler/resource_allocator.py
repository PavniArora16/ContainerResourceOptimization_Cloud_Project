import pandas as pd


class ResourceAllocator:

    def __init__(self, total_cpu=1.0, total_memory=1.0):
        self.total_cpu = float(total_cpu)
        self.total_memory = float(total_memory)

    def allocate(self, workloads):

        df = workloads.copy()

        required_columns = [
            "task_id",
            "priority",
            "predicted_cpu",
            "predicted_memory",
            "start_time_seconds",
            "end_time_seconds",
        ]

        missing = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing required scheduler columns: {missing}"
            )

        # ---------------------------------------------------------
        # Clean timing information
        # ---------------------------------------------------------

        df["start_time_seconds"] = pd.to_numeric(
            df["start_time_seconds"],
            errors="coerce"
        )

        df["end_time_seconds"] = pd.to_numeric(
            df["end_time_seconds"],
            errors="coerce"
        )

        df["predicted_cpu"] = pd.to_numeric(
            df["predicted_cpu"],
            errors="coerce"
        ).clip(lower=0)

        df["predicted_memory"] = pd.to_numeric(
            df["predicted_memory"],
            errors="coerce"
        ).clip(lower=0)

        df["priority"] = pd.to_numeric(
            df["priority"],
            errors="coerce"
        ).fillna(1).astype(int)

        df = df.dropna(
            subset=[
                "task_id",
                "start_time_seconds",
                "end_time_seconds",
                "predicted_cpu",
                "predicted_memory"
            ]
        ).copy()

        # Invalid duration → treat as a zero-duration task
        df.loc[
            df["end_time_seconds"] < df["start_time_seconds"],
            "end_time_seconds"
        ] = df["start_time_seconds"]

        # ---------------------------------------------------------
        # Sort by start time first.
        #
        # Priority is used when multiple tasks are waiting/running
        # at the same scheduling point.
        # ---------------------------------------------------------

        df = df.sort_values(
            [
                "start_time_seconds",
                "priority"
            ],
            ascending=[
                True,
                False
            ]
        ).reset_index(drop=True)

        # ---------------------------------------------------------
        # Active tasks
        #
        # Each active task keeps its CPU/memory until its
        # end_time. After that time, resources are released.
        # ---------------------------------------------------------

        active_tasks = []

        results = []

        # ---------------------------------------------------------
        # Process each task chronologically
        # ---------------------------------------------------------

        for _, row in df.iterrows():

            current_time = float(
                row["start_time_seconds"]
            )

            # -----------------------------------------------------
            # RELEASE COMPLETED TASKS
            # -----------------------------------------------------

            remaining_active = []

            for active in active_tasks:

                if active["end_time"] <= current_time:

                    # Task completed.
                    # Its resources are automatically released.
                    continue

                remaining_active.append(active)

            active_tasks = remaining_active

            # -----------------------------------------------------
            # Calculate currently used resources
            # -----------------------------------------------------

            used_cpu = sum(
                task["allocated_cpu"]
                for task in active_tasks
            )

            used_memory = sum(
                task["allocated_memory"]
                for task in active_tasks
            )

            available_cpu = max(
                0.0,
                self.total_cpu - used_cpu
            )

            available_memory = max(
                0.0,
                self.total_memory - used_memory
            )

            requested_cpu = float(
                row["predicted_cpu"]
            )

            requested_memory = float(
                row["predicted_memory"]
            )

            # -----------------------------------------------------
            # ALLOCATION
            # -----------------------------------------------------

            allocated_cpu = min(
                requested_cpu,
                available_cpu
            )

            allocated_memory = min(
                requested_memory,
                available_memory
            )

            # -----------------------------------------------------
            # STATUS
            # -----------------------------------------------------

            cpu_fully_allocated = (
                abs(
                    requested_cpu - allocated_cpu
                ) < 1e-9
            )

            memory_fully_allocated = (
                abs(
                    requested_memory - allocated_memory
                ) < 1e-9
            )

            if (
                allocated_cpu == 0
                and allocated_memory == 0
                and (
                    requested_cpu > 0
                    or requested_memory > 0
                )
            ):
                status = "NOT_ALLOCATED"

            elif (
                cpu_fully_allocated
                and memory_fully_allocated
            ):
                status = "FULL"

            else:
                status = "PARTIAL"

            unmet_cpu = max(
                0.0,
                requested_cpu - allocated_cpu
            )

            unmet_memory = max(
                0.0,
                requested_memory - allocated_memory
            )

            # -----------------------------------------------------
            # Record result
            # -----------------------------------------------------

            results.append(
                {
                    "task_id": row["task_id"],
                    "priority": int(row["priority"]),

                    "predicted_cpu": requested_cpu,
                    "predicted_memory": requested_memory,

                    "allocated_cpu": allocated_cpu,
                    "allocated_memory": allocated_memory,

                    "unmet_cpu": unmet_cpu,
                    "unmet_memory": unmet_memory,

                    "allocation_status": status,

                    "start_time_seconds":
                        current_time,

                    "end_time_seconds":
                        float(row["end_time_seconds"]),

                    "cluster_cpu_utilization":
                        (
                            sum(
                                task["allocated_cpu"]
                                for task in active_tasks
                            )
                            + allocated_cpu
                        ) / self.total_cpu,

                    "cluster_memory_utilization":
                        (
                            sum(
                                task["allocated_memory"]
                                for task in active_tasks
                            )
                            + allocated_memory
                        ) / self.total_memory,
                }
            )

            # -----------------------------------------------------
            # Keep allocated task active until its end time
            # -----------------------------------------------------

            if allocated_cpu > 0 or allocated_memory > 0:

                active_tasks.append(
                    {
                        "task_id": row["task_id"],
                        "end_time":
                            float(row["end_time_seconds"]),
                        "allocated_cpu":
                            allocated_cpu,
                        "allocated_memory":
                            allocated_memory,
                    }
                )

        return pd.DataFrame(results)
    # ---------------------------------------------------------
# Backward-compatible scheduler function
# ---------------------------------------------------------

def allocate_resources(
    workloads,
    total_cpu=1.0,
    total_memory=1.0
):
    allocator = ResourceAllocator(
        total_cpu=total_cpu,
        total_memory=total_memory
    )

    workloads_df = pd.DataFrame(workloads)

    return allocator.allocate(
        workloads_df
    )