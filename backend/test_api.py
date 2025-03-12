import requests

url = 'http://127.0.0.1:5000/api/predict'
file_path = 'eapol-mka.pcap'  # Make sure this path is correct

# Open the pcap file
with open(file_path, 'rb') as file:
    files = {'file': file}
    
    # Send the POST request
    response = requests.post(url, files=files)

# Print the raw response text to help debug
print("Response Status Code:", response.status_code)
print("Response Text:", response.text)  # This will show you the raw response content

# Attempt to print the JSON response
try:
    print(response.json())
except Exception as e:
    print(f"Error decoding JSON: {e}")
