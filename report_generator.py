# import io
# import logging
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4, letter
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch, cm
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
# from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
# import matplotlib.pyplot as plt
# import pandas as pd
# from datetime import datetime
# from io import BytesIO

# # Set up logging
# logger = logging.getLogger(__name__)

# def create_pdf_report(data, suggestions, summary):
#     """
#     Create a professional PDF report with graphs and analysis
    
#     Args:
#         data: List of dictionaries containing business data
#         suggestions: List of graph suggestions from Gemini
#         summary: Business analysis summary text
        
#     Returns:
#         BytesIO: The PDF file as a bytes buffer
#     """
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter, 
#                             rightMargin=72, leftMargin=72,
#                             topMargin=72, bottomMargin=72)
    
#     story = []
    
#     # Define styles
#     styles = getSampleStyleSheet()
    
#     # Create custom styles
#     title_style = ParagraphStyle(
#         'Title',
#         parent=styles['Title'],
#         fontSize=24,
#         spaceAfter=12
#     )
    
#     subtitle_style = ParagraphStyle(
#         'Subtitle',
#         parent=styles['Heading2'],
#         fontSize=18,
#         spaceAfter=6
#     )
    
#     body_style = ParagraphStyle(
#         'Body',
#         parent=styles['Normal'],
#         fontSize=11,
#         leading=14,
#         alignment=TA_JUSTIFY
#     )
    
#     # Add title and date
#     story.append(Paragraph("Business Intelligence Report", title_style))
#     current_date = datetime.now().strftime("%B %d, %Y")
#     story.append(Paragraph(f"Generated on {current_date}", styles['Italic']))
#     story.append(Spacer(1, 0.25*inch))
    
#     # Add summary section
#     story.append(Paragraph("Executive Summary", subtitle_style))
#     story.append(Spacer(1, 0.1*inch))
#     story.append(Paragraph(summary, body_style))
#     story.append(Spacer(1, 0.25*inch))
    
#     # Add data overview
#     df = pd.DataFrame(data)
#     story.append(Paragraph("Data Overview", subtitle_style))
#     story.append(Spacer(1, 0.1*inch))
    
#     # Format date strings to be more readable
#     try:
#         min_date = pd.to_datetime(df['date'].min()).strftime('%Y-%m-%d')
#         max_date = pd.to_datetime(df['date'].max()).strftime('%Y-%m-%d')
#         date_range = f"{min_date} to {max_date}"
#     except:
#         date_range = "Date range unavailable"
    
#     # Create a simple data summary table
#     summary_data = [
#         ["Total Records", str(len(df))],
#         ["Date Range", date_range],
#         ["Total Revenue", f"${df['total'].sum():.2f}"],
#         ["Number of Branches", str(len(df['branch'].unique()))]
#     ]
    
#     t = Table(summary_data, colWidths=[2*inch, 3*inch])
#     t.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (0, -1), colors.lavender),
#         ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
#         ('ALIGN', (0, 0), (0, -1), 'LEFT'),
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black)
#     ]))
    
#     story.append(t)
#     story.append(Spacer(1, 0.25*inch))
    
#     # Visualizations section
#     story.append(Paragraph("Key Business Insights", subtitle_style))
#     story.append(Spacer(1, 0.1*inch))
    
#     # Import generate_chart inside the function to avoid circular imports
#     from graph_gen import generate_chart
    
#     # Generate and add charts - Use in-memory approach instead of temp files
#     for i, chart in enumerate(suggestions):
#         if not isinstance(chart, dict):
#             continue
            
#         title = chart.get("title", f"Chart {i+1}")
#         insight = chart.get("insight", "No specific insight provided.")
        
#         # Add chart title and insight
#         story.append(Paragraph(title, styles['Heading3']))
#         story.append(Paragraph(insight, body_style))
#         story.append(Spacer(1, 0.1*inch))
        
#         try:
#             # Log which chart we're generating for debugging
#             logger.info(f"Generating chart {i}: {title}")
            
#             # Generate chart for PDF (using light theme)
#             chart_fig = generate_chart(df, chart, for_pdf=True)
            
