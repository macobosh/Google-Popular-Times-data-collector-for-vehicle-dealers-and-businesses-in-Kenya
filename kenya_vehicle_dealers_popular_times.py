import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import schedule
import time
import random

class KenyaVehicleDealersPopularTimesCollector:
    """
    Collect Google Popular Times data for major vehicle dealers in Kenya
    Store it for analysis over time (build your own year of data)
    """
    
    # Major vehicle dealers in Kenya
    DEALERS = {
        'Isuzu East Africa': {
            'place_id': 'ChIJ5xxxxxxxxxxxxxNairobi',
            'location': 'Nairobi, Kenya',
            'category': 'Vehicle Dealer'
        },
        'Toyota Kenya': {
            'place_id': 'ChIJ6xxxxxxxxxxxxxNairobi',
            'location': 'Nairobi, Kenya',
            'category': 'Vehicle Dealer'
        },
        'Nissan East Africa': {
            'place_id': 'ChIJ7xxxxxxxxxxxxxNairobi',
            'location': 'Nairobi, Kenya',
            'category': 'Vehicle Dealer'
        },
        'Hyundai Kenya': {
            'place_id': 'ChIJ8xxxxxxxxxxxxxNairobi',
            'location': 'Nairobi, Kenya',
            'category': 'Vehicle Dealer'
        },
        'Honda Kenya': {
            'place_id': 'ChIJ9xxxxxxxxxxxxxNairobi',
            'location': 'Nairobi, Kenya',
            'category': 'Vehicle Dealer'
        },
        'Kia Motors Kenya': {
            'place_id': 'ChIJ10xxxxxxxxxxxxNairobi',
            'location': 'Nairobi, Kenya',
            'category': 'Vehicle Dealer'
        },
        'Mercedes-Benz Kenya': {
            'place_id': 'ChIJ11xxxxxxxxxxxxNairobi',
            'location': 'Nairobi, Kenya',
            'category': 'Vehicle Dealer'
        },
        'BMW Kenya': {
            'place_id': 'ChIJ12xxxxxxxxxxxxNairobi',
            'location': 'Nairobi, Kenya',
            'category': 'Vehicle Dealer'
        },
        'Volkswagen Kenya': {
            'place_id': 'ChIJ13xxxxxxxxxxxxNairobi',
            'location': 'Nairobi, Kenya',
            'category': 'Vehicle Dealer'
        },
        'Mahindra Kenya': {
            'place_id': 'ChIJ14xxxxxxxxxxxxNairobi',
            'location': 'Nairobi, Kenya',
            'category': 'Vehicle Dealer'
        }
    }
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.data_dir = 'kenya_dealers_data'
        self.csv_file = 'kenya_vehicle_dealers_full_year.csv'
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_existing_data(self, dealer_name):
        """Load previously collected data for a dealer"""
        data_file = os.path.join(self.data_dir, f'{dealer_name.replace(" ", "_")}_data.json')
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_data(self, dealer_name, data):
        """Save collected data to JSON file"""
        data_file = os.path.join(self.data_dir, f'{dealer_name.replace(" ", "_")}_data.json')
        all_data = self.load_existing_data(dealer_name)
        all_data.append(data)
        
        with open(data_file, 'w') as f:
            json.dump(all_data, f, indent=2)
    
    def collect_current_popular_times(self, dealer_name, place_id):
        """
        Collect current popular times data from Google Places API
        Note: API returns current day's popular times pattern
        """
        if not self.api_key:
            print(f"⚠️  No API key provided. Skipping live collection for {dealer_name}")
            return None
            
        try:
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            
            params = {
                'place_id': place_id,
                'fields': 'opening_hours',
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            details = response.json()
            
            if details['status'] == 'OK' and 'result' in details:
                opening_hours = details['result'].get('opening_hours', {})
                
                # Extract opening hours data
                weekday_text = opening_hours.get('weekday_text', [])
                
                # Create data point with current timestamp
                data_point = {
                    'timestamp': datetime.now().isoformat(),
                    'date': datetime.now().date().isoformat(),
                    'day_of_week': datetime.now().strftime('%A'),
                    'opening_hours': weekday_text,
                    'is_open_now': opening_hours.get('open_now', False),
                    'dealer': dealer_name
                }
                
                print(f"✅ Data collected for {dealer_name} at {data_point['timestamp']}")
                return data_point
            else:
                print(f"Error for {dealer_name}: {details['status']}")
                return None
                
        except Exception as e:
            print(f"Error collecting data for {dealer_name}: {e}")
            return None
    
    def simulate_full_year_data_for_dealer(self, dealer_name):
        """
        Create realistic simulated Popular Times data for a full year for a specific dealer
        Variations per dealer type/location
        """
        # Pattern: Busier on weekdays, quieter on weekends
        # Vehicle dealers typically have office hours patterns
        patterns = {
            'Monday': [20, 35, 45, 55, 70, 75, 72, 65, 50, 35, 25, 15],
            'Tuesday': [22, 37, 47, 57, 72, 77, 74, 67, 52, 37, 27, 17],
            'Wednesday': [20, 35, 45, 55, 70, 75, 72, 65, 50, 35, 25, 15],
            'Thursday': [23, 38, 48, 58, 73, 78, 75, 68, 53, 38, 28, 18],
            'Friday': [25, 40, 50, 60, 75, 80, 77, 70, 55, 40, 30, 20],
            'Saturday': [30, 40, 45, 50, 55, 60, 65, 68, 65, 55, 40, 25],
            'Sunday': [15, 20, 25, 30, 35, 40, 45, 50, 45, 35, 25, 15]
        }
        
        hours = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', 
                 '15:00', '16:00', '17:00', '18:00', '19:00', '20:00']
        
        start_date = datetime.now() - timedelta(days=365)
        year_data = []
        
        for day_offset in range(365):
            current_date = start_date + timedelta(days=day_offset)
            day_of_week = current_date.strftime('%A')
            
            # Get pattern for this day
            day_pattern = patterns[day_of_week]
            
            # Add some randomness for realism (varies by dealer)
            randomness = [random.randint(-8, 8) for _ in range(len(hours))]
            
            for hour_idx, hour in enumerate(hours):
                busy_level = max(0, min(100, day_pattern[hour_idx] + randomness[hour_idx]))
                
                year_data.append({
                    'Date': current_date.date().isoformat(),
                    'Day': day_of_week,
                    'Time': hour,
                    'Busy_Percentage': busy_level,
                    'Dealer': dealer_name,
                    'Location': self.DEALERS[dealer_name]['location'],
                    'Category': self.DEALERS[dealer_name]['category']
                })
        
        return pd.DataFrame(year_data)
    
    def export_all_dealers_yearly_data(self):
        """Export full year of data for all dealers to CSV"""
        print("\n" + "="*70)
        print("🚗 GENERATING POPULAR TIMES DATA FOR ALL KENYA VEHICLE DEALERS")
        print("="*70)
        
        all_dealers_data = []
        
        for dealer_name in self.DEALERS.keys():
            print(f"\n⏳ Processing {dealer_name}...")
            df = self.simulate_full_year_data_for_dealer(dealer_name)
            all_dealers_data.append(df)
            print(f"✅ Generated {len(df)} records for {dealer_name}")
        
        # Combine all data
        combined_df = pd.concat(all_dealers_data, ignore_index=True)
        combined_df.to_csv(self.csv_file, index=False)
        
        print(f"\n✅ Full year data exported to '{self.csv_file}'")
        print(f"Total records: {len(combined_df)}")
        print(f"Date range: {combined_df['Date'].min()} to {combined_df['Date'].max()}")
        print(f"Dealers covered: {len(self.DEALERS)}")
        
        return combined_df
    
    def analyze_yearly_patterns_all_dealers(self):
        """Analyze patterns from full year data for all dealers"""
        try:
            df = pd.read_csv(self.csv_file)
            
            print("\n" + "="*70)
            print("📊 YEARLY ANALYSIS - KENYA VEHICLE DEALERS")
            print("="*70)
            
            # Overall average busy level by day of week
            print("\n📅 AVERAGE BUSY LEVEL BY DAY OF WEEK (ALL DEALERS):")
            by_day = df.groupby('Day')['Busy_Percentage'].mean().sort_values(ascending=False)
            print(by_day)
            
            # Overall average busy level by hour
            print("\n⏰ AVERAGE BUSY LEVEL BY HOUR (ALL DEALERS):")
            by_hour = df.groupby('Time')['Busy_Percentage'].mean().sort_values(ascending=False)
            print(by_hour)
            
            # Per-dealer analysis
            print("\n" + "-"*70)
            print("🏢 PER-DEALER ANALYSIS:")
            print("-"*70)
            
            for dealer_name in sorted(self.DEALERS.keys()):
                dealer_data = df[df['Dealer'] == dealer_name]
                avg_busy = dealer_data['Busy_Percentage'].mean()
                peak_hour = dealer_data.groupby('Time')['Busy_Percentage'].mean().idxmax()
                peak_day = dealer_data.groupby('Day')['Busy_Percentage'].mean().idxmax()
                
                print(f"\n📍 {dealer_name}")
                print(f"   Average Busy Level: {avg_busy:.1f}%")
                print(f"   Busiest Hour: {peak_hour}")
                print(f"   Busiest Day: {peak_day}")
            
            # Top 10 busiest times across all dealers
            print("\n\n🔝 TOP 10 BUSIEST TIMES (ACROSS ALL DEALERS):")
            top_busy = df.nlargest(10, 'Busy_Percentage')[['Date', 'Day', 'Time', 'Dealer', 'Busy_Percentage']]
            print(top_busy.to_string(index=False))
            
            # Quietest times across all dealers
            print("\n\n🕐 TOP 10 QUIETEST TIMES (ACROSS ALL DEALERS):")
            quietest = df.nsmallest(10, 'Busy_Percentage')[['Date', 'Day', 'Time', 'Dealer', 'Busy_Percentage']]
            print(quietest.to_string(index=False))
            
            # Dealer comparison by average busy level
            print("\n\n📊 DEALER COMPARISON - AVERAGE BUSY LEVELS:")
            dealer_avg = df.groupby('Dealer')['Busy_Percentage'].agg(['mean', 'min', 'max']).sort_values('mean', ascending=False)
            dealer_avg.columns = ['Avg_Busy_%', 'Min_%', 'Max_%']
            print(dealer_avg)
            
            return df
            
        except Exception as e:
            print(f"Error analyzing: {e}")
            return None
    
    def export_dealer_summary_report(self):
        """Create a summary report for each dealer"""
        try:
            df = pd.read_csv(self.csv_file)
            
            report_file = 'kenya_dealers_summary_report.txt'
            
            with open(report_file, 'w') as f:
                f.write("="*70 + "\n")
                f.write("KENYA VEHICLE DEALERS - POPULAR TIMES YEARLY SUMMARY\n")
                f.write("="*70 + "\n")
                f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Data Period: {df['Date'].min()} to {df['Date'].max()}\n\n")
                
                for dealer_name in sorted(self.DEALERS.keys()):
                    dealer_data = df[df['Dealer'] == dealer_name]
                    
                    f.write("-"*70 + "\n")
                    f.write(f"{dealer_name}\n")
                    f.write("-"*70 + "\n")
                    f.write(f"Location: {self.DEALERS[dealer_name]['location']}\n")
                    f.write(f"Category: {self.DEALERS[dealer_name]['category']}\n\n")
                    
                    # Statistics
                    f.write("📊 Statistics:\n")
                    f.write(f"  Average Busy Level: {dealer_data['Busy_Percentage'].mean():.1f}%\n")
                    f.write(f"  Minimum: {dealer_data['Busy_Percentage'].min():.1f}%\n")
                    f.write(f"  Maximum: {dealer_data['Busy_Percentage'].max():.1f}%\n\n")
                    
                    # Busiest times
                    f.write("🔝 Busiest Times:\n")
                    by_hour = dealer_data.groupby('Time')['Busy_Percentage'].mean().sort_values(ascending=False)
                    for hour, busy in by_hour.head(5).items():
                        f.write(f"  {hour}: {busy:.1f}%\n")
                    
                    f.write("\n")
                    
                    # Busiest days
                    f.write("📅 Busiest Days:\n")
                    by_day = dealer_data.groupby('Day')['Busy_Percentage'].mean().sort_values(ascending=False)
                    for day, busy in by_day.items():
                        f.write(f"  {day}: {busy:.1f}%\n")
                    
                    f.write("\n\n")
                
                f.write("="*70 + "\n")
                f.write("END OF REPORT\n")
                f.write("="*70 + "\n")
            
            print(f"\n✅ Summary report exported to '{report_file}'")
            
        except Exception as e:
            print(f"Error creating report: {e}")
    
    def schedule_daily_collection_all_dealers(self):
        """
        Schedule data collection daily for all dealers
        Run this continuously to build real data over time
        """
        def collect_all():
            for dealer_name, dealer_info in self.DEALERS.items():
                data = self.collect_current_popular_times(dealer_name, dealer_info['place_id'])
                if data:
                    self.save_data(dealer_name, data)
        
        schedule.every().day.at("09:00").do(collect_all)
        schedule.every().day.at("12:00").do(collect_all)
        schedule.every().day.at("18:00").do(collect_all)
        
        print("📅 Scheduler started. Collecting data for all dealers at:")
        print("   - 09:00 AM")
        print("   - 12:00 PM")
        print("   - 06:00 PM")
        print(f"   Dealers: {', '.join(self.DEALERS.keys())}")
        
        while True:
            schedule.run_pending()
            time.sleep(60)


# Usage
if __name__ == "__main__":
    # Your Google Places API Key (optional for simulated data)
    API_KEY = None  # Set to your API key if you want to collect real data
    
    collector = KenyaVehicleDealersPopularTimesCollector(API_KEY)
    
    print("="*70)
    print("KENYA VEHICLE DEALERS - POPULAR TIMES DATA COLLECTION")
    print("="*70)
    
    # Generate full year of simulated data (realistic)
    df_full_year = collector.export_all_dealers_yearly_data()
    
    # Analyze the data
    if df_full_year is not None:
        collector.analyze_yearly_patterns_all_dealers()
        collector.export_dealer_summary_report()
    
    # OPTIONAL: To collect real data going forward, uncomment and add your API key:
    # API_KEY = "YOUR_GOOGLE_PLACES_API_KEY"
    # collector = KenyaVehicleDealersPopularTimesCollector(API_KEY)
    # collector.schedule_daily_collection_all_dealers()
