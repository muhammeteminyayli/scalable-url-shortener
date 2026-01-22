# Scalable URL Shortener Service

This project is a high-performance URL shortening service developed using modern Python technologies (FastAPI, SQLModel).
Unlike standard CRUD applications, this project simulates a distributed system architecture using a "Range Block Allocation" strategy. This approach allows for generating millions of unique short codes without database locks or race conditions, ensuring scalability and speed.

## Features

* **High Performance:** Built with FastAPI and Uvicorn for asynchronous request handling.
* **Persistent Storage:** Uses SQLite and SQLModel (ORM) to ensure data persistence.
* **Distributed Architecture Simulation:** Implements a central Range Manager and independent Workers to generate thread-safe IDs without constant database queries.
* **Base62 Encoding:** Converts numeric IDs into compact, URL-friendly alphanumeric codes.
* **API Documentation:** Includes interactive API testing via Swagger UI.

## Tech Stack

* Python 3.x
* FastAPI
* SQLModel (SQLAlchemy + Pydantic)
* Uvicorn
* SQLite
* Threading

## Project Structure

This project follows the Separation of Concerns principle:

```text
📦 URL-Shortener
 ┣ 📜 main.py           # API Endpoints and Routing (Presentation Layer)
 ┣ 📜 services.py       # Business Logic, RangeManager and Worker Classes (Logic Layer)
 ┣ 📜 database.py       # Database Connection and Models (Data Layer)
 ┣ 📜 requirements.txt  # Project Dependencies
 ┗ 📜 README.md         # Documentation
```

## Installation

Follow these steps to run the project locally.

### 1. Clone the Repository

```bash
git clone [https://github.com/muhammeteminyayli/scalable-url-shortener.git](https://github.com/muhammeteminyayli/scalable-url-shortener.git)
cd scalable-url-shortener
```

### 2. Create a Virtual Environment

It is recommended to use a virtual environment to isolate dependencies.

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
uvicorn main:app --reload
```

The database file (`database.db`) will be automatically created in the project directory upon startup.

## Usage

Once the server is running, you can access the interactive API documentation at: http://127.0.0.1:8000/docs

### Shorten a Link (POST)

Submit a long URL to generate a short code.

**Endpoint:** `/shorten`

**Request Body:**

```json
{
  "url": "[https://www.google.com/search?q=python](https://www.google.com/search?q=python)"
}
```

**Response:**

```json
{
  "original": "[https://www.google.com/search?q=python](https://www.google.com/search?q=python)",
  "short_link": "[http://127.0.0.1:8000/4c92](http://127.0.0.1:8000/4c92)"
}
```

### Redirect (GET)

Accessing the short link redirects the user to the original URL.

**Endpoint:** `/{short_code}`

**Example:** Visiting `http://127.0.0.1:8000/4c92` will redirect you to the Google search result.

## Architecture: Range Manager Logic

To avoid the performance bottleneck of database AUTO_INCREMENT fields in distributed systems, this project uses a memory-based allocation strategy:

* **RangeManager:** Acts as the central authority. It allocates blocks of IDs (e.g., 1000 IDs at a time) to workers. It uses a thread lock to prevent conflicts.
* **Worker (Node):** Requests a block of IDs from the RangeManager. It assigns IDs from its local memory until the block is exhausted, then requests a new block. This minimizes database writes and improves speed.
* **Persistence:** The mapping between the ID, the long URL, and the short code is saved to the database immediately to ensure no data is lost.
