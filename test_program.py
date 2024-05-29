import requests

# Test login (adjust email and password to match a test user in your database)
login_response = requests.post('http://127.0.0.1:5000/login', data={
    'email': 'test@example.com',
    'password': 'password'
})
print('Login Response:', login_response.text)

# Test adding an entry
add_entry_response = requests.post('http://127.0.0.1:5000/skincare-form', data={
    'cleanser': 'Cleanser Video Test',
    'toner': 'Toner Video Test',
    'moisturizer': 'Moisturizer Video Test',
    'serum': 'Serum Video Test',
    'sunscreen': 'Sunscreen Video Test'
})
print('Add Entry Response:', add_entry_response.text)

# Test sorting entries
sort_response = requests.post('http://127.0.0.1:5000/sort-entries', json={
    'sort_key': 'moisturizer',
    'sort_order': 'desc'
})
print('Sort Response:', sort_response.json())
