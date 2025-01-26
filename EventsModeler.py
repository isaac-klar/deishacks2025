import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class EventsModeler:
    """
    A class that creates visualizations from a single DataFrame
    and also returns a small summary of the data for easy consumption.
    """

    def model_with_summary(
        self,
        filepath: str = None,
        data: pd.DataFrame = None,
        query: str = "Attended",
        output_folder: str = "static/"
    ):
        """
        Returns a tuple (chart_path, summary_dict).
        chart_path: path to the saved chart image
        summary_dict: a dictionary with some high-level stats about the data
        """
        chart_path = self.model(filepath, data, query, output_folder)
        summary = self.generate_summary(data, query)
        return chart_path, summary

    def model(
        self,
        filepath: str = None,
        data: pd.DataFrame = None,
        query: str = "Attended",
        output_folder: str = "static/"
    ) -> str:
        """
        Create a chart based on the query. Return path to the saved image.
        """
        if data is None and filepath:
            try:
                data = pd.read_excel(filepath)
            except:
                data = pd.read_csv(filepath)

        if data is None:
            raise ValueError("No DataFrame or file path provided.")

        os.makedirs(output_folder, exist_ok=True)

        has_event_col = ("Event" in data.columns)

        if query == "Attended":
            if has_event_col:
                attendance_counts = data.groupby("Event")["Attended"].value_counts().unstack(fill_value=0)
                plt.figure(figsize=(10, 6))
                attendance_counts.plot(kind='bar', stacked=True)
                plt.title("Attended by Event")
                plt.xlabel("Event")
                plt.ylabel("Count")
                plt.tight_layout()
                chart_path = os.path.join(output_folder, "Attended_bar.png")
                plt.savefig(chart_path)
                plt.close()
                return chart_path
            else:
                counts = data["Attended"].value_counts()
                plt.figure(figsize=(8, 6))
                plt.pie(counts.values, labels=counts.index, autopct='%1.1f%%')
                plt.title("Overall Attended Distribution")
                chart_path = os.path.join(output_folder, "Attended_pie.png")
                plt.savefig(chart_path)
                plt.close()
                return chart_path

        elif query == "Member Status":
            col = "Are you a member of Waltham Chamber of Commerce"
            if has_event_col:
                member_counts = data.groupby("Event")[col].value_counts().unstack(fill_value=0)
                plt.figure(figsize=(10, 6))
                member_counts.plot(kind='bar')
                plt.title("Member Status by Event")
                plt.xlabel("Event")
                plt.ylabel("Count")
                plt.tight_layout()
                chart_path = os.path.join(output_folder, "Member_Status_bar.png")
                plt.savefig(chart_path)
                plt.close()
                return chart_path
            else:
                counts = data[col].value_counts()
                plt.figure(figsize=(8, 6))
                plt.pie(counts.values, labels=counts.index, autopct='%1.1f%%')
                plt.title("Overall Member Status")
                chart_path = os.path.join(output_folder, "Member_Status_pie.png")
                plt.savefig(chart_path)
                plt.close()
                return chart_path

        elif query == "Sales":
            if has_event_col:
                group = data.groupby(["Event", "Are you a member of Waltham Chamber of Commerce"])\
                            .size().unstack(fill_value=0)
                member_label = "Member"
                non_member_label = "Non-member"
                group["Member Sales"] = group.get(member_label, 0) * 15
                group["Non-Member Sales"] = group.get(non_member_label, 0) * 20

                events = group.index
                member_sales = group["Member Sales"]
                non_member_sales = group["Non-Member Sales"]

                x = range(len(events))
                width = 0.35
                plt.figure(figsize=(10, 6))
                plt.bar(x, member_sales, width, label="Members", color="blue")
                plt.bar([p + width for p in x], non_member_sales, width, label="Non-Members", color="green")
                plt.title("Sales Comparison by Event")
                plt.xlabel("Event")
                plt.ylabel("Sales ($)")
                plt.xticks([p + width/2 for p in x], events, rotation=45, ha="right")
                plt.legend()
                plt.tight_layout()
                chart_path = os.path.join(output_folder, "Sales_bar.png")
                plt.savefig(chart_path)
                plt.close()
                return chart_path
            else:
                col = "Are you a member of Waltham Chamber of Commerce"
                member_count = (data[col] == "Member").sum()
                non_member_count = (data[col] == "Non-member").sum()
                member_sales = member_count * 15
                non_member_sales = non_member_count * 20

                plt.figure(figsize=(8, 6))
                plt.bar(["Members", "Non-Members"], [member_sales, non_member_sales], color=["blue", "green"])
                plt.title("Overall Sales")
                plt.xlabel("Membership")
                plt.ylabel("Sales ($)")
                plt.tight_layout()
                chart_path = os.path.join(output_folder, "Sales_bar.png")
                plt.savefig(chart_path)
                plt.close()
                return chart_path

        else:
            raise ValueError(f"Unknown query: {query}")

    def generate_summary(self, data: pd.DataFrame, query: str) -> dict:
        """
        Return a short summary dictionary with info about attendance, membership, sales, etc.
        to help non-technical folks quickly see key metrics.
        Customize these stats as needed for your use case.
        """
        summary = {}
        total_rows = len(data)
        summary["Total Rows"] = total_rows

        # Common columns
        attended_col = "Attended"
        membership_col = "Are you a member of Waltham Chamber of Commerce"

        # Attended summary
        if attended_col in data.columns:
            attended_count = (data[attended_col] == "Yes").sum()
            not_attended_count = (data[attended_col] == "No").sum()
            summary["Attended Yes"] = int(attended_count)
            summary["Attended No"] = int(not_attended_count)

        # Membership summary
        if membership_col in data.columns:
            member_count = (data[membership_col] == "Member").sum()
            nonmember_count = (data[membership_col] == "Non-member").sum()
            summary["# of Members"] = int(member_count)
            summary["# of Non-Members"] = int(nonmember_count)

        # Sales summary
        # Suppose each Member ticket = $15, each Non-Member = $20
        if membership_col in data.columns:
            if "Sales" in query:  # or always compute
                total_member_sales = (data[membership_col] == "Member").sum() * 15
                total_nonmember_sales = (data[membership_col] == "Non-member").sum() * 20
                summary["Total Sales ($)"] = total_member_sales + total_nonmember_sales
            else:
                # We could still show a quick estimate
                total_member_sales = (data[membership_col] == "Member").sum() * 15
                total_nonmember_sales = (data[membership_col] == "Non-member").sum() * 20
                summary["Potential Sales if 'Sales' query used ($)"] = total_member_sales + total_nonmember_sales

        return summary
