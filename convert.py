#!/usr/bin/env python3

import csv
import json
import re


class WordEntry:
    def __init__(self, word, content, fields):
        self.word = word
        self.content = content
        self.fields = fields


def process_file(input, output, chunk_size=1024 * 1024 * 1024):
    with open(input, "r") as f, open(output, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
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

        # field_regex = re.compile(r"^### +(.+)$\n+(.+(:?\n?.)*)")
        processed_words = 0

        for line in iter(lambda: f.read(chunk_size), ""):
            for json_line in line.splitlines():
                # if len(json_line) > 0 and processed_words < 1000:
                if len(json_line) > 0:
                    # print(json_line)
                    try:
                        data = json.loads(json_line)
                        word = data["word"]
                        content = preprocess_content(data["content"])
                        # print(content)

                        ## extract onformation from markdown content
                        key = ""
                        val = ""
                        result = {}
                        for content_line in content.splitlines():
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
                        if (
                            len(result) >= 6
                            and "analysis" in result
                            and len(result["analysis"]) > 0
                        ):
                            writer.writerow(
                                [
                                    (
                                        result["word"].replace("\n", "\\n")
                                        if "word" in result
                                        else ""
                                    ),
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
                                    (
                                        result["story"].replace("\n", "\\n")
                                        if "story" in result
                                        else ""
                                    ),
                                ]
                            )
                            ## dump content into specified file for further processing
                            with open(
                                "./data/done/{}.md".format(word), "w", newline=""
                            ) as mdfile:
                                mdfile.write(content)
                        else:
                            ## dump content into specified file for further processing
                            with open(
                                "./data/pending/{}.md".format(word), "w", newline=""
                            ) as mdfile:
                                mdfile.write(content)

                        processed_words += 1
                        print(".", end="")

                        if processed_words % 100 == 0:
                            print(f"Processed {processed_words} words")
                            csvfile.flush()
                    # Handle potential errors during JSON parsing or other operations
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Error processing line: {json_line} - {e}")
                else:
                    ## skip to next file
                    break
        csvfile.flush()
    print("\nCSV file generated successfully!")


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
    process_file("./data/GPT_Words.json", "./data/GPT_Words.csv")
