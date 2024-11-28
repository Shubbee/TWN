import mikeio
import plotly.graph_objects as go
import plotly.io as pio

# Read dfs0 files
dfs0_file1 = r"C:\Users\ssin\Downloads\210189_Concatenated_30May2024.dfs0"
dfs0_file2 = r"C:\Users\ssin\Downloads\210188_Concatenated_30May2024.dfs0"

ds1 = mikeio.open(dfs0_file1).to_dataframe()
ds2 = mikeio.open(dfs0_file2).to_dataframe()

# Create interactive plot
fig = go.Figure()

# Add Pressure data from the first dfs0 file to the plot
if 'Pressure' in ds1.columns:
    fig.add_trace(go.Scatter(x=ds1.index, y=ds1['Pressure'], mode='lines', name=f'{dfs0_file1} - Pressure'))

# Add Pressure data from the second dfs0 file to the plot
if 'Pressure' in ds2.columns:
    fig.add_trace(go.Scatter(x=ds2.index, y=ds2['Pressure'], mode='lines', name=f'{dfs0_file2} - Pressure'))

# Customize layout
fig.update_layout(
    title='Interactive Plot of Pressure Data from dfs0 Files',
    xaxis_title='Time',
    yaxis_title='Pressure',
    legend_title='Legend',
    hovermode='x unified'
)

# Save plot as HTML file
pio.write_html(fig, file='interactive_plot.html', auto_open=True)