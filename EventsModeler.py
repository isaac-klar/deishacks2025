import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # For headless environments
import matplotlib.pyplot as plt

# Use a built-in style (guaranteed to exist, no missing file issues)
plt.style.use('ggplot')

class EventsModeler:
    """
    Generates visually pleasing charts from one or multiple XLSX files (each = 1 event).
    If multiple => side-by-side bar comparisons.
    """

    def model(self, dataframes, labels=None, query="Attended", output_folder="static"):
        """
        :param dataframes: list of DataFrames (each is one event).
        :param labels:     optional list of event names. If None, use "Event_1", etc.
        :param query:      "Attended", "Member Status", "Sales".
        :param output_folder: where chart images are saved.
        :return:           chart filename (string), e.g. "Attended_Multi.png".
        """
        if not dataframes:
            raise ValueError("No DataFrames provided.")
        if labels and len(labels) != len(dataframes):
            raise ValueError("Length of labels must match length of dataframes.")

        os.makedirs(output_folder, exist_ok=True)

        if len(dataframes) == 1:
            # Single
            df = dataframes[0]
            label = labels[0] if labels else "Event_1"
            return self._model_single(df, label, query, output_folder)
        else:
            # Multiple => combine
            combined = []
            for i, df in enumerate(dataframes):
                event_label = labels[i] if labels else f"Event_{i+1}"
                tmp = df.copy()
                tmp["Event"] = event_label
                combined.append(tmp)
            merged_df = pd.concat(combined, ignore_index=True)
            return self._model_multi(merged_df, query, output_folder)

    def _model_single(self, df, label, query, output_folder):
        """Single-event chart with bigger fonts, pleasing color schemes."""
        if df.empty:
            raise ValueError(f"DataFrame for '{label}' is empty.")

        safe_label = label.replace(' ', '_')

        # General style for bigger fonts
        title_size = 18
        label_size = 14
        plt.figure(figsize=(9, 7))

        if query == "Attended":
            counts = df["Will you be in attendance?"].value_counts()
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
            mem_count = (df[col] == "Member").sum()
            nonmem_count = (df[col] == "Non-member").sum()
            mem_sales = mem_count * 15
            nonmem_sales = nonmem_count * 20

            plt.bar(["Members", "Non-Members"], [mem_sales, nonmem_sales], color=["#4c72b0", "#55a868"])
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

    def _model_multi(self, df, query, output_folder):
        """Multi-event chart => side-by-side bars for each event."""
        if df.empty:
            raise ValueError("Merged DataFrame is empty.")
        if "Event" not in df.columns:
            raise ValueError("No 'Event' column for multi-file logic.")

        title_size = 18
        label_size = 14
        plt.figure(figsize=(12, 7))

        if query == "Attended":
            group = df.groupby(["Event", "Will you be in attendance?"]).size().unstack(fill_value=0)
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
            group = df.groupby(["Event", col]).size().unstack(fill_value=0)
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
            group = df.groupby(["Event", col]).size().unstack(fill_value=0)
            mem_sales = group.get("Member", 0) * 15
            nonmem_sales = group.get("Non-member", 0) * 20

            x = range(len(group))
            width = 0.4
            plt.bar(x, mem_sales, width, label="Members", color="#4c72b0")
            plt.bar([p + width for p in x], nonmem_sales, width, label="Non-Members", color="#55a868")

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
