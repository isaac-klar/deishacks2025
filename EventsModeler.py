import pandas as pd
import matplotlib.pyplot as plt
import os

class EventsModeler:
    def __init__(self):
        pass

    def model(self, filepath: str, query: str, output_folder: str) -> str:
        """
        Generate a visualization based on the query and save it as an image.

        Args:
            filepath (str): Path to the Excel file.
            query (str): The question/query to model data for.
            output_folder (str): Folder to save the visualization.

        Returns:
            str: Path to the generated visualization image.
        """
        # Load data
        df = pd.read_excel(filepath)

        mems = 0
        nons = 0

        if query == "Are you a member of Waltham Chamber of Commerce":
            for e in df["Are you a member of Waltham Chamber of Commerce"]:
                if str(e) == "Member":
                    mems += 1
                if str(e) == "Non-member":
                    nons += 1

        # Generate pie chart
        c = [mems, nons]
        labels = ["Members", "Non-members"]

        plt.figure(figsize=(6, 6))
        plt.pie(c, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title("Pie Chart: Members vs Non-members")

        # Save the visualization
        output_path = os.path.join(output_folder, "pie_chart_members.png")
        plt.savefig(output_path)
        plt.close()

        return output_path
