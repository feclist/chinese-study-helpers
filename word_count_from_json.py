import re
import json
from collections import Counter
import jieba
from pypinyin import pinyin, Style
from cedict_utils.cedict import CedictParser
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_text(text):
    """
    Removes emojis, special characters, and keeps only Hanzi and basic text.
    """
    # Remove emojis and special characters
    clean_text = re.sub(r'[^一-鿿A-Za-z0-9\s]', '', text)
    return clean_text

def segment_text(texts):
    """
    Segments cleaned text using jieba and counts word occurrences.
    Filters out non-Chinese text and numbers after segmentation.
    """
    # List to store all words
    all_words = []
    
    logging.info("Starting text segmentation.")
    for i, text in enumerate(texts):
        logging.info(f"Processing text {i + 1}/{len(texts)}.")
        clean = clean_text(text)  # Clean the text
        segmented = jieba.lcut(clean)  # Segment using jieba
        all_words.extend([word for word in segmented if word.strip() and re.match(r'[\u4e00-\u9fff]', word)])  # Keep only Chinese characters

    logging.info("Text segmentation completed.")

    # Count word occurrences
    word_counts = Counter(all_words)
    return word_counts

def load_cedict_dictionary():
    """
    Loads the CEDICT dictionary using cedict_utils.
    """
    logging.info("Loading CEDICT dictionary.")
    parser = CedictParser()
    parser.read_file("cedict_ts.u8")  # Ensure this file is available in your working directory
    entries = parser.parse()
    dictionary = {entry.simplified: entry for entry in entries}
    logging.info("CEDICT dictionary loaded successfully.")
    return dictionary

def derive_translation_from_components(word, dictionary):
    """
    Derives a translation for a word based on its individual characters.
    """
    character_translations = []
    for char in word:
        char_entry = dictionary.get(char)
        if char_entry:
            character_translations.append(", ".join(char_entry.meanings))
        else:
            character_translations.append("?")  # Placeholder for unknown characters
    return " + ".join(character_translations)

async def fetch_missing_translations(missing_words):
    """
    Fetches translations for missing words using Google Translate in batches.
    """
    from googletrans import Translator

    translator = Translator()
    translations = {}
    batch_size = 100
    for i in range(0, len(missing_words), batch_size):
        batch = missing_words[i:i + batch_size]
        try:
            logging.info(f"Translating batch {i // batch_size + 1}/{-(-len(missing_words) // batch_size)}.")
            batch_translation = await translator.translate("\n".join(batch), src='zh-cn', dest='en')
            batch_results = batch_translation.text.split("\n")
            for word, translated in zip(batch, batch_results):
                translations[word] = translated
        except Exception as e:
            logging.error(f"Error translating batch {i // batch_size + 1}: {e}")
    return translations

async def add_translations_and_pinyin(word_counts, dictionary):
    """
    Enhances word counts with translations and pinyin using the CEDICT dictionary.
    Falls back to Google Translate for missing words.
    """
    enhanced_data = []
    missing_words = []
    total_words = len(word_counts)
    logging.info(f"Starting translations and pinyin generation for {total_words} words.")

    for word in word_counts:
        if word not in dictionary:
            missing_words.append(word)

    missing_translations = await fetch_missing_translations(missing_words) if missing_words else {}

    for word, count in word_counts.items():
        entry = dictionary.get(word)
        if entry:
            word_translation = ", ".join(entry.meanings)
            word_pinyin = entry.pinyin
        else:
            word_translation = missing_translations.get(word, derive_translation_from_components(word, dictionary))
            word_pinyin = " ".join([pinyin(char, style=Style.TONE3)[0][0] for char in word if re.match(r'[\u4e00-\u9fff]', char)])

        enhanced_data.append({
            "Word": word,
            "Count": count,
            "Translation": word_translation,
            "Pinyin": word_pinyin
        })

    logging.info("Translations and pinyin generation completed.")
    return sorted(enhanced_data, key=lambda x: x["Count"], reverse=True)

def save_enhanced_data(enhanced_data, word_counts, output_file):
    """
    Saves the enhanced data and metadata to a JSON file.
    """
    total_words = sum(word_counts.values())
    unique_words = len(word_counts)

    output = {
        "metadata": {
            "total_words": total_words,
            "unique_words": unique_words
        },
        "data": enhanced_data
    }

    logging.info(f"Saving enhanced data to {output_file}.")
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=4)
    logging.info("Data saved successfully.")

def print_statistics(word_counts):
    """
    Prints summary statistics about the processed text.
    """
    total_words = sum(word_counts.values())
    unique_words = len(word_counts)
    logging.info(f"Total words: {total_words}")
    logging.info(f"Unique words: {unique_words}")
    logging.info(f"Top 5 words: {word_counts.most_common(5)}")

async def main():
    # Load input data from JSON file
    input_file = "texts.json"
    logging.info(f"Loading input data from {input_file}.")
    with open(input_file, "r", encoding="utf-8") as file:
        texts = json.load(file)
    
    # Process texts and count words
    word_counts = segment_text(texts)

    # Print statistics
    print_statistics(word_counts)

    # Load CEDICT dictionary
    dictionary = load_cedict_dictionary()

    # Add translations and pinyin
    enhanced_data = await add_translations_and_pinyin(word_counts, dictionary)

    # Save results to a JSON file
    output_file = "enhanced_word_counts.json"
    save_enhanced_data(enhanced_data, word_counts, output_file)
    
    logging.info(f"Enhanced word count results saved to '{output_file}'.")

if __name__ == "__main__":
    asyncio.run(main())
