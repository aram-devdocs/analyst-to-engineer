import os
import requests
from datetime import datetime
import pandas as pd
from typing import Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import argparse


# https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet
# https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2024-01.parquet
# https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2024-01.parquet
# https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2024-01.parquet

def get_existing_downloads(base_path: str) -> Set[Tuple[str, int, int]]:
    """
    Scan the existing directory structure and return a set of (data_type, year, month)
    for files that have already been downloaded
    """
    existing = set()
    if not os.path.exists(base_path):
        return existing
        
    for year_dir in os.listdir(base_path):
        year_path = os.path.join(base_path, year_dir)
        if not os.path.isdir(year_path):
            continue
            
        try:
            year = int(year_dir)
            for month_dir in os.listdir(year_path):
                month_path = os.path.join(year_path, month_dir)
                if not os.path.isdir(month_path):
                    continue
                    
                try:
                    month = int(month_dir)
                    # Check for files in the month directory
                    for file in os.listdir(month_path):
                        if file.endswith('.parquet'):
                            # Extract data type from filename (e.g., yellow_tripdata_2020-01.parquet)
                            data_type = file.split('_')[0]
                            existing.add((data_type, year, month))
                except ValueError:
                    continue
        except ValueError:
            continue
            
    return existing

def create_directory_structure(base_path):
    """Create directory structure if it doesn't exist"""
    if not os.path.exists(base_path):
        os.makedirs(base_path)

def download_file(url: str, output_path: str) -> Tuple[str, bool]:
    """
    Download a file from url to output_path
    Returns tuple of (output_path, success)
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return output_path, True
    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        return output_path, False

def download_worker(args):
    """Worker function for thread pool"""
    url, output_path = args
    return download_file(url, output_path)

def scrape_taxi_data(start_year=2009, end_year=2024, data_type='yellow', max_workers=4):
    """
    Scrape taxi data from NYC TLC website using multiple threads
    
    Args:
        start_year (int): Start year for data collection
        end_year (int): End year for data collection
        data_type (str): Type of taxi data ('yellow', 'green', 'fhv', 'fhvhv')
        max_workers (int): Maximum number of concurrent downloads
    """
    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data"
    base_path = "data/taxi_data"
    
    # Create base directory
    create_directory_structure(base_path)
    
    # Get existing downloads
    existing_downloads = get_existing_downloads(base_path)
    
    current_year = datetime.now().year
    end_year = min(end_year, current_year)
    
    # Prepare download tasks
    download_tasks = []
    for year in range(start_year, end_year + 1):
        year_path = os.path.join(base_path, str(year))
        create_directory_structure(year_path)
        
        for month in range(1, 13):
            if year == current_year and month > datetime.now().month:
                continue
                
            if (data_type, year, month) in existing_downloads:
                continue
                
            month_str = str(month).zfill(2)
            month_path = os.path.join(year_path, month_str)
            create_directory_structure(month_path)
            
            file_name = f"{data_type}_tripdata_{year}-{month_str}.parquet"
            url = f"{base_url}/{data_type}_tripdata_{year}-{month_str}.parquet"
            output_path = os.path.join(month_path, file_name)
            
            download_tasks.append((url, output_path))
    
    if not download_tasks:
        print(f"All {data_type} taxi data files for the specified period already exist.")
        return
    
    print(f"Found {len(download_tasks)} files to download")
    successful = 0
    failed = 0
    
    # Create progress bar
    pbar = tqdm(total=len(download_tasks), desc="Downloading files")
    
    # Use ThreadPoolExecutor for concurrent downloads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_url = {
            executor.submit(download_worker, task): task[0] 
            for task in download_tasks
        }
        
        # Process completed downloads
        for future in as_completed(future_to_url):
            output_path, success = future.result()
            if success:
                successful += 1
            else:
                failed += 1
            pbar.update(1)
    
    pbar.close()
    
    print(f"\nDownload complete:")
    print(f"Successfully downloaded: {successful}")
    print(f"Failed downloads: {failed}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download NYC TLC trip record data')
    parser.add_argument('--start-year', 
                      type=int, 
                      default=2009,
                      help='Start year for data collection (default: 2009)')
    parser.add_argument('--end-year', 
                      type=int, 
                      default=datetime.now().year,
                      help='End year for data collection (default: current year)')
    parser.add_argument('--data-type', 
                      type=str, 
                      default='yellow',
                      choices=['yellow', 'green', 'fhv', 'fhvhv'],
                      help='Type of taxi data to download (default: yellow)')
    parser.add_argument('--max-workers', 
                      type=int, 
                      default=4,
                      help='Maximum number of concurrent downloads (default: 4)')

    args = parser.parse_args()

    # Validate years
    if args.start_year > args.end_year:
        parser.error("start-year cannot be greater than end-year")
    
    if args.start_year < 2009:
        parser.error("start-year cannot be earlier than 2009")
    
    if args.end_year > datetime.now().year:
        parser.error("end-year cannot be in the future")

    # Download taxi data with specified parameters
    scrape_taxi_data(
        start_year=args.start_year,
        end_year=args.end_year,
        data_type=args.data_type,
        max_workers=args.max_workers
    )