#             # Save chart directly to BytesIO buffer instead of temp file
#             img_buffer = BytesIO()
#             chart_fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
#             plt.close(chart_fig)
#             img_buffer.seek(0)
            
#             # Add image to the report with proper sizing
#             img = Image(img_buffer, width=6*inch, height=3*inch)
#             story.append(img)
            
#         except Exception as e:
#             logger.error(f"Error generating chart {i}: {str(e)}", exc_info=True)
#             story.append(Paragraph(f"Error generating chart: {str(e)}", styles['Normal']))
        
#         # Add space after each chart
#         story.append(Spacer(1, 0.3*inch))
        
#         # Add page break after every second chart (except the last)
#         if i % 2 == 1 and i < len(suggestions) - 1:
#             story.append(PageBreak())
    
#     # Add recommendations section if we have at least one chart completed
#     if suggestions:
#         story.append(PageBreak())
#         story.append(Paragraph("Recommendations", subtitle_style))
#         story.append(Spacer(1, 0.1*inch))
        
#         # Try to extract recommendations from summary
#         recommendation_paragraphs = summary.split('.')
#         recommendations = [para.strip() for para in recommendation_paragraphs 
#                           if any(keyword in para.lower() for keyword in 
#                                 ['recommend', 'should', 'could', 'opportunity', 'improve'])]
        
#         # If no recommendations found, use some generic ones
#         if not recommendations:
#             recommendations = [
#                 "Optimize inventory for top-performing product lines",
#                 "Focus marketing efforts on key customer segments",
#                 "Investigate underperforming branches",
#                 "Consider expanding payment options based on preferred methods"
#             ]
        
#         for rec in recommendations:
#             if rec:  # Check if not empty
#                 story.append(Paragraph(f"• {rec}", body_style))
#                 story.append(Spacer(1, 0.1*inch))
    
#     # Build the PDF
#     doc.build(story)
#     buffer.seek(0)
#     return buffer
# import io
# import logging
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4, letter
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch, cm
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
# from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
# import matplotlib.pyplot as plt
# import pandas as pd
# from datetime import datetime
# from io import BytesIO

# # Set up logging
# logger = logging.getLogger(__name__)

# def create_pdf_report(data, suggestions, summary):
#     """
#     Create a professional PDF report with graphs and analysis
    
#     Args:
#         data: List of dictionaries containing business data
#         suggestions: List of graph suggestions from Gemini
#         summary: Business analysis summary text
        
#     Returns:
#         BytesIO: The PDF file as a bytes buffer
#     """
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter, 
#                             rightMargin=72, leftMargin=72,
#                             topMargin=72, bottomMargin=72)
    
#     story = []
    
#     # Define styles
#     styles = getSampleStyleSheet()
    
#     # Create custom styles
#     title_style = ParagraphStyle(
#         'Title',
#         parent=styles['Title'],
#         fontSize=24,
#         spaceAfter=12
#     )
    
#     subtitle_style = ParagraphStyle(
#         'Subtitle',
#         parent=styles['Heading2'],
#         fontSize=18,
#         spaceAfter=6
#     )
    
#     body_style = ParagraphStyle(
#         'Body',
#         parent=styles['Normal'],
#         fontSize=11,
#         leading=14,
#         alignment=TA_JUSTIFY
#     )
    
#     # Add title and date
#     story.append(Paragraph("Business Intelligence Report", title_style))
#     current_date = datetime.now().strftime("%B %d, %Y")
#     story.append(Paragraph(f"Generated on {current_date}", styles['Italic']))
#     story.append(Spacer(1, 0.25*inch))
    
#     # Add summary section
#     story.append(Paragraph("Executive Summary", subtitle_style))
#     story.append(Spacer(1, 0.1*inch))
#     story.append(Paragraph(summary, body_style))
#     story.append(Spacer(1, 0.25*inch))
    
#     # Add data overview
#     df = pd.DataFrame(data)
#     story.append(Paragraph("Data Overview", subtitle_style))
#     story.append(Spacer(1, 0.1*inch))
    
