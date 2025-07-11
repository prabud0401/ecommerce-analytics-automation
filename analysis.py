# analysis.py

import os
import json
import logging
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import BarChart, Reference
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import plotly.express as px
import plotly.io as pio

import config

def load_all_scraped_data():
    """Loads the consolidated JSON data file."""
    if not os.path.exists(config.OUTPUT_FILE_PATH):
        logging.warning(f"Data file not found at {config.OUTPUT_FILE_PATH}. Analysis cannot proceed.")
        return None
        
    with open(config.OUTPUT_FILE_PATH, 'r') as f:
        data = json.load(f)
    
    logging.info(f"Loaded {len(data)} total products from {config.OUTPUT_FILE_PATH}.")
    return pd.DataFrame(data)

def clean_data(df):
    """Cleans and preprocesses the DataFrame."""
    if df is None or df.empty:
        return pd.DataFrame()

    # Clean price column
    df['price'] = df['price'].replace({r'\$': '', r',': ''}, regex=True)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    # Clean rating and review_count columns
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['review_count'] = pd.to_numeric(df['review_count'], errors='coerce')

    df.dropna(subset=['price', 'title'], inplace=True)
    logging.info(f"Data cleaned. {len(df)} products remain after cleaning.")
    return df

def create_excel_report(df):
    """Creates a multi-sheet Excel report with analysis."""
    if df.empty:
        logging.warning("DataFrame is empty, skipping Excel report generation.")
        return

    output_path = f"{config.REPORTS_DIR}/Product_Analysis_Report.xlsx"
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sheet 1: Product Summary
        df.to_excel(writer, sheet_name='Product Summary', index=False)
        logging.info("Created 'Product Summary' sheet.")

        # Sheet 2: Brand Analysis (Pivot Table)
        pivot_table = df.pivot_table(
            index='brand',
            values=['price', 'rating', 'review_count'],
            aggfunc={'price': 'mean', 'rating': 'mean', 'review_count': 'sum'}
        ).round(2)
        pivot_table.to_excel(writer, sheet_name='Brand Analysis')
        logging.info("Created 'Brand Analysis' pivot table sheet.")

        # Add a chart to the Brand Analysis sheet
        workbook = writer.book
        worksheet = workbook['Brand Analysis']
        chart = BarChart()
        chart.title = "Average Price by Brand"
        chart.y_axis.title = 'Average Price ($)'
        chart.x_axis.title = 'Brand'
        
        data = Reference(worksheet, min_col=2, min_row=1, max_row=pivot_table.shape[0] + 1, max_col=2)
        categories = Reference(worksheet, min_col=1, min_row=2, max_row=pivot_table.shape[0] + 1)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(categories)
        worksheet.add_chart(chart, "E5")

    logging.info(f"Excel report saved to {output_path}")

def create_pdf_report(df):
    """Generates a PDF summary report."""
    if df.empty:
        logging.warning("DataFrame is empty, skipping PDF report generation.")
        return
        
    output_path = f"{config.REPORTS_DIR}/Summary_Report.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("E-Commerce Product Analysis Report", styles['h1']))
    story.append(Spacer(1, 12))

    # --- Summary Section ---
    num_products = len(df)
    avg_price = df['price'].mean()
    story.append(Paragraph(f"This report summarizes the analysis of {num_products} laptops.", styles['BodyText']))
    story.append(Paragraph(f"The average price across all analyzed products is ${avg_price:.2f}.", styles['BodyText']))
    story.append(Spacer(1, 24))

    # --- Matplotlib Chart for PDF ---
    plt.figure(figsize=(8, 4))
    brand_avg_price = df.groupby('brand')['price'].mean().sort_values()
    brand_avg_price.plot(kind='bar', color=['skyblue', 'lightgreen', 'salmon'])
    plt.title('Average Laptop Price by Brand')
    plt.ylabel('Average Price ($)')
    plt.xlabel('Brand')
    plt.xticks(rotation=0)
    plt.tight_layout()
    chart_path = f"{config.REPORTS_DIR}/brand_price_chart.png"
    plt.savefig(chart_path)
    plt.close()
    
    story.append(Paragraph("Average Price by Brand", styles['h2']))
    story.append(Image(chart_path, width=400, height=200))
    story.append(Spacer(1, 24))

    # --- Top 5 Rated Laptops Table ---
    top_5_rated = df.sort_values(by='rating', ascending=False).head(5)
    top_5_data = [['Brand', 'Title', 'Rating']]
    for index, row in top_5_rated.iterrows():
        top_5_data.append([row['brand'], Paragraph(row['title'], styles['BodyText']), row['rating']])
    
    table = Table(top_5_data, colWidths=[70, 350, 50])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(Paragraph("Top 5 Rated Products", styles['h2']))
    story.append(table)

    doc.build(story)
    logging.info(f"PDF report saved to {output_path}")

def create_html_dashboard(df):
    """Generates an interactive HTML dashboard using Plotly."""
    if df.empty:
        logging.warning("DataFrame is empty, skipping HTML dashboard generation.")
        return

    output_path = f"{config.REPORTS_DIR}/Interactive_Dashboard.html"
    
    # Chart 1: Price Distribution by Brand
    fig1 = px.box(df, x='brand', y='price', title='Price Distribution by Brand', color='brand')
    
    # Chart 2: Rating vs. Review Count
    fig2 = px.scatter(df, x='rating', y='review_count', color='brand', size='price',
                      hover_name='title', title='Rating vs. Review Count (Size by Price)')

    with open(output_path, 'w') as f:
        f.write("<html><head><title>Product Analysis Dashboard</title></head><body>")
        f.write("<h1>Interactive Product Analysis Dashboard</h1>")
        f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(fig2.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write("</body></html>")

    logging.info(f"Interactive HTML dashboard saved to {output_path}")

def run_analysis():
    """Main function to run all analysis and reporting tasks."""
    logging.info("--- Starting Data Analysis and Reporting ---")
    
    df = load_all_scraped_data()
    df_cleaned = clean_data(df)
    
    if not df_cleaned.empty:
        create_excel_report(df_cleaned)
        create_pdf_report(df_cleaned)
        create_html_dashboard(df_cleaned)
    else:
        logging.error("Analysis could not be completed due to lack of valid data.")

    logging.info("--- Finished Data Analysis and Reporting ---")

if __name__ == '__main__':
    # Allows running analysis independently of scraping
    run_analysis()
