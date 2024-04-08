import requests
from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector

url = "https://www.speedtest.net/global-index"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
mobile_data = []
mobile_header = []
for row in soup.find_all('tr', {'class': 'rankings-row odd'}):
    columns = row.find_all('td')
    if not mobile_header:
        mobile_header = [column.text for column in columns]
    else:
        mobile_data.append([column.text for column in columns])

# Extract fixed data
fixed_data = []
fixed_header = []
for row in soup.find_all('tr', {'class': 'rankings-row even'}):
    columns = row.find_all('td')
    if not fixed_header:
        fixed_header = [column.text for column in columns]
    else:
        fixed_data.append([column.text for column in columns])

# Convert the extracted data to pandas dataframes
mobile_df = pd.DataFrame(mobile_data, columns=mobile_header)
fixed_df = pd.DataFrame(fixed_data, columns=fixed_header)

# Display the data
print("Mobile data:")
print(mobile_df)
print("\nFixed data:")
print(fixed_df)
# Save the data to CSV files
mobile_df.to_csv('mobile.csv', index=False)
fixed_df.to_csv('fixed.csv', index=False)

# Connect to MySQL database
config = {
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'database': 'your_database',
    'port': 3306
}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# Create mobile table
cursor.execute("""
CREATE TABLE mobile (
  country VARCHAR(255),
  download_speed DECIMAL(10,2),
  upload_speed DECIMAL(10,2),
  latency DECIMAL(10,2),
  rank INT,
  change DECIMAL(4,2)
)
""")

# Insert mobile data into the table
for index, row in mobile_df.iterrows():
    cursor.execute("""
    INSERT INTO mobile (country, download_speed, upload_speed, latency, rank, change)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, tuple(row))

# Create fixed table
cursor.execute("""
CREATE TABLE fixed (
  country VARCHAR(255),
  download_speed DECIMAL(10,2),
  upload_speed DECIMAL(10,2),
  latency DECIMAL(10,2),
  rank INT,
  change DECIMAL(4,2)
)
""")
# Insert fixed data into the table
for index, row in fixed_df.iterrows():
    cursor.execute("""
    INSERT INTO fixed (country, download_speed, upload_speed, latency, rank, change)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, tuple(row))

# Commit the changes
cnx.commit()

# Close the cursor and connection
cursor.close()
cnx.close()
