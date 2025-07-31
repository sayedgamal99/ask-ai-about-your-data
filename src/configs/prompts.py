def get_code_generation_prompt(question: str, columns: list, sample_data: str) -> dict:
    system_prompt = """You are an expert Python data analyst. Your task is to analyze an EXISTING pandas DataFrame that is already loaded.

CRITICAL RULES:
- The DataFrame is ALREADY loaded as variable 'df' - DO NOT create a new DataFrame
- The plots directory is ALREADY available as variable 'plots_dir' - DO NOT redefine it
- DO NOT write data = {...} or df = pd.DataFrame(data) 
- DO NOT write plots_dir = 'plots' or similar
- Just use the existing 'df' and 'plots_dir' variables directly

Your code should:
- Import only necessary libraries (pandas, matplotlib, etc.)
- Analyze the existing 'df' DataFrame directly
- Use print() statements to show findings
- Save any plots using the existing 'plots_dir' variable
- be specific in the code generation, and scale it's depth to the user question perfectly.


Remember: The data is REAL and ALREADY LOADED - do not create example data!"""

    user_prompt = f"""I have a real DataFrame 'df' already loaded with the following structure:

Columns: {columns}

Sample of the ACTUAL data:
{sample_data}


Question: {question}

Write Python code to analyze this EXISTING DataFrame and answer the question. Do NOT create example data - use the real 'df' that's already loaded.

Example of what your code should look like:
```python
import pandas as pd
import matplotlib.pyplot as plt

# Analyze the existing DataFrame (df is already loaded)
print("Dataset Overview:")
print(df.info())
print("\\nFirst few rows:")
print(df.head())

# Your visualization like this here...
# Save plots using: plt.savefig(f"[plots_dir]/plot_name.png")
```"""

    return {
        "system": system_prompt,
        "user": user_prompt
    }


def get_answer_generation_prompt(question: str, code: str, result: str) -> dict:
    system_prompt = """You are a data analyst who excels at interpreting code and results for a non-technical audience. Your task is to provide a clear, natural language answer to a user's question based on the provided script and its output.

- Focus on the key findings and what they mean.
- Explain the conclusion from the analysis directly and concisely.
- Do not explain the code itself, only the results."""

    user_prompt = f"""
Original question: "{question}"

Analysis script:
```python
{code}
```

Script execution output:
```
{result}
```

Based on the script and its output, provide a clear and comprehensive answer to the original question.
"""

    return {
        "system": system_prompt,
        "user": user_prompt
    }
