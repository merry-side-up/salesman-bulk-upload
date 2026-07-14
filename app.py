import streamlit as st
import pandas as pd
from api import create_visit

st.set_page_config(
    page_title="SalesSync Bulk Visit Creator",
    page_icon="📅",
    layout="wide"
)

st.title("📅 SalesSync Bulk Visit Creator")

uploaded_file = st.file_uploader(
    "Upload your planning Excel",
    type=["xlsx"]
)

if uploaded_file is not None:

    try:
        df = pd.read_excel(uploaded_file)

        st.success(f"✅ {len(df)} visits loaded")

        st.subheader("Excel Preview")
        st.dataframe(df, use_container_width=True)

        st.subheader("Detected Columns")
        st.write(df.columns.tolist())

        required_columns = [
            "client id",
            "Assigned Date",
            "saleman id"
        ]

        missing = [c for c in required_columns if c not in df.columns]

        if missing:
            st.error("Missing columns:")
            st.write(missing)

        else:

            task_columns = [
                col for col in df.columns
                if col.lower().startswith("task id")
            ]

            if not task_columns:
                st.error("No task ID columns found. Add columns like: task id 1, task id 2...")
            else:

                st.success(
                    f"✅ Excel format is valid! Found {len(task_columns)} task columns"
                )

                st.divider()

                if st.button("🚀 Create Visits"):

                    results = []

                    progress = st.progress(0)

                    total = len(df)

                    for index, row in df.iterrows():

                        # Collect all task IDs from the row
                        task_ids = []

                        for col in task_columns:

                            if pd.notna(row[col]):

                                task_ids.append(
                                    int(row[col])
                                )

                        payload = {

                            "assignedDate": pd.to_datetime(
                                row["Assigned Date"],
                                dayfirst=True
                            ).strftime("%Y-%m-%d"),

                            "clientId": int(
                                row["client id"]
                            ),

                            "everyWeeks": 0,

                            "isRecurring": "0",

                            "isUrgent": "0",

                            "notes": "",

                            "salesManId": int(
                                row["saleman id"]
                            ),

                            "tasksIds": task_ids,

                            "totalMonths": 0
                        }


                        try:

                            response = create_visit(payload)


                            if response.status_code == 200:

                                data = response.json()

                                results.append({

                                    "row": index + 1,

                                    "client": row["client id"],

                                    "tasks": str(task_ids),

                                    "status": "✅ Created",

                                    "visit id": data["data"]["id"]

                                })


                            else:

                                results.append({

                                    "row": index + 1,

                                    "client": row["client id"],

                                    "tasks": str(task_ids),

                                    "status": "❌ Failed",

                                    "visit id": ""

                                })


                        except Exception as e:

                            results.append({

                                "row": index + 1,

                                "client": row["client id"],

                                "tasks": str(task_ids),

                                "status": f"❌ Error: {e}",

                                "visit id": ""

                            })


                        progress.progress(
                            (index + 1) / total
                        )


                    st.subheader("Creation Results")

                    result_df = pd.DataFrame(results)

                    st.dataframe(
                        result_df,
                        use_container_width=True
                    )


    except Exception as e:

        st.error(f"Error reading Excel: {e}")
        