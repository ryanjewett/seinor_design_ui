from datetime import datetime, timedelta

def generate_timestamps(start_date: str, end_date: str) -> list:
    # Parse the input dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    timestamps = []
    
    # Iterate through each day from start to end
    current_date = start
    while current_date <= end:
        # Create timestamp for every second of the current day
        for second in range(24 * 60 * 60):  # 86400 seconds in a day
            time_str = f"{current_date.strftime('%Y-%m-%d')}/{(timedelta(seconds=second) + datetime.min).time()}"
            timestamps.append(time_str)
        # Move to the next day
        current_date += timedelta(days=1)
    
    return timestamps

# Example usage
start_date = "2024-09-01"
end_date = "2024-09-02"
timestamps = generate_timestamps(start_date, end_date)

# Print the generated timestamps
for ts in timestamps:
    print(ts)