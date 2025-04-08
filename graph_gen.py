from fastapi.responses import FileResponse
import zipfile
import tempfile
import os
# At the top of your graph_gen.py file
import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt
import pandas as pd
import io
import seaborn as sns
from matplotlib.figure import Figure

# Color constants
DARK_BG = '#09090B'
LIGHT_TEXT = '#FFFFFF'
DARK_TEXT = '#000000'  # Dark text for pie chart
BAR = '#7C3AED'
VIBRANT_INDIGO_SHADES = [
    '#F5F3FF',  # Ultra-light lavender
    '#EEE7FE',  # Gentle soft violet
    '#E5DEFE',  # Whispering lavender
    '#E0D4FD',  # Cloudy lilac
    '#DDD6FE',  # Lavender tint
    '#C4B5FD',  # Soft violet
    '#B2A0FC',  # Medium pastel indigo
    '#A78BFA',  # Medium violet
    '#925CFA',  # Vibrant indigo variant
    '#8B5CF6',  # Bright medium indigo
    '#7C3AED',  # Base vibrant indigo
    '#6D28D9',  # Rich indigo
    '#5B21B6',  # Deep purple
    '#4C1D95',  # Bold dark indigo
    '#3C1A6E',  # Strong midnight shade
]

def apply_dark_theme(ax):
    ax.set_facecolor(DARK_BG)
    ax.tick_params(colors=LIGHT_TEXT)
    ax.xaxis.label.set_color(LIGHT_TEXT)
    ax.yaxis.label.set_color(LIGHT_TEXT)
    ax.title.set_color(LIGHT_TEXT)

