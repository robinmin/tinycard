#!/usr/bin/env python3

import csv
import shutil
import re
import sys
import os


def process_file(input_file, output_file):
    """
    Reads a text file line by line, processes each line with a provided function,
    and appends the result to an output file. Creates the output file if it doesn't exist.

    Args:
        input_file: The path to the input text file.
        output_file: The path to the output text file.
        header_line: An optional header line to write to the output file initially (default: None).
    """

    header_line = ""
    word = get_filename(input_file)
    # Check if output file exists before opening
    if not os.path.exists(output_file):
        create_new_file = True
    else:
        create_new_file = False

    processed = False
    with open(input_file, "r") as input_handle, open(output_file, "a") as output_handle:
        writer = csv.writer(output_handle, quoting=csv.QUOTE_ALL)
        # Write header line if provided and the output file doesn't exist
        if create_new_file:
            writer.writerow(
                [
                    "word",
                    "analysis",
                    "example",
                    "etymology",
                    "prefix_suffix",
                    "history",
                    "word_form",
                    "memory_aid",
                    "story",
                ]
            )

        ## extract onformation from markdown content
        key = ""
        val = ""
        result = {}
        for content_line in input_handle:
            content_line = preprocess_line(content_line)
            if len(content_line) <= 0:
                continue

            # print(">>>", content_line)
            match = re.match(r"^[#*]+ *(.+)[ #*:：]*$", content_line)
            if match:
                if len(key):
                    result[key] = proccess_val(val)
                    key = ""
                    val = ""
                key = proccess_key(match.group(1))
            else:
                val = val + "\n" + content_line
        if len(key):
            result[key] = proccess_val(val)

        ## rename field
        result = rename_maping(result)
        result["word"] = word
        # print(result)

        ## write into CSV file
        if len(result) >= 6 and "analysis" in result and len(result["analysis"]) > 0:
            writer.writerow(
                [
                    (result["word"].replace("\n", "\\n") if "word" in result else ""),
                    (
                        result["analysis"].replace("\n", "\\n")
                        if "analysis" in result
                        else ""
                    ),
                    (
                        result["example"].replace("\n", "\\n")
                        if "example" in result
                        else ""
                    ),
                    (
                        result["etymology"].replace("\n", "\\n")
                        if "etymology" in result
                        else ""
                    ),
                    (
                        result["prefix_suffix"].replace("\n", "\\n")
                        if "prefix_suffix" in result
                        else ""
                    ),
                    (
                        result["history"].replace("\n", "\\n")
                        if "history" in result
                        else ""
                    ),
                    (
                        result["word_form"].replace("\n", "\\n")
                        if "word_form" in result
                        else ""
                    ),
                    (
                        result["memory_aid"].replace("\n", "\\n")
                        if "memory_aid" in result
                        else ""
                    ),
                    (result["story"].replace("\n", "\\n") if "story" in result else ""),
                ]
            )
            output_handle.flush()
            processed = True

        ## move the file into another folder if processed
        try:
            destination_folder = "./data/done2/"
            shutil.move(input_file, destination_folder)
            # print(f"File '{input_file}' moved successfully to '{destination_folder}'.")
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found.")
        except Exception as e:  # Catch other potential exceptions
            print(f"Error moving file: {e}")


def get_filename(filepath):
    """
    Extracts the filename (without path or extension) from a filepath.

    Args:
        filepath: The path to the file.

    Returns:
        The filename (without path or extension).
    """
    filename, extension = os.path.splitext(filepath)
    return filename.split("/")[-1]  # Get last part after path separators


def preprocess_content(text):
    if text is None:
        return text
    new_text = text

    new_text = re.sub("[【】]", "", new_text)

    new_text = re.sub("[ \t#*:：]*分析词义[ \t#*:：]*", "### 分析词义\n", new_text)
    new_text = re.sub("[ \t#*:：]*词义解析[ \t#*:：]*", "### 分析词义\n", new_text)
    new_text = re.sub("[ \t#*:：]*词义分析[ \t#*:：]*", "### 分析词义\n", new_text)
    new_text = re.sub("[ \t#*:：]*单词分析[ \t#*:：]*", "### 分析词义\n", new_text)
    new_text = re.sub("[ \t#*:：]*单词解析[ \t#*:：]*", "### 分析词义\n", new_text)
    new_text = re.sub("[ \t#*:：]*单词释义[ \t#*:：]*", "### 分析词义\n", new_text)
    new_text = re.sub("[ \t#*:：]*内容分析[ \t#*:：]*", "### 分析词义\n", new_text)

    new_text = re.sub("[ \t#*:：]*(列举)?例句[ \t#*:：]*", "### 列举例句\n", new_text)
    # new_text = re.sub("[ \t#*:：]*举例[ \t#*:：]*", "### 列举例句\n", new_text)

    new_text = re.sub("[ \t#*:：]*词根分析[ \t#*:：]*", "### 词根分析\n", new_text)
    new_text = re.sub("[ \t#*:：]*词缀分析[ \t#*:：]*", "### 词缀分析\n", new_text)
    new_text = re.sub(
        "[ \t#*:：](发展)?历史和文化背景*[ \t#*:：]*",
        "### 发展历史和文化背景\n",
        new_text,
    )
    # 历史和文化背景
    new_text = re.sub("[ \t#*:：]*单词变形[ \t#*:：]*", "### 单词变形\n", new_text)
    new_text = re.sub("[ \t#*:：]*词形变化[ \t#*:：]*", "### 单词变形\n", new_text)
    new_text = re.sub("[ \t#*:：]*记忆辅助[ \t#*:：]*", "### 记忆辅助\n", new_text)
    new_text = re.sub("[ \t#*:：]*小故事[ \t#*:：]*", "### 小故事\n", new_text)

    new_text = re.sub(
        r"\"", "'", re.sub(r"\n+", "\n", re.sub(r"\n *\n", "\n", new_text))
    )
    return new_text


def preprocess_line(text):
    if text is None:
        return text
    return re.sub(
        r"^[*# ]+\d+\\\. *",
        "",
        re.sub(
            r"^_+",
            "",
            re.sub(
                r"^[* ]+",
                "",
                re.sub(r"\"", "'", re.sub(r"\n+", "\n", re.sub(r"\n *\n", "\n", text))),
            ),
        ),
    )


def proccess_val(text):
    if text is None:
        return text
    return re.sub(r"[ \t\n]+$", "", re.sub(r"^[ \t\n]+", "", text))


def proccess_key(key):
    if len(key) <= 0:
        return key
    return re.sub(r"^[*# ]+\d+\\\. *", "", re.sub(r"[:：]?[ *#\t]*$", "", key))


def rename_maping(data):
    key_mapping = {
        "分析词义": "analysis",
        "列举例句": "example",
        "词根分析": "etymology",
        "词缀分析": "prefix_suffix",
        "发展历史和文化背景": "history",
        "单词变形": "word_form",
        "记忆辅助": "memory_aid",
        "小故事": "story",
    }

    return {key_mapping.get(key, key): value for key, value in data.items()}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_file(sys.argv[1], "./data/GPT_Words2.csv")
    else:
        print("No command line argument provided.")
