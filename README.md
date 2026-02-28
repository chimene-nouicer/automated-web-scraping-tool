# AI Beauty Assistant — Automated Web Scraping Tool

## Project Overview

AI Beauty Assistant is a fully automated web scraping tool that collects and processes product data from Lookfantastic (French website version).

The tool automatically generates:
- A personalized skincare routine
- A personalized haircare routine

Recommendations are based on:
- Skin or hair type
- Main concern
- Maximum budget per product
- Semantic analysis of product descriptions

This project combines:
- Automated web scraping (Selenium)
- Data processing
- A scoring system inspired by AI logic
- An interactive user interface (Streamlit)

## Purpose of the Project

The beauty market is saturated with thousands of products. For beginners, it is difficult to:
- Choose the right cleanser for oily skin
- Select an appropriate anti-aging serum
- Find a suitable shampoo for dry or oily hair

This tool addresses that problem by:
- Automatically scraping public product categories
- Analyzing product descriptions
- Scoring products based on user profiles
- Generating a complete routine in seconds


## Core Features

### 1. Fully Automated Web Scraping

Automatic navigation through product categories

Extraction of product names ; prices ; descriptions ; URLs

Automatic cookie handling

Randomized delays to simulate human behavior

Optional headless mode


### 2. Intelligent Scoring System

Each product is evaluated based on:
- Relevance to the main concern (acne, dry skin, anti-aging…)
- Compatibility with skin or hair type
- Budget compliance
- Presence of key ingredients detected using regular expressions

Examples:

Retinol → prioritized for anti-aging

Salicylic acid → prioritized for acne-prone skin

Shea butter → prioritized for dry or curly/coily hair


### 3. Dual Module System
Skincare Module

Generated routine includes: cleanser, serum, moisturizer, SPF

Haircare Module

Generated routine includes: shampoo, conditioner, hair mask, serum / Oil


### 4. Streamlit Interface

The application provides a simple and interactive interface:
- User profile selection
- Progress bar during scraping
- Structured product display
- Direct link to each product page

## Project Architecture

automated-web-scraping-tool/

│

├── .gitignore

├── LICENSE

├── README.md

├── app (1).py

├── scraper (1).py

├── requirements.txt

│


## 🔹 scraper.py

Contains:

- BaseScraper class
- LookfantasticScraper class
- Product dataclass
- Scoring functions
- Routine generation logic

## 🔹 app.py
Contains the Streamlit user interface.

The architecture follows an object-oriented design to ensure modularity, readability, and reusability.

## Installation

### 1️⃣ Clone the repository

git clone https://github.com/your-username/ai-beauty-assistant.git

cd ai-beauty-assistant

### 2️⃣ Create a virtual environment (recommended)

python -m venv venv

source venv/bin/activate      # Mac/Linux

venv\Scripts\activate         # Windows

### 3️⃣ Install dependencies

pip install -r requirements.txt

Usage

Run the application:
python -m streamlit run app.py

Your browser will open automatically.

Steps:
- Select your profile
- Click “Generate my routine”
- Wait for automatic scraping and analysis
- View your personalized routine


To stop the application:
- Close the terminal.
-Dependencies
- Included in requirements.txt:
-selenium
- webdriver-manager
- streamlit
- dataclasses (if Python < 3.7)


## Web Scraping Strategy

The target website uses dynamic JavaScript content.

Selenium allows:
- Full page rendering
- Explicit waits (WebDriverWait)
- Cookie handling
- Reliable element detection


## Ethics & Legal Considerations

This project follows responsible scraping practices:
- Only public product category pages are accessed
- robots.txt is respected
- Random delays are implemented
- No large-scale or aggressive scraping
- No security bypassing
- No credentials are stored or committed
- Transparent data usage explained in this README


This project was developed strictly for educational purposes.

When official APIs are available, they should always be preferred.

## Technical Challenges & Solutions

Challenge
- Dynamic content loading
- Risk of blocking
- Missing product data
- Long scraping time
- No relevant product found


Solution
- WebDriverWait
- Realistic User-Agent + delays
- Try/Except handling
- Streamlit session caching
- Default fallback product

### Strengths

Modular and object-oriented architecture

Clean separation between scraping logic and UI

Customizable scoring system

Easily extendable to other e-commerce websites

Reusable scraper structure


### Limitations

Scraping time may vary

Keyword-based analysis (not scientific)

Depends on website HTML structure

No advanced ingredient analysis


## Future Improvements

- Parallel scraping (multithreading)
- Local database caching (SQLite / JSON)
- Additional product categories (body care, makeup…)
- REST API implementation (Flask / FastAPI)
- Ingredient-based scoring model
- User review analysis
- Cloud deployment (Streamlit Cloud / Render)


## Disclaimer

This tool:
- Does not replace medical or dermatological advice
- Does not provide professional diagnosis
- Provides automated suggestions based on publicly available product descriptions
- All scraped data remains the property of the original website.

*** Chimène NOUICER (DS2E) Venera SINANAJ (DS2E) ***
