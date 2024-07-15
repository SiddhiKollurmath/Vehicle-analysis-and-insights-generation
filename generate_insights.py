import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_insights(excel_file_path = 'car_plate_data.xlsx',output_dir = 'graphs'):
    df = pd.read_excel(excel_file_path)

    df["DateTime"] = pd.to_datetime(df['Date'] + ' '+df['Time'])
 
    df['Date'] = df['DateTime'].dt.date
    df['Hour'] = df['DateTime'].dt.hour

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dates = df['Date'].unique()

    for date in dates:
        df_date = df[df['Date'] == date]

        vehicle_counts_by_interval = df_date.groupby('Hour').size()
    
        all_hours = list(range(24))
        vehicle_counts_by_interval = vehicle_counts_by_interval.reindex(all_hours,fill_value=0)


        plt.figure(figsize=(12,6))
        vehicle_counts_by_interval.plot(kind = 'bar')
        plt.xlabel('Hour interval')
        plt.ylabel('Number of Vehicles')
        plt.title(f'Number of Vehicles Entries by Hour for {date}')
        plt.xticks(range(24),[f'{h}:00-{h+1}:00' for h in range(24)],rotation = 45)
        plt.tight_layout()
        plt.savefig('vehicle_entries_by_hrinterval.png')
        
        output_file = os.path.join(output_dir, f'{date}.png')
        plt.savefig(output_file)
        plt.close()

if __name__ == "__main__":
    generate_insights()