#     # Create a summary based on available data
#     summary_data = [["Total Records", str(len(df))]]
    
#     # Check for date field - might be 'date' or 'Date'
#     date_field = None
#     for potential_date_field in ['date', 'Date']:
#         if potential_date_field in df.columns:
#             date_field = potential_date_field
#             break
    
#     if date_field:
#         try:
#             min_date = pd.to_datetime(df[date_field].min()).strftime('%Y-%m-%d')
#             max_date = pd.to_datetime(df[date_field].max()).strftime('%Y-%m-%d')
#             date_range = f"{min_date} to {max_date}"
#             summary_data.append(["Date Range", date_range])
#         except:
#             pass
    
#     # Check for financial metrics based on data structure
#     # For stock data
#     if 'Close' in df.columns:
#         avg_close = df['Close'].mean()
#         summary_data.append(["Average Close Price", f"${avg_close:.2f}"])
        
#         if 'Volume' in df.columns:
#             total_volume = df['Volume'].sum()
#             summary_data.append(["Total Volume", f"{total_volume:,}"])
    
#     # For sales data (from original example)
#     elif 'total' in df.columns:
#         total_revenue = df['total'].sum()
#         summary_data.append(["Total Revenue", f"${total_revenue:.2f}"])
    
#     # Check for branch or symbol
#     for field in ['branch', 'Symbol']:
#         if field in df.columns:
#             count = len(df[field].unique())
#             label = "Number of Branches" if field == 'branch' else "Number of Symbols"
#             summary_data.append([label, str(count)])
#             break
    
#     # Create the table
#     t = Table(summary_data, colWidths=[2*inch, 3*inch])
#     t.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (0, -1), colors.lavender),
#         ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
#         ('ALIGN', (0, 0), (0, -1), 'LEFT'),
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black)
#     ]))
    
#     story.append(t)
#     story.append(Spacer(1, 0.25*inch))
    
#     # Visualizations section
#     story.append(Paragraph("Key Business Insights", subtitle_style))
#     story.append(Spacer(1, 0.1*inch))
    
#     # Import generate_chart inside the function to avoid circular imports
#     from graph_gen import generate_chart
    
#     # Generate and add charts - Use in-memory approach instead of temp files
#     for i, chart in enumerate(suggestions):
#         if not isinstance(chart, dict):
#             continue
            
#         title = chart.get("title", f"Chart {i+1}")
#         insight = chart.get("insight", "No specific insight provided.")
        
#         # Add chart title and insight
#         story.append(Paragraph(title, styles['Heading3']))
#         story.append(Paragraph(insight, body_style))
#         story.append(Spacer(1, 0.1*inch))
        
#         try:
#             # Log which chart we're generating for debugging
#             logger.info(f"Generating chart {i}: {title}")
            
#             # Generate chart for PDF (using light theme)
#             chart_fig = generate_chart(df, chart, for_pdf=True)
            
#             # Save chart directly to BytesIO buffer instead of temp file
#             img_buffer = BytesIO()
#             chart_fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
#             plt.close(chart_fig)
#             img_buffer.seek(0)
            
#             # Add image to the report with proper sizing
#             img = Image(img_buffer, width=6*inch, height=3*inch)
#             story.append(img)
            
#         except Exception as e:
#             logger.error(f"Error generating chart {i}: {str(e)}", exc_info=True)
#             story.append(Paragraph(f"Error generating chart: {str(e)}", styles['Normal']))
        
#         # Add space after each chart
#         story.append(Spacer(1, 0.3*inch))
        
#         # Add page break after every second chart (except the last)
#         if i % 2 == 1 and i < len(suggestions) - 1:
#             story.append(PageBreak())
    
#     # Add recommendations section if we have at least one chart completed
#     if suggestions:
#         story.append(PageBreak())
#         story.append(Paragraph("Recommendations", subtitle_style))
#         story.append(Spacer(1, 0.1*inch))
        
#         # Try to extract recommendations from summary
#         recommendation_paragraphs = summary.split('.')
#         recommendations = [para.strip() for para in recommendation_paragraphs 
#                           if any(keyword in para.lower() for keyword in 
#                                 ['recommend', 'should', 'could', 'opportunity', 'improve'])]
        
