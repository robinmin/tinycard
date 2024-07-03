use English;

-- 01, create table tc_words
CREATE TABLE IF NOT EXISTS tc_words (
    word VARCHAR(255) NOT NULL PRIMARY KEY COMMENT '单词',
    chinese_meaning VARCHAR(255) COMMENT '中文含义',
    root VARCHAR(255) COMMENT '词根',
    etymology TEXT COMMENT '词源',

    part_of_speech VARCHAR(64) COMMENT '词性',
    british_ipa VARCHAR(64) COMMENT '英式音标',
    american_ipa VARCHAR(64) COMMENT '美式音标',

    oed_definition TEXT COMMENT 'Oxford English Dictionary释意',
    mw_definition TEXT COMMENT 'Merriam-Webster释意',
    synonyms VARCHAR(255) COMMENT '同义词',
    antonyms VARCHAR(255) COMMENT '反义词',
    memory_tips TEXT COMMENT '记忆技巧',

    derived_word1 VARCHAR(255) COMMENT '衍生词1',
    derived_word1_meaning VARCHAR(255) COMMENT '衍生词1含义',
    derived_word2 VARCHAR(255) COMMENT '衍生词2',
    derived_word2_meaning VARCHAR(255) COMMENT '衍生词2含义',
    derived_word3 VARCHAR(255) COMMENT '衍生词3',
    derived_word3_meaning VARCHAR(255) COMMENT '衍生词3含义',
    derived_word4 VARCHAR(255) COMMENT '衍生词4',
    derived_word4_meaning VARCHAR(255) COMMENT '衍生词4含义',
    derived_word5 VARCHAR(255) COMMENT '衍生词5',
    derived_word5_meaning VARCHAR(255) COMMENT '衍生词5含义',
    derived_word6 VARCHAR(255) COMMENT '衍生词6',
    derived_word6_meaning VARCHAR(255) COMMENT '衍生词6含义',
    derived_word7 VARCHAR(255) COMMENT '衍生词7',
    derived_word7_meaning VARCHAR(255) COMMENT '衍生词7含义',
    derived_word8 VARCHAR(255) COMMENT '衍生词8',
    derived_word8_meaning VARCHAR(255) COMMENT '衍生词8含义',
    derived_word9 VARCHAR(255) COMMENT '衍生词9',
    derived_word9_meaning VARCHAR(255) COMMENT '衍生词9含义',
    derived_word10 VARCHAR(255) COMMENT '衍生词10',
    derived_word10_meaning VARCHAR(255) COMMENT '衍生词10含义',
    derived_words_count INT COMMENT '衍生词数量'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='单词表';


-- 02, create table tc_usage_examples
CREATE TABLE IF NOT EXISTS tc_usage_examples (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    word VARCHAR(255) NOT NULL COMMENT '单词',
    sentence TEXT COMMENT '例句',
    translation TEXT COMMENT '例句翻译',
    key(word)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='例句表';

-- 03, create table gpt_8k_words
CREATE TABLE IF NOT EXISTS gpt_8k_words (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',

    word        VARCHAR(256) NOT NULL comment '单词',
    analysis    text NULL comment '词义',
    example     text NULL comment '例句',
    etymology   text NULL comment '词根',
    affix       text NULL comment '词缀',
    history     text NULL comment '历史和文化背景',
    word_form   text NULL comment '变形',
    memory_aid  text NULL comment '助记',
    story       text NULL comment '小故事'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ChatGPT 8K单词表';

CREATE INDEX idx_gpt_8k_words_word ON english.gpt_8k_words(word);

create view v_gpt_8k_words_abcd as
with gpt_8k_words_abcd as(
	select
		gkw.word,
		case when nd.phonetic_EN=nd.phonetic_US then nd.phonetic_EN else concat('[',nd.phonetic_EN, '] / ', nd.phonetic_US) end phonetic,
		gkw.analysis,
		gkw.example,
		gkw.etymology,
		gkw.affix,
		gkw.history,
		gkw.word_form,
		gkw.memory_aid,
		gkw.story
	from english.gpt_8k_words as gkw
	left join english.neodict as nd on gkw.word = nd.wordContent
	where nd.familiarity in ('A', 'B', 'C', 'D')
)
select * from gpt_8k_words_abcd;

create view v_gpt_8k_words_non_abcd as
with gpt_8k_words_non_abcd as(
	select
		gkw.word,
		case when nd.phonetic_EN=nd.phonetic_US then nd.phonetic_EN else concat('[',nd.phonetic_EN, '] / ', nd.phonetic_US) end phonetic,
		gkw.analysis,
		gkw.example,
		gkw.etymology,
		gkw.affix,
		gkw.history,
		gkw.word_form,
		gkw.memory_aid,
		gkw.story
	from english.gpt_8k_words as gkw
	left join english.neodict as nd on gkw.word = nd.wordContent
	where nd.familiarity not in ('A', 'B', 'C', 'D')
)
select * from gpt_8k_words_non_abcd;
