import google.generativeai as genai
import os
import json
import re

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")


def extract_response_parts(response_text: str) -> dict:
    try:
        # Match a full JSON object
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON object found in response.")

        response_json = json.loads(match.group())

        suggestions = response_json.get("suggestions", [])
        summary = response_json.get("summary", "No summary provided.")

        return {
            "suggestions": suggestions,
            "summary": summary
        }

    except Exception as e:
        print(f"Failed to extract structured response: {e}")
        return {
            "suggestions": [],
            "summary": "Unable to generate summary."
        }


async def get_graph_suggestions(data: list[dict]) -> dict:
    prompt = f"""
    You are an expert business intelligence analyst specializing in data visualization and strategic insights.
    
    # DATASET
    Analyze this dataset carefully:
    ```json
    {data}
    ```
    
    # TASK
    Perform a comprehensive business analysis using this data and suggest visualizations that reveal actionable insights.
    
    # REQUIRED OUTPUTS
    1. **Visualization Recommendations**: Suggest the most informative visualizations that would help business stakeholders make decisions.
    2. **Business Summary**: Provide a concise, high-impact analysis highlighting key findings.
    
    ## Visualization Requirements
    For each visualization, include:
    - The most appropriate chart type (bar, line, scatter, pie, hist, area, box, heatmap, bubble)
    - Meaningful axis selections or category/value pairs
    - Business-focused title that communicates the insight
    - Purpose of the visualization (what business question it answers)
    
    Ensure charts cover:
    - Performance trends
    - Comparison analysis
    - Distribution patterns
    - Correlation discovery
    - Anomaly detection (if applicable)
    - Forecasting indicators (if possible)
    
    ## Business Insights Requirements
    In your summary, address:
    - Key performance indicators and their trends
    - Unexpected patterns or anomalies
    - Potential business opportunities
    - Risk factors or warning signs
    - Actionable recommendations for decision-makers
    - Short-term and long-term predictions
    
    # EXPECTED RESPONSE FORMAT (STRICT JSON)
    Return your answer in this exact JSON format with no additional text:
    ```json
    {{
      "suggestions": [
        {{ 
          "type": "chart_type", 
          "x": "x_field", 
          "y": "y_field", 
          "title": "Business-Focused Title",
          "insight": "Brief explanation of what this visualization reveals"
        }},
        # Additional chart suggestions...
      ],
      "summary": "Concise business analysis with key findings, trends, and actionable recommendations for stakeholders."
    }}
    ```
    
    Ensure you maximize the analytical value for business stakeholders who need to make strategic decisions based on this data 
    NOTE: do not bold anything in summary.
    """
    
    response = model.generate_content(prompt)
    return extract_response_parts(response.text)

async def get_graph_suggestions_(data: list[dict], notes: str) -> dict:
    prompt = f"""
    You are an expert business intelligence analyst.

    # PRIMARY USER FOCUS
    The following user notes represent the most important areas to focus on in your analysis.
    ALL visualizations and insights MUST directly address these priorities:
    \"\"\"{notes}\"\"\"

    # DATASET
    Analyze this dataset with specific attention to elements related to the user focus above:
    ```json
    {data[:5]}  # Showing first 5 records for brevity, but full dataset will be analyzed
    ```
    
    There are {len(data)} records in the full dataset.
    
    # TASK
    Perform a focused business analysis that PRIORITIZES addressing the user notes:
    \"\"\"{notes}\"\"\"
    
    All visualizations and insights should directly connect to these priorities.
    
    # REQUIRED OUTPUTS
    1. **Visualization Recommendations**: Suggest 4-6 visualizations that specifically address the user's focus areas.
    2. **Business Summary**: Provide analysis highlighting key findings related to the user's notes (300-500 words).
    
    ## Visualization Requirements
    For each visualization, include:
    - The most appropriate chart type (bar, line, scatter, pie, hist, area, box, heatmap, bubble)
    - Meaningful axis selections or category/value pairs 
    - Business-focused title that communicates the insight
    - A 2-3 sentence insight describing what this visualization reveals and its business implications
    - IMPORTANT: Explain how this chart addresses the user's specific focus areas
    
    ## Business Summary Requirements
    In your summary, address:
    - Insights directly related to the user's specified focus areas
    - Actionable recommendations that address the user's priorities
    - Write in a professional, executive-friendly style
    
    # EXPECTED RESPONSE FORMAT (STRICT JSON)
    Return your answer in this exact JSON format with no additional text:
    ```json
    {{
      "suggestions": [
        {{ 
          "type": "chart_type", 
          "x": "x_field", 
          "y": "y_field", 
          "title": "Business-Focused Title",
          "insight": "Brief explanation of what this visualization reveals and its business implications"
        }},
        # Additional chart suggestions following same structure...
      ],
      "summary": "Comprehensive business analysis with key findings, trends, and actionable recommendations for stakeholders. This should be 300-500 words of professional business analysis."
    }}
    ```
    
    REMEMBER: Focus primarily on addressing \"\"\"{notes}\"\"\" in all your analysis and recommendations.
    NOTE: Be precise in your field selections - use exact field names from the dataset.
    """
    
    response = model.generate_content(prompt)
    return extract_response_parts(response.text)
