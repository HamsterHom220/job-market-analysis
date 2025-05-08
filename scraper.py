import requests
import pandas as pd
import time

vacancies = []
page = 0
per_page = 100
max_pages = 30  # Lower page count to avoid rate limits while testing

while page < max_pages:
    response = requests.get(
        'https://api.hh.ru/vacancies',
        params={
            'text': 'PROFESSION_NAME', # PASTE YOUR QUERY
            'page': page,
            'per_page': per_page
        }
    )

    if response.status_code != 200:
        print(f"Error {response.status_code} on page {page}")
        break

    data = response.json()

    for item in data['items']:
        vacancy_id = item.get('id')
        
        # GET detailed vacancy info
        detail_resp = requests.get(f'https://api.hh.ru/vacancies/{vacancy_id}')
        
        if detail_resp.status_code != 200:
            print(f"Error {detail_resp.status_code} on vacancy {vacancy_id}")
            continue
        
        detail = detail_resp.json()
        
        vacancy = {
            'id': vacancy_id,
            'name': item.get('name'),
            'area': item['area']['name'] if item.get('area') else None,
            'salary_from': item['salary']['from'] if item.get('salary') else None,
            'salary_to': item['salary']['to'] if item.get('salary') else None,
            'currency': item['salary']['currency'] if item.get('salary') else None,
            'snippet_requirement': item['snippet']['requirement'] if item.get('snippet') else None,
            'snippet_responsibility': item['snippet']['responsibility'] if item.get('snippet') else None,
            'experience': detail['experience']['name'] if detail.get('experience') else None,
            'employment': detail['employment']['name'] if detail.get('employment') else None,
            'schedule': detail['schedule']['name'] if detail.get('schedule') else None,
            'key_skills': [skill['name'] for skill in detail.get('key_skills', [])]
        }
        vacancies.append(vacancy)
    
    print(f"Fetched page {page+1}/{max_pages}")
    page += 1
    time.sleep(2)

# Convert to DataFrame
df = pd.DataFrame(vacancies)

# Join key skills list into string
df['key_skills'] = df['key_skills'].apply(lambda skills: ', '.join(skills) if skills else None)

# Save to CSV
df.to_csv('vacancies.csv', index=False)
print(f"Saved {len(df)} vacancies to vacancies.csv")
