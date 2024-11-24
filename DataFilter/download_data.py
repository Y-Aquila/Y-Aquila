import requests
import os
import time

# Configuration
API_URL = "https://rapidmapping.emergency.copernicus.eu/backend/dashboard-api/public-activations/"
ACTIVATION_CODE = "EMSR773"
OUTPUT_DIR = "DATA/copernicus_data"
WAIT_TIME = 3  # Waiting time in seconds between downloads to avoid error 429 (rate limit)**

def download_file(url, output_path):
    try:
        print(f"Starting download from {url} to {output_path}")
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        print(f"Progress : {100*downloaded_size/total_size} %", end="\r")
            print(f"\nFile successfully downloaded : {output_path}")
        else:
            print(f"HTTP Error {response.status_code} for {url}")
    except Exception as e:
        print(f"Error while downloading from {url} : {e}")


def fetch_and_download_activation_data(activation_code):

    try:
        # Retrieve activation data
        response = requests.get(API_URL, params={"code": activation_code})
        if response.status_code == 200:
            data = response.json()
            print("Data successfully retrieved.")

            # Browse AOIs and their products
            aois = data.get("results", [{}])[0].get("aois", [])
            for aoi in aois:
                print(f"AOI Name: {aoi.get('name')}, AOI Number: {aoi.get('number')}")
                
                # Download base files (blpPath)
                blp_path = aoi.get("blpPath")
                if blp_path:
                    print(f"Base Layers Package Download : {blp_path}")
                    download_file(blp_path, os.path.join(OUTPUT_DIR, f"AOI_{aoi.get('number')}_BaseLayers.zip"))
                    time.sleep(WAIT_TIME)  # Pause to avoid rate limiting
                
                # Browse products associated with the AOI
                for product in aoi.get("products", []):
                    download_path = product.get("downloadPath")
                    product_type = product.get("type")
                    if download_path:
                        print(f"Download of {product_type} : {download_path}")
                        file_name = f"AOI_{aoi.get('number')}_{product_type}.zip"
                        download_file(download_path, os.path.join(OUTPUT_DIR, file_name))
                        time.sleep(WAIT_TIME)  # Pause to avoid rate limiting
        else:
            print(f"Error : {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"An error occured : {e}")

# Appeler la fonction pour récupérer et télécharger les données
fetch_and_download_activation_data(ACTIVATION_CODE)
