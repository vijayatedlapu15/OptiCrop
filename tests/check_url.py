import urllib.request

urls = [
    "https://raw.githubusercontent.com/Sadhana-Panthi/agricultural-crop-recommendation/main/Crop_recommendation.csv",
    "https://raw.githubusercontent.com/ravikant-diwakar/Crop-Recommendation/main/Crop_recommendation.csv",
    "https://raw.githubusercontent.com/arbaaz-01/Crop-Recommendation-Model/main/Crop_recommendation.csv",
    "https://raw.githubusercontent.com/aakashr02/Crop-Recommendation/master/Crop_recommendation.csv",
    "https://raw.githubusercontent.com/animesh-agarwal/Machine-Learning/master/Crop_Recommendation/Crop_recommendation.csv"
]

for url in urls:
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req) as response:
            print(f"URL: {url} -> Status: {response.status}")
            if response.status == 200:
                print("FOUND WORKING URL!")
    except Exception as e:
        print(f"URL: {url} -> Error: {e}")
