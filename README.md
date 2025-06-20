# 🕷️ Web Scraping Pipeline Project

## 🛠️ Project Setup

### 🐍 Create Python Runtime Environment

```bash
python -m venv .venv
````

### ⚡ Activate Python Runtime Environment

```bash
    source .venv/bin/activate
```

### 📦 Install Python Packages

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install required libraries
pip install -r requirements.txt
```

### 🎭 Install Playwright in CLI Environment

```bash
playwright install firefox
```

---

## 🚀 Project Run Instructions

This project follows a modular scraping pipeline managed via a single entry point script: `run_script.py`.

Each run is configured via the `configs.yml` file with the following fields:

| Field       | Description                                                       |
| ----------- | ----------------------------------------------------------------- |
| `run_group` | Logical group name for related scraping jobs                      |
| `run_name`  | Specific scraping job within the group                            |
| `run_type`  | Determines which script to execute (`extract`, `detail`, or `clean`) |

---

### 🧭 Script Responsibilities

| `run_type` | Script              | Description                                                                                       |
| ---------- | ------------------- | ------------------------------------------------------------------------------------------------- |
| `extract`     | `scraper_extractor.py`   | Scrapes data from the marketplace website and stores it in a JSON file                            |
| `detail`   | `scraper_detail.py` | Loads the JSON output from the `extract` run, scrapes detailed data, and saves it to a new JSON file |
| `clean`    | `scraper_clean.py`  | Cleans the data collected by `detail` and exports it as a timestamped CSV file                    |

---

### 🔁 Pipeline Workflow & Dependencies

Scripts must be executed in the following order due to data dependencies:

```text
Step 1: scraper_main.py   → Collects initial high-level data  
Step 2: scraper_detail.py → Uses output from Step 1 to add detailed data  
Step 3: scraper_clean.py  → Uses output from Step 2 to clean and save results  
```

---

### ▶️ How to Run a Script

To run the pipeline, use the following command and change the `--run_mode` as needed (`main`, `detail`, or `clean`):

- `--max`: Specifies the maximum number of pages to scrape from the website. (Only applies when `run_mode` is `extract`)

```bash
python run_script.py --run_group "electronics" --run_name "camera-photo" --run_mode "extract" --max 1
```