import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # For headless environments
import matplotlib.pyplot as plt

# Use a built-in style that is guaranteed to work with default Matplotlib
plt.style.use('ggplot')

class EventsModeler:
    """
    Generates fancy charts from one or multiple XLSX files,
    each file = a single event. If multiple => side-by-side comparison.
    """

    def model(self, dataframes, labels=None, query="Attended", output_folder="static"):
        """
        :param dataframes: list of DataFrames (each is one event).
        :param labels:     list of event names (matching dataframes length).
        :param query:      one of "Attended", "Member Status", or "Sales".
        :param output_folder: directory in which to save the charts.
        :return:           chart filename (e.g. "Attended_Multi.png").
        """
        if not dataframes:
            raise ValueError("No DataFrames provided.")
        if labels and len(labels) != len(dataframes):
            raise ValueError("labels length must match dataframes length.")

        os.makedirs(output_folder, exist_ok=True)

        if len(dataframes) == 1:
            # Single file => single chart
            df = dataframes[0]
            label = labels[0] if labels else "Event_1"
            return self._model_single(df, label, query, output_folder)
        else:
            # Multiple => combine
            combined = []
            for i, df in enumerate(dataframes):
                event_label = labels[i] if labels else f"Event_{i+1}"
                temp = df.copy()
                temp["Event"] = event_label
                combined.append(temp)
            merged_df = pd.concat(combined, ignore_index=True)
            return self._model_multi(merged_df, query, output_folder)

    def _model_single(self, df, label, query, output_folder):
        """Single event chart. If multiple columns, we do 'Attended', 'Member Status', or 'Sales'."""
        if df.empty:
            raise ValueError(f"DataFrame for '{label}' is empty.")

        safe_label = label.replace(" ", "_")

        # Larger fonts for computer screens
        title_size = 18
        label_size = 14
        plt.figure(figsize=(9, 7))

        if query == "Attended":
            # Pie chart of "Yes"/"No"
            counts = df["Attended"].value_counts()
            plt.pie(
                counts.values,
                labels=counts.index,
                autopct='%1.1f%%',
                startangle=140,
                textprops={'fontsize': label_size}
            )
            plt.title(f"Attended - {label}", fontsize=title_size)
            filename = f"Attended_{safe_label}.png"
            plt.savefig(os.path.join(output_folder, filename), dpi=120)
            plt.close()
            return filename

        elif query == "Member Status":
            col = "Are you a member of Waltham Chamber of Commerce"
            counts = df[col].value_counts()
            plt.pie(
                counts.values,
                labels=counts.index,
                autopct='%1.1f%%',
                startangle=140,
                textprops={'fontsize': label_size}
            )
            plt.title(f"Member Status - {label}", fontsize=title_size)
            filename = f"MemberStatus_{safe_label}.png"
            plt.savefig(os.path.join(output_folder, filename), dpi=120)
            plt.close()
            return filename

        elif query == "Sales":
            col = "Are you a member of Waltham Chamber of Commerce"
            member_count = (df[col] == "Member").sum()
            non_member_count = (df[col] == "Non-member").sum()

            member_sales = member_count * 15
            non_member_sales = non_member_count * 20

            plt.bar(["Members", "Non-Members"], [member_sales, non_member_sales], color=["#4c72b0", "#55a868"])
            plt.title(f"Sales - {label}", fontsize=title_size)
            plt.xlabel("Membership", fontsize=label_size)
            plt.ylabel("Sales ($)", fontsize=label_size)
            plt.tight_layout()
            filename = f"Sales_{safe_label}.png"
            plt.savefig(os.path.join(output_folder, filename), dpi=120)
            plt.close()
            return filename

        else:
            raise ValueError(f"Unknown query: {query}")

    def _model_multi(self, merged_df, query, output_folder):
        """Multi-event chart. We'll do side-by-side bars for multiple events."""
        if merged_df.empty:
            raise ValueError("Merged DataFrame is empty.")
        if "Event" not in merged_df.columns:
            raise ValueError("No 'Event' column found for multi-file logic.")

        title_size = 18
        label_size = 14
        plt.figure(figsize=(12, 7))

        if query == "Attended":
            # Group by (Event, Attended) => side by side for "Yes"/"No"
            group = merged_df.groupby(["Event", "Attended"]).size().unstack(fill_value=0)
            yes_vals = group.get("Yes", 0)
            no_vals = group.get("No", 0)

            x = range(len(group))
            width = 0.4
            plt.bar(x, yes_vals, width, label="Yes", color="#4c72b0")
            plt.bar([p + width for p in x], no_vals, width, label="No", color="#c44e52")

            plt.title("Attended (Multiple Events)", fontsize=title_size)
            plt.xlabel("Event", fontsize=label_size)
            plt.ylabel("Count", fontsize=label_size)
            plt.xticks([p + width/2 for p in x], group.index, rotation=45, ha="right")
            plt.legend(fontsize=label_size)
            plt.tight_layout()
            filename = "Attended_Multi.png"
            plt.savefig(os.path.join(output_folder, filename), dpi=120)
            plt.close()
            return filename

        elif query == "Member Status":
            col = "Are you a member of Waltham Chamber of Commerce"
            group = merged_df.groupby(["Event", col]).size().unstack(fill_value=0)
            mem_vals = group.get("Member", 0)
            nonmem_vals = group.get("Non-member", 0)

            x = range(len(group))
            width = 0.4
            plt.bar(x, mem_vals, width, label="Members", color="#4c72b0")
            plt.bar([p + width for p in x], nonmem_vals, width, label="Non-Members", color="#55a868")

            plt.title("Member Status (Multiple Events)", fontsize=title_size)
            plt.xlabel("Event", fontsize=label_size)
            plt.ylabel("Count", fontsize=label_size)
            plt.xticks([p + width/2 for p in x], group.index, rotation=45, ha="right")
            plt.legend(fontsize=label_size)
            plt.tight_layout()
            filename = "MemberStatus_Multi.png"
            plt.savefig(os.path.join(output_folder, filename), dpi=120)
            plt.close()
            return filename

        elif query == "Sales":
            col = "Are you a member of Waltham Chamber of Commerce"
            group = merged_df.groupby(["Event", col]).size().unstack(fill_value=0)

            member_sales = group.get("Member", 0) * 15
            nonmember_sales = group.get("Non-member", 0) * 20

            x = range(len(group))
            width = 0.4
            plt.bar(x, member_sales, width, label="Members", color="#4c72b0")
            plt.bar([p + width for p in x], nonmember_sales, width, label="Non-Members", color="#55a868")

            plt.title("Sales (Multiple Events)", fontsize=title_size)
            plt.xlabel("Event", fontsize=label_size)
            plt.ylabel("Sales ($)", fontsize=label_size)
            plt.xticks([p + width/2 for p in x], group.index, rotation=45, ha="right")
            plt.legend(fontsize=label_size)
            plt.tight_layout()
            filename = "Sales_Multi.png"
            plt.savefig(os.path.join(output_folder, filename), dpi=120)
            plt.close()
            return filename

        else:
            raise ValueError(f"Unknown query: {query}")
