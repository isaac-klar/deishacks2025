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
        
        if "Event" not in data.columns:
            # Perform query-based visualization
            if query == "Attended":
                counts = data["Attended"].value_counts()
                labels = counts.index
                values = counts.values
                plt.figure(figsize=(8, 6))
                plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
                plt.title(f"Visualization for {query}")
            elif query == "Member Status":
                counts = data["Are you a member of Waltham Chamber of Commerce"].value_counts()
                labels = counts.index
                values = counts.values
                plt.figure(figsize=(8, 6))
                plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
                plt.title(f"Visualization for {query}")
            elif query == "Sales":
                counts = data["Did you pay for this event?"].value_counts()
                labels = ["Paid", "Unpaid"]
                sales = 0
                for val in counts.values():
                    if val == "Yes":
                        sales += 1000
                values = counts.values
                plt.figure(figsize=(8, 6))
                plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
                plt.title(f"Visualization for {query}")
            else:
                raise ValueError(f"Unknown query: {query}")

            # Create and save the visualization (for pie charts)
            plt.figure(figsize=(8, 6))
            plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
            plt.title(f"Visualization for {query}")
            visualization_path = os.path.join(output_folder, f"{query.replace(' ', '_')}.png")
            plt.savefig(visualization_path)
            plt.close()

            return visualization_path
        
        else:
            if query == "Attended":
                # Count how many people attended each event
                attendance_counts = data.groupby("Event")["Attended"].value_counts().unstack(fill_value=0)
                plt.figure(figsize=(10, 6))
                attendance_counts.plot(kind='bar', stacked=True)
                plt.title(f"Bar chart for {query} by Event")
                plt.xlabel('Event')
                plt.ylabel('Attendance Count')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                visualization_path = os.path.join(output_folder, f"{query.replace(' ', '_')}_bar.png")
                plt.savefig(visualization_path)
                plt.close()
                return visualization_path

            elif query == "Member Status":
                # Count how many members vs non-members for each event
                member_counts = data.groupby("Event")["Are you a member of Waltham Chamber of Commerce"].value_counts().unstack(fill_value=0)
                # Plot two bars side by side for each event: one for members, one for non-members
                plt.figure(figsize=(10, 6))
                member_counts.plot(kind='bar', width=0.8)
                plt.title(f"Bar chart for {query} by Event")
                plt.xlabel('Event')
                plt.ylabel('Member Status Count')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                visualization_path = os.path.join(output_folder, f"{query.replace(' ', '_')}_bar.png")
                plt.savefig(visualization_path)
                plt.close()
                return visualization_path

            elif query == "Sales":
                # Count how many people paid for each event, and multiply by $1,000
                sales_counts = data.groupby("Event")["Did you pay for this event?"].value_counts().unstack(fill_value=0)
                # Get only 'Yes' counts and multiply by 1000 for the dollar amount
                sales_amount = sales_counts.get("Yes", 0) * 1000
                plt.figure(figsize=(10, 6))
                sales_amount.plot(kind='bar')
                plt.title(f"Bar chart for {query} by Event")
                plt.xlabel('Event')
                plt.ylabel('Sales ($)')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                visualization_path = os.path.join(output_folder, f"{query.replace(' ', '_')}_bar.png")
                plt.savefig(visualization_path)
                plt.close()
                return visualization_path


            else:
                raise ValueError(f"Unknown query: {query}")