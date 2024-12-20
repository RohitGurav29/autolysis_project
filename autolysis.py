# -*- coding: utf-8 -*-
"""Untitled12.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Pitd_Zoi2x5qo6XnpY_HBOsWiKgX7DQu
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai

# Set AI Proxy API base and token
openai.api_base = "https://aiproxy.sanand.workers.dev/openai/v1"
openai.api_key = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZHMyMDAwMTM2QGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.aZJLYrq4UV4N1SfjXhNfctmCM8cbRGzmWkSW37nSy0c"  

# Define the main analysis function
def analyze_csv(file_path):
    try:
        # Load the dataset with a specified encoding
        data = pd.read_csv(file_path, encoding='latin1')

        # Create an output directory based on file name
        output_dir = os.path.splitext(file_path)[0]
        os.makedirs(output_dir, exist_ok=True)

        # Basic Dataset Overview
        summary = data.describe(include='all').to_dict()
        missing_values = data.isnull().sum().to_dict()

        # Visualization 1: Missing Values Heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(data.isnull(), cbar=False, cmap="viridis")
        plt.title("Missing Values Heatmap")
        missing_heatmap_path = os.path.join(output_dir, "missing_values.png")
        plt.savefig(missing_heatmap_path)
        plt.close()

        # Visualization 2: Correlation Heatmap (numerical data only)
        numeric_data = data.select_dtypes(include='number')  # Select only numeric columns
        if numeric_data.shape[1] > 1:  # Ensure there's more than one numeric column
            correlation_matrix = numeric_data.corr()
            plt.figure(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
            plt.title("Correlation Heatmap")
            corr_heatmap_path = os.path.join(output_dir, "correlation_heatmap.png")
            plt.savefig(corr_heatmap_path)
            plt.close()
        else:
            correlation_matrix = None

        # Visualization 3: Bar Plot of Top Categorical Column (if available)
        top_categorical_column = None
        if not data.select_dtypes(include='object').empty:
            top_categorical_column = data.select_dtypes(include='object').columns[0]
            value_counts = data[top_categorical_column].value_counts()
            plt.figure(figsize=(10, 6))
            sns.barplot(x=value_counts.index, y=value_counts.values)
            plt.xticks(rotation=45)
            plt.title(f"Bar Plot of {top_categorical_column}")
            bar_plot_path = os.path.join(output_dir, f"{top_categorical_column}_bar_plot.png")
            plt.savefig(bar_plot_path)
            plt.close()

        # Interact with AI Proxy for insights
        llm_input = {
            "summary_statistics": summary,
            "missing_values": missing_values,
            "correlation_matrix": correlation_matrix,
            "top_categorical_column": top_categorical_column,
        }

        prompt = f"""
        You are analyzing a dataset. Here is the overview:
        Summary Statistics: {summary}
        Missing Values: {missing_values}
        Correlation Matrix: {correlation_matrix}
        Top Categorical Column: {top_categorical_column}

        Write a detailed analysis explaining:
        1. The structure and quality of the dataset.
        2. Key patterns or anomalies.
        3. Possible real-world implications.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that helps analyze datasets."},
                {"role": "user", "content": prompt}
            ]
        )
        analysis_text = response['choices'][0]['message']['content'].strip()

        # Save the README
        readme_path = os.path.join(output_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write("# Automated Analysis Report\n")
            f.write(analysis_text)
            if correlation_matrix is not None:
                f.write(f"\n\n![Correlation Heatmap](correlation_heatmap.png)")
            f.write(f"\n\n![Missing Values Heatmap](missing_values.png)")
            if top_categorical_column:
                f.write(f"\n\n![Bar Plot of {top_categorical_column}]({top_categorical_column}_bar_plot.png)")

        print(f"Analysis complete! Results saved in {output_dir}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# List of files to analyze
file_names = ['/content/goodreads.csv', '/content/happiness.csv', '/content/media.csv']

# Process each file
for file_name in file_names:
    analyze_csv(file_name)