def apply_light_theme_for_pdf(ax):
    """Apply a light theme suitable for PDF reports"""
    bg_color = '#FFFFFF'
    text_color = '#333333'
    ax.set_facecolor(bg_color)
    ax.tick_params(colors=text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    ax.title.set_color(text_color)
    return ax


def generate_graphs_zip(data: list[dict], suggestions: list[dict], summary: str):
    df = pd.DataFrame(data)
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, s in enumerate(suggestions):
            if not isinstance(s, dict):
                continue

            gtype = s.get("type", "line")
            title = s.get("title", f"graph_{i}")
            x = s.get("x")
            y = s.get("y")
            labels = s.get("labels")
            values = s.get("values")
            size = s.get("size")

            try:
                fig, ax = plt.subplots(figsize=(12, 6), facecolor=DARK_BG)

                if gtype == "scatter" and x and y:
                    ax.scatter(df[x], df[y], color=BAR)

                elif gtype == "bar" and x and y:
                    ax.bar(df[x], df[y], color=BAR)

                elif gtype == "line" and x and y:
                    ax.plot(df[x], df[y], color=BAR, marker='o')

                elif gtype == "hist" and x:
                    ax.hist(df[x], color=VIBRANT_INDIGO_SHADES[9])

                elif gtype == "box" and x and y:
                    df.boxplot(column=[y], by=x, ax=ax,
                               boxprops=dict(color=LIGHT_TEXT),
                               whiskerprops=dict(color=LIGHT_TEXT),
                               capprops=dict(color=LIGHT_TEXT),
                               medianprops=dict(color=BAR))
                    ax.set_title(title, color=LIGHT_TEXT)
                    ax.set_xlabel(x, color=LIGHT_TEXT)
                    ax.set_ylabel(y, color=LIGHT_TEXT)
                    ax.figure.suptitle("")
                    apply_dark_theme(ax)
                    plt.xticks(rotation=90)

                elif gtype == "pie" and labels and values:
                    fig, ax = plt.subplots(figsize=(12, 6), facecolor=DARK_BG)
                    wedges, texts, autotexts = ax.pie(
                        df[values], 
                        labels=df[labels],
                        colors=VIBRANT_INDIGO_SHADES[:len(df)],
                        autopct='%1.1f%%', 
                        textprops=dict(color=DARK_TEXT, fontweight='bold')  # Dark text for better visibility
                    )
                    # Make sure percentage text is also dark
                    for autotext in autotexts:
                        autotext.set_color(DARK_TEXT)
                        autotext.set_fontweight('bold')
                    
                    ax.set_title(title, color=LIGHT_TEXT)

                elif gtype == "area" and x and y:
                    ax.fill_between(df[x], df[y], color=BAR, alpha=0.6)

                elif gtype == "bubble" and x and y and size:
                    ax.scatter(df[x], df[y], s=df[size]*20, alpha=0.6, color=BAR)

                elif gtype == "heatmap":
                    numeric_df = df.select_dtypes(include='number')
                    if numeric_df.shape[1] > 1:
                        fig, ax = plt.subplots(figsize=(12, 8), facecolor=DARK_BG)
                        cmap = sns.light_palette(VIBRANT_INDIGO_SHADES[-1], as_cmap=True)
                        sns.heatmap(numeric_df.corr(), ax=ax, cmap=cmap, annot=True, fmt=".2f", cbar=False)
                        ax.set_title(title, color=LIGHT_TEXT)
                        for label in ax.get_xticklabels() + ax.get_yticklabels():
                            label.set_color(LIGHT_TEXT)
                        plt.xticks(rotation=90)
                        plt.yticks(rotation=0)

                else:
                    plt.close(fig)
                    continue

                if gtype not in ["pie", "box", "heatmap"]:
                    ax.set_title(title)
                    if x: ax.set_xlabel(x)
                    if y: ax.set_ylabel(y)
                    apply_dark_theme(ax)
                    if x and len(df[x]) > 5:
                        plt.xticks(rotation=90)


                
                plt.tight_layout(pad=3.0)

                img_buf = io.BytesIO()
                fig.savefig(img_buf, format="png", bbox_inches="tight", transparent=True, dpi=100)
                plt.close(fig)
                img_buf.seek(0)
                zipf.writestr(f"{title.replace(' ', '_')}.png", img_buf.read())

            except Exception as e:
                print(f"Error generating {title}: {e}")
                continue

        # Add summary as a text file
        zipf.writestr("summary.txt", summary)

    zip_buffer.seek(0)
    return zip_buffer

def generate_chart(df: pd.DataFrame, chart_config: dict, for_pdf: bool = True):
    """
    Create a single chart based on configuration
    
    Args:
        df: DataFrame with the data
        chart_config: Configuration for the chart
        for_pdf: Whether to use light theme (for PDF) or dark theme
        
    Returns:
        Figure: Matplotlib figure object
    """
    gtype = chart_config.get("type", "line")
    title = chart_config.get("title", "Untitled Chart")
    x = chart_config.get("x")
    y = chart_config.get("y")
    labels = chart_config.get("labels")
    values = chart_config.get("values")
    size = chart_config.get("size")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    try:
        if gtype == "scatter" and x and y:
            ax.scatter(df[x], df[y], color=BAR if not for_pdf else '#7C3AED')

        elif gtype == "bar" and x and y:
            # For bar charts with many categories, ensure proper width and orientation
            if len(df[x].unique()) > 10:
                # Horizontal bar chart for many categories
                ax.barh(df[x], df[y], color=BAR if not for_pdf else '#7C3AED')
                plt.tight_layout(pad=3.0)
            else:
                ax.bar(df[x], df[y], color=BAR if not for_pdf else '#7C3AED')

        elif gtype == "line" and x and y:
            ax.plot(df[x], df[y], color=BAR if not for_pdf else '#7C3AED', marker='o')

        elif gtype == "hist" and x:
            ax.hist(df[x], color=VIBRANT_INDIGO_SHADES[9] if not for_pdf else '#8B5CF6')

        elif gtype == "box" and x and y:
            props = dict(color='#333333' if for_pdf else LIGHT_TEXT)
            median_props = dict(color='#7C3AED')
            
            df.boxplot(column=[y], by=x, ax=ax,
                       boxprops=props,
                       whiskerprops=props,
                       capprops=props,
                       medianprops=median_props)
            ax.set_title(title)
            ax.set_xlabel(x)
            ax.set_ylabel(y)
            ax.figure.suptitle("")
            if not for_pdf:
                apply_dark_theme(ax)
            else:
                apply_light_theme_for_pdf(ax)
            plt.xticks(rotation=90)

        elif gtype == "pie" and labels and values:
            # Handle pie charts - limit to top categories if there are too many
            if df[labels].nunique() > 8:
                # Get the top 7 categories by value
                top_categories = df.groupby(labels)[values].sum().nlargest(7).index
                
                # Create a copy of the dataframe with an "Other" category for the rest
                pie_df = df.copy()
                pie_df.loc[~pie_df[labels].isin(top_categories), labels] = 'Other'
                
                # Group by the modified categories
                pie_data = pie_df.groupby(labels)[values].sum().reset_index()
                
                # Plot the pie chart with the consolidated categories
                wedges, texts, autotexts = ax.pie(
                    pie_data[values], 
                    labels=pie_data[labels],
                    colors=['#C4B5FD', '#A78BFA', '#8B5CF6', '#7C3AED', '#6D28D9', '#5B21B6', '#4C1D95', '#3C1A6E'][:len(pie_data)],
                    autopct='%1.1f%%', 
                    textprops=dict(color=DARK_TEXT, fontweight='bold')
                )
            else:
                # Plot all categories if there aren't too many
                pie_data = df.groupby(labels)[values].sum().reset_index()
                colors = ['#C4B5FD', '#A78BFA', '#8B5CF6', '#7C3AED', '#6D28D9', '#5B21B6'] if for_pdf else VIBRANT_INDIGO_SHADES
                wedges, texts, autotexts = ax.pie(
                    pie_data[values], 
                    labels=pie_data[labels],
                    colors=colors[:len(pie_data)],
                    autopct='%1.1f%%', 
                    textprops=dict(color=DARK_TEXT, fontweight='bold')
                )
            
            for autotext in autotexts:
                autotext.set_color(DARK_TEXT)
                autotext.set_fontweight('bold')
            
            ax.set_title(title)

        elif gtype == "area" and x and y:
            ax.fill_between(df[x], df[y], color='#7C3AED', alpha=0.6)

        elif gtype == "bubble" and x and y and size:
            ax.scatter(df[x], df[y], s=df[size]*20, alpha=0.6, color='#7C3AED')

        elif gtype == "heatmap":
            numeric_df = df.select_dtypes(include='number')
            if numeric_df.shape[1] > 1:
                cmap = sns.light_palette('#7C3AED', as_cmap=True)
                sns.heatmap(numeric_df.corr(), ax=ax, cmap=cmap, annot=True, fmt=".2f", cbar=True)
                ax.set_title(title)
                plt.xticks(rotation=90)
                plt.yticks(rotation=0)
        
        # Set labels and styling
        if gtype not in ["pie", "box", "heatmap"]:
            ax.set_title(title)
            if x: ax.set_xlabel(x)
            if y: ax.set_ylabel(y)
            
            if not for_pdf:
                apply_dark_theme(ax)
            else:
                apply_light_theme_for_pdf(ax)
                
            if x and len(df[x].unique()) > 5:
                plt.xticks(rotation=90)
        
        plt.tight_layout(pad=3.0)
        return fig
        
    except Exception as e:
        print(f"Error generating chart '{title}': {e}")
        plt.close(fig)
        # Return a simple error figure
        error_fig, error_ax = plt.subplots(figsize=(10, 6))
        error_ax.text(0.5, 0.5, f"Error creating chart: {str(e)}", 
                 horizontalalignment='center', verticalalignment='center')
        error_ax.axis('off')
        return error_fig

def generate_graphs_zip_(data: list[dict], suggestions: dict):
    """Generate graphs and return as zip file"""
    df = pd.DataFrame(data)
    zip_buffer = io.BytesIO()
    
    # Extract suggestions and summary
    graph_suggestions = suggestions.get("suggestions", [])
    summary = suggestions.get("summary", "No summary provided.")

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, s in enumerate(graph_suggestions):
            if not isinstance(s, dict):
                continue

            title = s.get("title", f"graph_{i}")
            
            try:
                fig = generate_chart(df, s, for_pdf=False)
                
                img_buf = io.BytesIO()
                fig.savefig(img_buf, format="png", bbox_inches="tight", transparent=True, dpi=100)
                plt.close(fig)
                img_buf.seek(0)
                zipf.writestr(f"{title.replace(' ', '_')}.png", img_buf.read())

            except Exception as e:
                print(f"Error generating {title}: {e}")
                continue

        # Add summary as a text file
        zipf.writestr("summary.txt", summary)

    zip_buffer.seek(0)
    return zip_buffer