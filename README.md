# Back_End_Ecomerce_django_REST


# Django E-commerce Backend

This is a Django REST project for building the backend of an e-commerce platform.

## Project Structure

The project is organized into several Django apps:

1. **ecommerce**: The main project app.
2. **product**: Handles product management.
3. **category**: Manages product categories.
4. **order**: Manages orders and transactions.
5. **user_app**: Manages user authentication and authorization.
6. **user_profile**: Handles user profiles.
7. **wishlist**: Manages user wishlists.
8. **cart**: Handles shopping carts.

## Database

By default, this project uses SQLite3 as the database. However, it's configured to work with PostgreSQL as well, if needed.

## Getting Started

1. Clone this repository to your local machine.
2. Create a virtual environment (optional but recommended).
3. Install the required dependencies using `pip install -r requirements.txt`.
4. Configure your database settings in `settings.py` if you want to use PostgreSQL.
5. Apply migrations with `python manage.py migrate`.
6. Create a superuser with `python manage.py createsuperuser`.
7. Start the development server with `python manage.py runserver`.

## Usage

- Access the Django admin panel at `http://localhost:8000/admin/` to manage your e-commerce platform.
- Explore the API endpoints to interact with your backend.

## Contributing

Feel free to contribute to this project by opening issues or submitting pull requests. Contributions are welcome!

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

Special thanks to the Django community and the open-source contributors who make projects like this possible.

