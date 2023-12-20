# Django Purchase Order API

This repository contains a Django-based CRUD API for managing purchase orders.

## Prerequisites

- Python 3.x
- Pip (Python package manager)

## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/brokoder/shop-api.git
    cd shop-api
    ```

2. Create and activate a virtual environment:

    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Go to App Repo:

    ```bash
    cd MainApp
    ```

5. Apply migrations:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

## Running the Server

To start the development server, run the following command:

    ```bash
    python manage.py runserver
    ```

By default, the server will run at http://127.0.0.1:8000/

## Running Tests
To run tests, use the following command
    ```bash
    python manage.py test
    ```
## API Endpoints

`GET /purchase/orders/`: Retrieve all purchase orders.
`GET /purchase/orders/<int:id>/`: Retrieve a specific purchase order.
`POST /purchase/orders/`: Create a new purchase order.
`PUT /purchase/orders/<int:id>/`: Update a purchase order.
`DELETE /purchase/orders/<int:id>/`: Delete a purchase order.
Replace <int:id> with the specific ID of the purchase order.

