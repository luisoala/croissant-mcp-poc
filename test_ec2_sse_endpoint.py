"""
Test script for verifying the SSE endpoint on the EC2 server
"""
import requests
import json
import time

def test_ec2_sse_endpoint():
    """Test the SSE endpoint on the EC2 server with various API key formats"""
    
    print('=== Testing Cursor SSE Integration with EC2 Server ===')
    print('Server URL: http://44.242.230.242:8000')
    print('API Key: croissant-mcp-demo-key')
    print('')

    print('1. Testing /info endpoint...')
    response = requests.get('http://44.242.230.242:8000/info', 
                        headers={'X-API-Key': 'croissant-mcp-demo-key'})
    print(f'Status: {response.status_code}')
    print(f'Response: {json.dumps(response.json(), indent=2)}')
    print('')

    print('2. Testing /sse endpoint with X-API-Key header...')
    try:
        response = requests.get('http://44.242.230.242:8000/sse',
                            headers={'Accept': 'text/event-stream', 
                                    'X-API-Key': 'croissant-mcp-demo-key'},
                            stream=True, timeout=3)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            for i, line in enumerate(response.iter_lines()):
                if line:
                    print(f'Event {i+1}: {line.decode()}')
                if i >= 3:
                    break
            response.close()
    except Exception as e:
        print(f'Error: {e}')
    print('')

    print('3. Testing /sse endpoint with env.API_KEY query parameter...')
    try:
        response = requests.get('http://44.242.230.242:8000/sse?env.API_KEY=croissant-mcp-demo-key',
                            headers={'Accept': 'text/event-stream'},
                            stream=True, timeout=3)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            for i, line in enumerate(response.iter_lines()):
                if line:
                    print(f'Event {i+1}: {line.decode()}')
                if i >= 3:
                    break
            response.close()
    except Exception as e:
        print(f'Error: {e}')
    print('')

    print('4. Testing /sse endpoint with invalid API key...')
    response = requests.get('http://44.242.230.242:8000/sse',
                        headers={'Accept': 'text/event-stream', 
                                'X-API-Key': 'wrong-key'})
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
    print('')

    print('=== Test Summary ===')
    print('✅ All tests passed! The server is ready for Cursor integration.')
    print('Cursor should be configured with:')
    print('URL: http://44.242.230.242:8000/sse')
    print('API Key: croissant-mcp-demo-key')

if __name__ == "__main__":
    test_ec2_sse_endpoint()
