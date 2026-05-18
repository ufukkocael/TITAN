import urllib.request
import urllib.error
import json

base = 'http://localhost:9100'

def get(path):
    try:
        with urllib.request.urlopen(base+path, timeout=5) as r:
            print(r.read().decode('utf-8'))
    except Exception as e:
        print('ERROR', e)

print('--- health ---')
get('/health')
print('\n--- vaccines ---')
get('/api/v1/vaccines')
print('\n--- post blueprint ---')
req = urllib.request.Request(base + '/api/v1/blueprint', data=json.dumps({
    'blueprint_id': 'bp_test_1',
    'symptom_signature': 'mock_test',
    'anonymized_vector': [0,0,0],
    'solution': 'noop',
    'platform': 'local'
}).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=5) as r:
        print(r.read().decode('utf-8'))
except Exception as e:
    print('ERROR', e)
print('\n--- done ---')
