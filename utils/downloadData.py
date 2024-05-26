import requests

PATHS = [
    'stats/requests/csv',
    'stats/failures/csv',
    'exceptions/csv',
]

def download(port):
    for path in PATHS:
        response = requests.get(f"http://localhost:{port}/{path}")
        with open(f'{path.replace("/", "_")}.csv', 'wb') as file:
            file.write(response.content)
    
    response = requests.get(f"http://localhost:{port}/stats/report?theme=light&download=1")
    with open(f'report.html', 'wb') as file:
        file.write(response.content)

if __name__ == '__main__':
    port = input('Enter the port number: ')
    download(port)
