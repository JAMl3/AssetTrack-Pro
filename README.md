# AssetTrack-Pro
Flask-based web app for asset and user management. Import data, assign assets, view by category, edit details, and execute SQL queries. User-friendly interface and SQLite backend.

This web application is built using Flask, a Python web framework, and SQLite as the database backend. It provides functionality for managing assets and users. Users can import assets and users from CSV files, assign assets to users, view assets by category, edit asset details, and perform SQL queries through a web interface.

## Features

- **Import Assets:** Users can import assets from a CSV file. The application validates the file format and allows users to import asset data into the database.

- **Import Users:** Users can import user data from a CSV file. The application validates the file format and allows users to import user information into the database.

- **Assign Assets:** Users can assign assets to specific users. The application provides an interface for assigning assets to users, establishing a many-to-many relationship between assets and users.

- **View Assets:** Users can view assets filtered by category. The application displays assets based on their categories, allowing users to easily navigate through different types of assets.

- **Edit Assets:** Users can edit asset details, including name, category, unique ID, and purchase order number. The application provides a form for users to update asset information.

- **SQL Console:** The application includes an SQL console that allows users to execute custom SQL queries. Users can perform various database operations using SQL commands through the web interface.

## Getting Started

1. **Clone the Repository:**
   ```
   git clone https://github.com/JAMl3/AssetTrack-Pro
   cd AssetTrack-Pro
   ```

2. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Run the Application:**
   ```
   python app.py
   ```

   The application will be accessible at `http://localhost:5000`.

## Screenshots

Welcome.html

![image](https://github.com/JAMl3/AssetTrack-Pro/assets/97791913/5e2b56e7-36ac-4945-a140-c40bc83f185d)

view_assets.html

![image](https://github.com/JAMl3/AssetTrack-Pro/assets/97791913/c341b638-7973-4124-be75-d497e016ba95)

assign_assets.html

![image](https://github.com/JAMl3/AssetTrack-Pro/assets/97791913/ccd1c7c6-d61e-4906-80b5-d65a0953f9f9)

assigned_assets.html

![image](https://github.com/JAMl3/AssetTrack-Pro/assets/97791913/27ea1d36-fa22-4b8f-b759-eacfaeeb04a9)

users.html

![image](https://github.com/JAMl3/AssetTrack-Pro/assets/97791913/e2e31559-b76c-4b59-92de-2f6fc09b9ba9)

add_asset.html

![image](https://github.com/JAMl3/AssetTrack-Pro/assets/97791913/c847d8fb-70b8-450c-adae-4bf4233bf1cc)

add_users.html

![image](https://github.com/JAMl3/AssetTrack-Pro/assets/97791913/1887a611-9726-4f84-a02a-f859e274b6dd)

sql_console.html

![image](https://github.com/JAMl3/AssetTrack-Pro/assets/97791913/f0eae4c8-9f04-47dc-ba09-526fe2246a9f)



## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
