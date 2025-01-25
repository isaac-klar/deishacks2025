import pandas as pd
import matplotlib.pyplot as plt
import os

class EventsModeler:
    def model(self, filepath: str, query: str, output_folder: str, data=None) -> str:
        # Load data from file if provided
        if filepath:
            data = pd.read_excel(filepath)

        # DataFrame should be loaded at this point
        if data is None:
            raise ValueError("No data provided for modeling.")

        # Perform query-based visualization
        if query == "Attended":
            counts = data["Attended"].value_counts()
            labels = counts.index
            values = counts.values
        elif query == "Member Status":
            counts = data["Are you a member of Waltham Chamber of Commerce"].value_counts()
            labels = counts.index
            values = counts.values
        elif query == "Paid":
            labels = ["Low", "Medium", "High"]
            values = [
                (int(data["What are your Yearly Sales?"]) < 100000).sum(),
                ((int(data["What are your Yearly Sales?"]) >= 100000) & (data["Sales"] <= 500000)).sum(),
                (int(data["What are your Yearly Sales?"]) > 500000).sum(),
            ]
        else:
            raise ValueError(f"Unknown query: {query}")

        # Create and save the visualization
        plt.figure(figsize=(8, 6))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title(f"Visualization for {query}")
        visualization_path = os.path.join(output_folder, f"{query.replace(' ', '_')}.png")
        plt.savefig(visualization_path)
        plt.close()

        return visualization_path
