# Domain Finder
A utility to find unregistered domains.

## Setup
1. Clone the repo
```bash
git clone https://github.com/Gr3atWh173/domain_finder.git
cd domain_finder
```

2. Install it
```bash
poetry install
```

3. Setup your Postgres database.
4. Create an `.env` file with the following keys:
```env
DJANGO_SECRET_KEY = django-secret-key
DJANGO_DEBUG = True || False
DATABASE_HOST = address-where-database-hosted
DATABASE_PORT = port-where-database-hosted
DATABASE_NAME = name-of-the-database
DATABASE_USER = user-which-accesses-database
DATABASE_PASSWORD = password-of-above-user
DATABASE_NAME_TEST = database-for-testing
```

5. Run it
```bash
poetry run python manage.py runserver
```


## Endpoints

### Domain Finding
1. `GET /api/v1/registrationStatus`
    - Required parameters:
        - `domain` containing the domain name to check
    - Optional headers:
        - `Authorization` with the format `JWT ACCESS_TOKEN`

    Sample response:
    ```json
    {
        "name": "google",
        "tld": "com",
        "registered": true
    }
    ```

2. `GET /api/v1/similarDomains`
    - Required parameters:
        - `domain` containing the domain name to find similars to

    Sample response:
    ```json
    {
        "domain": {
            "name": "randeepsingh",
            "tld": "com",
            "registered": true  | false,
        },
        "similar": [
            {
                "name": "randeepsingh",
                "tld": "jp",
                "registered": true | false,
            },
            (...)
        ]
    }
    ```

### User Authentication
The app uses JWT based auth with access and refresh tokens having lifetimes of 5 and 360 minutes respectively.
Auth endpoints are provided by `Djoser`.

1. CREATE USER
    ```
    POST /api/v1/auth/users

    {
        "email": "someuser@gmail.com",
        "password": "passwordpassword",
        "username": "someuser"
    }
    ```

2. LOGIN USER
    ```
    POST /api/v1/auth/jwt/create

    {
        "password": "passwordpassword",
        "username": "someuser"
    }
    ```

    Sample response:
    ```json
    {
        "refresh": "...",
        "access": "..."
    }
    ```

3. GET USER
    ```
    GET /api/v1/auth/users/me
    ```
    - Required headers:
        - `Authorization` with the format `JWT ACCESS_TOKEN`

    Sample response:
    ```json
    {
        "email": "someuser@gmail.com",
        "history": [
            "google"
        ],
        "id": 1,
        "username": "someuser"
    }
    ```
