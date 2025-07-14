# My Stock Portfolio Analyzer

This is a simple web-based stock portfolio analyzer built with Python and Flask. It allows you to upload a `portfolio.json` file, view your current holdings, analyze realized and unrealized profit/loss, and manage your transaction history.

This guide provides all the necessary steps for setting up the project locally and deploying it to the web using Render.

---


## Table of Contents
1.  Prerequisites
2.  Local Setup
3.  Data Management
    -   Importing from Spreadsheet
    -   Fixing Date Formats
4.  Deployment to Render
5.  Updating the Application

---

## 1. Prerequisites

Before you begin, ensure you have the following installed on your Mac:
-   Python 3
-   pip (Python's package installer)
-   Git

You will also need accounts for the following services:
-   GitHub
-   Render

---

## 2. Local Setup

These steps are for running the application on your own computer for development or testing.

1.  **Open Terminal** and navigate to your project directory:
    ```bash
    cd /Users/chanaimac/MyStockPythonApp
    ```

2.  **(Optional but Recommended)** Create and activate a virtual environment to keep project dependencies isolated:
    ```bash
    # Create the environment
    python3 -m venv venv
    # Activate it
    source venv/bin/activate
    ```

3.  **Install required packages**:
    Render will use this file to install dependencies. We need `Flask` to run the web app and `gunicorn` as the web server for Render.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the development server**:
    ```bash
    python webapp.py
    ```

5.  Open your web browser and go to `http://127.0.0.1:5000` or `http://localhost:5000`. You should see the application running.

---

## 3. Data Management

### Importing from Spreadsheet

You can import transaction data from a spreadsheet (like Apple Numbers) into your `portfolio.json` file.

1.  **Prepare your spreadsheet**: Ensure it has the correct columns: `Date`, `Symbol`, `Type`, `Lot Number`, `Volume`, `Price per Share`, `Commission`, `Tax Rate (%)`, `Remark`.
2.  **Export to CSV**: Export the sheet as a CSV file and name it `new_transactions.csv`. Place it in the project folder.
3.  **Run the converter script**: This script will safely append the new data from the CSV to your main `portfolio.json`, checking for duplicate lot numbers.
    ```bash
    python converter.py
    ```

### Fixing Date Formats

If your `portfolio.json` has inconsistent date formats, you can use the `fix_dates.py` script to standardize them all to `YYYY-MM-DD`.

1.  The script automatically creates a backup (`portfolio.backup.json`).
2.  Run the script from your terminal:
    ```bash
    python fix_dates.py
    ```

---

## 4. Deployment to Render

Follow these steps to deploy your application to a live URL on the internet.

1.  **Push your code to GitHub**:
    ```bash
    # Add all changed files to the staging area
    git add .

    # Commit the changes with a descriptive message
    git commit -m "Prepare for deployment to Render"

    # Push the changes to your GitHub repository
    git push
    ```

2.  **Configure on Render.com**:
    -   Log in to your Render account.
    -   From the Dashboard, click **New +** > **Web Service**.
    -   Choose **Build and deploy from a Git repository** and connect your GitHub account.
    -   Select your `MyStockPythonApp` repository.
    -   Fill in the service details:
        -   **Name**: Give your app a unique name (e.g., `my-stock-analyzer-chanai`).
        -   **Region**: Choose a region close to you (e.g., Singapore).
        -   **Branch**: `main` (or your default branch).
        -   **Runtime**: `Python 3`.
        -   **Build Command**: `pip install -r requirements.txt` (Render usually detects this automatically).
        -   **Start Command**: `gunicorn webapp:app`
            -   `webapp` refers to your Python file `webapp.py`.
            -   `app` refers to the Flask object `app = Flask(__name__)` inside that file.
    -   Click **Create Web Service**.

3.  **Wait for Deployment**: Render will now pull your code from GitHub, install the packages from `requirements.txt`, and start your application using the `gunicorn` command. Once it's done, you will get a public URL (like `https://my-stock-analyzer-chanai.onrender.com`) that you can access from anywhere.

---

## 5. Updating the Application

Whenever you make changes to your application and want to update the live version, you just need to repeat step 1: **Push your code to GitHub**.

```bash
git add .
git commit -m "Add new feature or fix bug"
git push
```

Render will automatically detect the new push and redeploy your application with the latest changes.