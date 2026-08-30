import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# Load predictions
# --------------------------------------------------

df = pd.read_csv(
    "results/predictions.csv"
)


# --------------------------------------------------
# CPU prediction graph
# --------------------------------------------------

plt.figure(figsize=(10, 5))

plt.plot(
    df["next_cpu"].values[:200],
    label="Actual CPU"
)

plt.plot(
    df["predicted_cpu"].values[:200],
    label="Predicted CPU"
)

plt.xlabel("Test observation")

plt.ylabel("CPU usage")

plt.title(
    "Actual vs Predicted CPU Usage"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "results/cpu_prediction.png"
)

plt.close()


# --------------------------------------------------
# Memory prediction graph
# --------------------------------------------------

plt.figure(figsize=(10, 5))

plt.plot(
    df["next_memory"].values[:200],
    label="Actual Memory"
)

plt.plot(
    df["predicted_memory"].values[:200],
    label="Predicted Memory"
)

plt.xlabel("Test observation")

plt.ylabel("Memory usage")

plt.title(
    "Actual vs Predicted Memory Usage"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "results/memory_prediction.png"
)

plt.close()


print("Evaluation graphs generated.")

print(
    "Saved: results/cpu_prediction.png"
)

print(
    "Saved: results/memory_prediction.png"
)