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
                member_sales = 0
                non_member_sales = 0
                for e in data["Are you a member of Waltham Chamber of Commerce"]:
                    if str(e)== "Member":
                        member_sales += 15
                    else:
                        non_member_sales += 20
                
                # Total sales
                total_sales = member_sales + non_member_sales
                sales_data = [member_sales, non_member_sales]
                # Prepare data for the bar chart
                
                # Plot the bar chart for sales
                plt.figure(figsize=(10, 6))
                plt.bar(["Members", "Non-Members"], sales_data, color=["blue", "green"])
                plt.title(f"Bar chart for {query}")
                plt.xlabel('Membership Status')
                plt.ylabel('Sales ($)')
                plt.tight_layout()
                
                # Save the visualization
                visualization_path = os.path.join(output_folder, f"{query.replace(' ', '_')}_bar.png")
                plt.savefig(visualization_path)
                plt.close()
                
                return visualization_path
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
                # Group by Event and Membership Status and calculate the sum of sales
                sales_data = data.groupby(['Event', 'Are you a member of Waltham Chamber of Commerce']).size().unstack(fill_value=0)

                # Calculate sales for members and non-members
                sales_data["Member Sales"] = sales_data.get("Member", 0) * 15
                sales_data["Non-Member Sales"] = sales_data.get("Non-member", 0) * 20

                # Prepare data for the bar chart
                events = sales_data.index
                member_sales = sales_data["Member Sales"]
                non_member_sales = sales_data["Non-Member Sales"]

                # Plot the bar chart for sales comparison across multiple events
                width = 0.35  # Bar width
                x = range(len(events))  # X-axis positions for the events

                plt.figure(figsize=(12, 6))
                plt.bar(x, member_sales, width, label="Members", color="blue")
                plt.bar([p + width for p in x], non_member_sales, width, label="Non-Members", color="green")

                plt.title(f"Sales Comparison by Event for {query}")
                plt.xlabel('Event')
                plt.ylabel('Sales ($)')
                plt.xticks([p + width / 2 for p in x], events, rotation=45, ha="right")
                plt.legend()

                # Save the visualization
                visualization_path = os.path.join(output_folder, f"{query.replace(' ', '_')}_bar.png")
                plt.tight_layout()
                plt.savefig(visualization_path)
                plt.close()

                return visualization_path




            else:
                raise ValueError(f"Unknown query: {query}")