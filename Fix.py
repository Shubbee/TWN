import mikeio
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

# Read dfs0 files
dfs0_file1 = r"C:\Users\ssin\Downloads\210189_Concatenated_30May2024.dfs0"
dfs0_file2 = r"C:\Users\ssin\Downloads\210188_Concatenated_30May2024.dfs0"

ds1 = mikeio.open(dfs0_file1).to_dataframe()
ds2 = mikeio.open(dfs0_file2).to_dataframe()

# Extract Pressure data
pressure1 = ds1['Pressure']
pressure2 = ds2['Pressure']

# Define the time ranges
sensor_off_start = '2024-04-18 17:00:00'
sensor_off_end = '2024-04-20 21:00:00'

# Remove the period when the sensor was off
pressure1_pre = pressure1[:sensor_off_start]
pressure1_post = pressure1[sensor_off_end:]
pressure2_pre = pressure2[:sensor_off_start]
pressure2_post = pressure2[sensor_off_end:]

# Resample or interpolate to align timestamps
pressure1_pre_resampled = pressure1_pre.resample('H').mean().interpolate()
pressure1_post_resampled = pressure1_post.resample('H').mean().interpolate()
pressure2_pre_resampled = pressure2_pre.resample('H').mean().interpolate()
pressure2_post_resampled = pressure2_post.resample('H').mean().interpolate()

# Function to calculate correlation by day
def daily_correlation(df1, df2):
    df = pd.DataFrame({'pressure1': df1, 'pressure2': df2})
    df['date'] = df.index.date
    daily_corr = df.groupby('date').apply(lambda x: x['pressure1'].corr(x['pressure2']))
    return daily_corr

# Calculate baseline correlation before sensor reset
baseline_corr = daily_correlation(pressure1_pre_resampled, pressure2_pre_resampled).mean()
print(f"Baseline correlation before sensor reset: {baseline_corr}")

# Function to calculate overall correlation after shifting
def calculate_shifted_correlation(shift, freq='H'):
    shifted = pressure2_post_resampled.shift(periods=shift, freq=freq)
    aligned = pd.concat([pressure1_post_resampled, shifted], axis=1).dropna()
    correlation = aligned.corr().iloc[0, 1]
    return correlation

# Step 1: Find the best hourly shift
hour_shifts = range(-100, 200)  # Test shifts from -100 to +200 hours
hourly_correlations = [calculate_shifted_correlation(shift) for shift in hour_shifts]

# Find the best hourly shift
best_hour_shift = hour_shifts[np.argmax(hourly_correlations)]
best_hour_correlation = max(hourly_correlations)
print(f"Best hourly shift: {best_hour_shift} hours, resulting in correlation: {best_hour_correlation}")

# Step 2: Refine the best hourly shift to the closest minute
minute_shifts = range(-60, 61)  # Test shifts from -60 to +60 minutes around the best hourly shift
minute_correlations = [calculate_shifted_correlation(best_hour_shift * 60 + shift, freq='T') for shift in minute_shifts]

# Find the best minute shift
best_minute_shift = minute_shifts[np.argmax(minute_correlations)]
best_minute_correlation = max(minute_correlations)
print(f"Best minute shift: {best_minute_shift} minutes, resulting in correlation: {best_minute_correlation}")

# Combine the best hourly shift and the best minute shift
total_best_shift_minutes = best_hour_shift * 60 + best_minute_shift
print(f"Total best shift: {total_best_shift_minutes} minutes")

# Apply the best shift
shifted_pressure2_post = pressure2_post_resampled.shift(periods=total_best_shift_minutes, freq='T')
pressure2_adjusted = pd.concat([pressure2_pre_resampled, shifted_pressure2_post])

# Create interactive plot
fig = go.Figure()

# Add original and adjusted Pressure data to plot
fig.add_trace(go.Scatter(x=pressure1.index, y=pressure1, mode='lines', name=f'210189 - Pressure'))
fig.add_trace(go.Scatter(x=pressure2.index, y=pressure2, mode='lines', name=f'210188 - Original Pressure'))
fig.add_trace(go.Scatter(x=pressure2_adjusted.index, y=pressure2_adjusted, mode='lines', name=f'210188 - Shifted Pressure'))

# Customize layout
fig.update_layout(
    title='210188 Pressure Data shift',
    xaxis_title='Time',
    yaxis_title='Pressure',
    legend_title='Legend',
    hovermode='x unified'
)

# Save plot as HTML file
pio.write_html(fig, file='interactive_plot_adjusted.html', auto_open=True)
