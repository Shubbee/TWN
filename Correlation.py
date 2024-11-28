import mikeio
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd

# Read dfs0 files
# Read dfs0 files
dfs0_file1 = r"C:\Users\ssin\Downloads\210189_Concatenated_30May2024.dfs0"
dfs0_file2 = r"C:\Users\ssin\Downloads\210188_Concatenated_30May2024.dfs0"

ds1 = mikeio.open(dfs0_file1).to_dataframe()
ds2 = mikeio.open(dfs0_file2).to_dataframe()

# Extract Pressure data
pressure1 = ds1['Pressure']
pressure2 = ds2['Pressure']


# Resample or interpolate to align timestamps
pressure1_resampled = pressure1.resample('H').mean().interpolate()
pressure2_resampled = pressure2.resample('H').mean().interpolate()

# Align the data
combined = pd.DataFrame({'pressure1': pressure1_resampled, 'pressure2': pressure2_resampled})

# Function to calculate correlation by day
def daily_correlation(df):
    df['date'] = df.index.date
    daily_corr = df.groupby('date').apply(lambda x: x['pressure1'].corr(x['pressure2']))
    return daily_corr

# Calculate daily correlation
correlation_by_day = daily_correlation(combined)

# Create interactive plot for daily correlation
fig = go.Figure()

fig.add_trace(go.Scatter(x=correlation_by_day.index, y=correlation_by_day, mode='lines', name='Daily Correlation'))

# Customize layout
fig.update_layout(
    title='Daily Correlation between 210189 and 210188 Sensor Pressure Data',
    xaxis_title='Date',
    yaxis_title='Correlation',
    legend_title='Legend',
    hovermode='x unified'
)

# Save plot as HTML file
pio.write_html(fig, file='daily_correlation_plot.html', auto_open=True)