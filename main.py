#!/usr/bin/env python3

from openai import OpenAI
import mysql.connector
import json
import sys
import re
from config import OPENAI_API_KEY, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, DEBUG_INFO

# Set OpenAI API Key
client = OpenAI(
  api_key=OPENAI_API_KEY,  # this is also the default, it can be omitted
)

# Function to call OpenAI API
def get_word_data(word):
    prompt = f"""
    假设你是一个精通各种语言的语言大师，尤其精通英语的各种掌故与用法,我现在需要相关信息针对英语单词进行学习与记忆。你的任务是根据输入单词，按照后续JSON格式输出如下相关信息（至少包含中文含义、词根、词源、派生词、Oxford English Dictionary释意、Merriam-Webster释意、同义词、反义词、记忆技巧以及常用场景用法示例等）。为避免混乱词意一定要准确，切记切记。举例如下：
    若输入单词是'pity',则返回下列JSON格式信息：
    ```json
    {{
        "word": "pity",
        "chinese_meaning": "怜悯，同情",
        "root": "pietas",
        "etymology": "拉丁语，意为“敬意、虔诚”，演变为“怜悯、同情”",
        "part_of_speech": "noun, verb",
        "british_ipa": "/ˈpɪti/",
        "american_ipa": "/ˈpɪti/",
        "derived_words": {{
            "piteous": "可怜的",
            "pitiful": "可怜的，令人怜悯的"
        }},
        "oed_definition": "The feeling of sorrow and compassion caused by the suffering and misfortunes of others.",
        "mw_definition": "Sympathetic sorrow for one suffering, distressed, or unhappy.",
        "synonyms": [
            "compassion",
            "sympathy",
            "mercy"
        ],
        "antonyms": [
            "indifference",
            "cruelty",
            "harshness"
        ],
        "memory_tips": "将“pity”与“pet”（宠物）联系起来，想象对一只可怜的小宠物感到同情。",
        "usage_examples": [
            {{
                "sentence": "I feel pity for the homeless.",
                "translation": "我为无家可归的人感到同情。"
            }},
            {{
                "sentence": "Do you pity him?",
                "translation": "你同情他吗？"
            }},
            {{
                "sentence": "I don’t pity him; he brought this on himself.",
                "translation": "我不怜悯他，这是他自找的。"
            }},
            {{
                "sentence": "It’s a pity you can’t come to the party.",
                "translation": "你不能来参加派对，真是太遗憾了。"
            }},
            {{
                "sentence": "The tragic event evoked widespread pity and compassion from the community.",
                "translation": "那场悲剧事件引起了社区广泛的怜悯和同情。"
            }},
            {{
                "sentence": "Her eyes filled with pity as she watched the child cry.",
                "translation": "当她看到那个孩子哭泣时，她的眼中充满了怜悯。"
            }}
        ]
    }}
    ```

    以上输出为完整的JSON格式。请按照上述输入要求与输出JSON格式返回当前输入单词的信息，输入单词是：{word}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a language expert, especially proficient in English. Now I need information on how to learn and memorize English words."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2048
    )
    if response is None or response.choices is None or len(response.choices) <= 0:
        return None

    # return json.loads(response_message)
    # Sanity check to ensure the response is as expected
    try:
        response_message = response.choices[0].message.content
        response_message = re.sub(r"^```json|```$", "", response_message).strip()
        if DEBUG_INFO:
            print(response_message)

        word_data = json.loads(response_message)

        required_keys = [
            'word', 'chinese_meaning', 'root', 'etymology', 'derived_words',
            'oed_definition', 'mw_definition', 'synonyms', 'antonyms',
            'part_of_speech', 'british_ipa', 'american_ipa', 'memory_tips', 'usage_examples'
        ]

        for key in required_keys:
            if key not in word_data:
                raise ValueError(f"Missing key in response: {key}")

        return word_data
    except (KeyError, IndexError, json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Invalid response format: {e}")
    return None

# Function to establish MySQL connection
def get_mysql_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

# Function to flatten dictionary to string
def flatten_dict(d):
    return "; ".join([f"{k}: {v}" for k, v in d.items()])

def flatten_list(d):
    return "; ".join(d)

# Function to remove quotes from strings
def remove_quotes(s):
    return s.replace("'", "").replace('"', '')

# Function to insert data into MySQL database
def insert_word_data(word, word_data, connection):
    cursor = connection.cursor()

    # Check if oed_definition and mw_definition are dict or list, then flatten them
    if isinstance(word_data['oed_definition'], dict):
        word_data['oed_definition'] = flatten_dict(word_data['oed_definition'])
    elif isinstance(word_data['oed_definition'], list):
        word_data['oed_definition'] = flatten_list(word_data['oed_definition'])

    if isinstance(word_data['mw_definition'], dict):
        word_data['mw_definition'] = flatten_dict(word_data['mw_definition'])
    elif isinstance(word_data['mw_definition'], list):
        word_data['mw_definition'] = flatten_list(word_data['mw_definition'])

    # Remove quotes from all string values in word_data
    for key, value in word_data.items():
        if isinstance(value, str):
            word_data[key] = remove_quotes(value)

    # compress part_of_speech
    word_data['part_of_speech'] = word_data['part_of_speech'].replace('noun', 'n.').replace('adjective', 'adj.').replace('adverb', 'adv.').replace('verb', 'v.').replace('conjunction', 'conj.').replace('preposition', 'prep.').replace('pronoun', 'pron.')

    # Insert into words table
    derived_words = word_data.get('derived_words', {})
    derived_words_count = len(derived_words)
    derived_word_keys = list(derived_words.keys())

    word_values = (
        word_data['word'],
        word_data['chinese_meaning'],
        word_data['root'],
        word_data['etymology'],
        word_data['part_of_speech'],
        word_data['british_ipa'],
        word_data['american_ipa'],

        derived_word_keys[0] if len(derived_word_keys) > 0 else None, derived_words.get(derived_word_keys[0], None) if len(derived_word_keys) > 0 else None,
        derived_word_keys[1] if len(derived_word_keys) > 1 else None, derived_words.get(derived_word_keys[1], None) if len(derived_word_keys) > 1 else None,
        derived_word_keys[2] if len(derived_word_keys) > 2 else None, derived_words.get(derived_word_keys[2], None) if len(derived_word_keys) > 2 else None,
        derived_word_keys[3] if len(derived_word_keys) > 3 else None, derived_words.get(derived_word_keys[3], None) if len(derived_word_keys) > 3 else None,
        derived_word_keys[4] if len(derived_word_keys) > 4 else None, derived_words.get(derived_word_keys[4], None) if len(derived_word_keys) > 4 else None,
        derived_word_keys[5] if len(derived_word_keys) > 5 else None, derived_words.get(derived_word_keys[5], None) if len(derived_word_keys) > 5 else None,
        derived_word_keys[6] if len(derived_word_keys) > 6 else None, derived_words.get(derived_word_keys[6], None) if len(derived_word_keys) > 6 else None,
        derived_word_keys[7] if len(derived_word_keys) > 7 else None, derived_words.get(derived_word_keys[7], None) if len(derived_word_keys) > 7 else None,
        derived_word_keys[8] if len(derived_word_keys) > 8 else None, derived_words.get(derived_word_keys[8], None) if len(derived_word_keys) > 8 else None,
        derived_word_keys[9] if len(derived_word_keys) > 9 else None, derived_words.get(derived_word_keys[9], None) if len(derived_word_keys) > 9 else None,

        derived_words_count,
        word_data['oed_definition'],
        word_data['mw_definition'],
        ",".join(word_data['synonyms']),
        ",".join(word_data['antonyms']),
        word_data['memory_tips']
    )
    if DEBUG_INFO:
        print(word_values)

    insert_word_query = """
    REPLACE INTO tc_words (
        word, chinese_meaning, root, etymology,
        part_of_speech, british_ipa, american_ipa,
        derived_word1, derived_word1_meaning,
        derived_word2, derived_word2_meaning,
        derived_word3, derived_word3_meaning,
        derived_word4, derived_word4_meaning,
        derived_word5, derived_word5_meaning,
        derived_word6, derived_word6_meaning,
        derived_word7, derived_word7_meaning,
        derived_word8, derived_word8_meaning,
        derived_word9, derived_word9_meaning,
        derived_word10, derived_word10_meaning,
        derived_words_count, oed_definition,
        mw_definition, synonyms,
        antonyms, memory_tips
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(insert_word_query, word_values)
        # word_id = cursor.lastrowid

        # Insert into usage_examples table
        usage_examples = word_data.get('usage_examples', [])
        insert_usage_example_query = """
        REPLACE INTO tc_usage_examples (word, sentence, translation) VALUES (%s, %s, %s)
        """

        for example in usage_examples:
            cursor.execute(insert_usage_example_query, (word, example['sentence'], example['translation']))

        connection.commit()
    except mysql.connector.Error as exp:
        print(f"Error when insert information into db: {exp}")
        connection.rollback()
    finally:
        cursor.close()

# Main function
def main(word):
    debug_trace('Step 1: Establish MySQL connection')
    connection = get_mysql_connection()

    try:
        debug_trace('Step 2: Call OpenAI API')
        word_data = get_word_data(word)

        debug_trace('Step 3: Insert data into MySQL database')
        if word_data is not None:
            insert_word_data(word, word_data, connection)
        else:
            print(f"Failed to fetch information for {word}")
    except Exception as exp:
        print(f"An error occurred to fetch {word}: {exp}")
    finally:
        debug_trace('Step 4: Close MySQL connection')
        connection.close()

def debug_trace(msg):
    if DEBUG_INFO:
        print(msg)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: ./main.py <word>")
        sys.exit(1)

    input_word = sys.argv[1]
    print(f"Start to fetch information for {input_word}......")
    main(input_word)