#         # If no recommendations found, use some generic ones based on data type
#         if not recommendations:
#             if 'Close' in df.columns:  # Stock data
#                 recommendations = [
#                     "Monitor price volatility patterns for trading opportunities",
#                     "Analyze volume trends to identify potential market sentiment shifts",
#                     "Consider correlation analysis with market indices for broader context",
#                     "Implement technical analysis indicators for trading decisions"
#                 ]
#             else:  # Default business recommendations
#                 recommendations = [
#                     "Optimize inventory for top-performing product lines",
#                     "Focus marketing efforts on key customer segments",
#                     "Investigate underperforming branches",
#                     "Consider expanding payment options based on preferred methods"
#                 ]
        
#         for rec in recommendations:
#             if rec:  # Check if not empty
#                 story.append(Paragraph(f"• {rec}", body_style))
#                 story.append(Spacer(1, 0.1*inch))
    
#     # Build the PDF
#     doc.build(story)
#     buffer.seek(0)
#     return buffer

import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from io import BytesIO
import logging

# Set up logging
logger = logging.getLogger(__name__)

def create_pdf_report(data, suggestions, summary):
    """
    Create a professional PDF report with graphs and analysis
    
    Args:
        data: List of dictionaries containing business data
        suggestions: List of graph suggestions from Gemini
        summary: Business analysis summary text
        
    Returns:
        BytesIO: The PDF file as a bytes buffer
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Create custom styles with improved formatting
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=16,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceBefore=12,
        spaceAfter=8,
        textColor=colors.navy
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_JUSTIFY
    )
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Italic'],
        alignment=TA_CENTER,
        fontSize=10,
        spaceAfter=24
    )
    
    chart_title_style = ParagraphStyle(
        'ChartTitle',
        parent=styles['Heading3'],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.darkblue
    )
    
    insight_style = ParagraphStyle(
        'Insight',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        firstLineIndent=0,
        alignment=TA_JUSTIFY
    )
    
    bullet_style = ParagraphStyle(
        'BulletPoint',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        leftIndent=20,
        firstLineIndent=-15
    )
    
    # Add title and date
    story.append(Paragraph("Business Intelligence Report", title_style))
    current_date = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(f"Generated on {current_date}", date_style))
    
    # Add executive summary section with better formatting
    story.append(Paragraph("Executive Summary", subtitle_style))
    
    # Format summary into well-structured paragraphs
    paragraphs = summary.split('\n\n')
    if len(paragraphs) == 1:  # If it's a single block, try to break it up
        sentences = summary.split('. ')
        formatted_paragraphs = []
        current_paragraph = []
        
        for sentence in sentences:
            current_paragraph.append(sentence)
            if len(current_paragraph) >= 3:  # Group ~3 sentences per paragraph
                formatted_paragraphs.append('. '.join(current_paragraph) + '.')
                current_paragraph = []
        
        # Add any remaining sentences
        if current_paragraph:
            formatted_paragraphs.append('. '.join(current_paragraph) + '.')
        
        # Join paragraphs with proper spacing
        for para in formatted_paragraphs:
            story.append(Paragraph(para, body_style))
            story.append(Spacer(1, 0.1*inch))
    else:
        for para in paragraphs:
            if para.strip():  # Check if paragraph isn't empty
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.15*inch))
    
    # Add data overview with improved table styling
    df = pd.DataFrame(data)
    story.append(Paragraph("Data Overview", subtitle_style))
    
    # Format date strings to be more readable
    date_range = "Date range unavailable"
    for date_col in ['date', 'Date']:
        if date_col in df.columns:
            try:
                min_date = pd.to_datetime(df[date_col].min()).strftime('%Y-%m-%d')
                max_date = pd.to_datetime(df[date_col].max()).strftime('%Y-%m-%d')
                date_range = f"{min_date} to {max_date}"
                break
            except:
                pass
    
    # Try to calculate total revenue or other metrics based on available columns
    total_rev = "N/A"
    if 'total' in df.columns:
        total_rev = f"${df['total'].sum():.2f}"
    
    # Create a simple data summary table with better styling
    summary_data = [
        ["Total Records", str(len(df))],
        ["Date Range", date_range],
    ]
    
    # Add revenue info if available
    if total_rev != "N/A":
        summary_data.append(["Total Revenue", total_rev])
    
    # Add branch info if available
    if 'branch' in df.columns:
        summary_data.append(["Number of Branches", str(len(df['branch'].unique()))])
    elif 'symbol' in df.columns or 'Symbol' in df.columns:  # For stock data
        symbol_col = 'symbol' if 'symbol' in df.columns else 'Symbol'
        summary_data.append(["Number of Symbols", str(len(df[symbol_col].unique()))])
    
    # Add average price if available for stock data
    for close_col in ['close', 'Close']:
        if close_col in df.columns:
            summary_data.append(["Average Close Price", f"${df[close_col].mean():.2f}"])
            break
    
    # Add volume info for stock data
    for vol_col in ['volume', 'Volume']:
        if vol_col in df.columns:
            summary_data.append(["Total Volume", f"{df[vol_col].sum():,}"])
            break
    
    # Create a better styled table
    col_widths = [2.5*inch, 2.5*inch]
    t = Table(summary_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lavender),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Right-align values
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Visualizations section with improved styling
    story.append(Paragraph("Key Business Insights", subtitle_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Import generate_chart inside the function to avoid circular imports
    from graph_gen import generate_chart
    
    # Generate and add charts with better formatting
    for i, chart in enumerate(suggestions):
        if not isinstance(chart, dict):
            continue
            
        title = chart.get("title", f"Chart {i+1}")
        insight = chart.get("insight", "No specific insight provided.")
        
        # Add chart title with better styling
        story.append(Paragraph(title, chart_title_style))
        
        # Add insight with proper formatting
        story.append(Paragraph(insight, insight_style))
        story.append(Spacer(1, 0.15*inch))
        
        try:
            # Generate chart for PDF (using light theme)
            chart_fig = generate_chart(df, chart, for_pdf=True)
            
            # Save chart directly to BytesIO buffer
            img_buffer = BytesIO()
            chart_fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=200)
            plt.close(chart_fig)
            img_buffer.seek(0)
            
            # Add image to the report with proper sizing and centering
            img = Image(img_buffer, width=6*inch, height=3*inch)
            img.hAlign = 'CENTER'  # Center the image
            story.append(img)
            
        except Exception as e:
            logger.error(f"Error generating chart {i}: {str(e)}", exc_info=True)
            story.append(Paragraph(f"Error generating chart: {str(e)}", styles['Normal']))
        
        # Add space after each chart
        story.append(Spacer(1, 0.4*inch))
        
        # Add page break after every second chart (except the last)
        if i % 2 == 1 and i < len(suggestions) - 1:
            story.append(PageBreak())
    
    # Add recommendations section with proper formatting
    if suggestions:
        story.append(PageBreak())
        story.append(Paragraph("Recommendations", subtitle_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Try to extract recommendations from summary
        recommendation_paragraphs = summary.split('.')
        recommendations = [para.strip() for para in recommendation_paragraphs 
                          if any(keyword in para.lower() for keyword in 
                                ['recommend', 'should', 'could', 'opportunity', 'improve'])]
        
        # If no recommendations found, use some generic ones
        if not recommendations:
            recommendations = [
                "Optimize inventory for top-performing product lines",
                "Focus marketing efforts on key customer segments",
                "Investigate underperforming branches",
                "Consider expanding payment options based on preferred methods"
            ]
        
        # Create a proper bulleted list
        for rec in recommendations:
            if rec:  # Check if not empty
                # Clean up the recommendation text
                clean_rec = rec.strip()
                if clean_rec.startswith('•'):
                    clean_rec = clean_rec[1:].strip()
                    
                story.append(Paragraph(f"• {clean_rec}", bullet_style))
                story.append(Spacer(1, 0.1*inch))
    
    # Build the PDF
    doc.build(story)
    buffer.seek(0)
    return buffer