# XHS Text Extract

This project is designed to extract text content from posts on the Xiaohongshu (XHS) platform and perform text analysis, including word segmentation, translation, and pinyin generation.

## Features

- **Text Extraction**: Extracts text content from XHS posts using a web scraping script.
- **Text Processing**: Cleans and segments the extracted text using `jieba`.
- **Translation and Pinyin**: Enhances word counts with translations and pinyin using the CEDICT dictionary and Google Translate for missing words.
- **Statistics**: Provides summary statistics about the processed text.

## Requirements

- Python 3.13
- Node.js
- `jieba`, `pypinyin`, `cedict_utils`, `googletrans` Python packages

## Setup

1. **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd xhs-text-extract
    ```

2. **Set up the Python virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `.\venv\Scripts\activate`
    ```

3. **Install the required Python packages**:
    ```bash
    pip install jieba pypinyin cedict_utils googletrans
    ```

## Usage

### Extracting Text from XHS

1. **Run the web scraping script**:
    - Open the XHS website in your browser.
    - Open the browser's developer console (usually F12 or right-click and select "Inspect").
    - Copy and paste the contents of `scrape-xhs.js` into the console and press Enter.
    - The script will extract text from all posts and log the results to the console.

2. **Save the extracted texts**:
    - Copy the logged JSON array of texts and save it to a file named `texts.json` in the project directory.

### Processing Text

1. **Run the text processing script**:
    ```bash
    python word_count_from_json.py
    ```

2. **Output**:
    - The script will generate an `enhanced_word_counts.json` file containing word counts, translations, and pinyin.

## Script Details

### `scrape-xhs.js`

This script extracts text content from XHS posts by:
- Waiting for specific elements to appear and contain text.
- Clicking on post links to open popups and extract text.
- Closing popups and repeating the process for all posts.
- Logging the extracted texts to the console.

### `word_count_from_json.py`

This script processes the extracted texts by:
- Cleaning and segmenting the text using `jieba`.
- Counting word occurrences and filtering out non-Chinese text.
- Loading the CEDICT dictionary for translations and pinyin.
- Fetching missing translations using Google Translate.
- Enhancing word counts with translations and pinyin.
- Saving the results to `enhanced_word_counts.json`.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
