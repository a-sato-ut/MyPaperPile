import os
from PyPDF2 import PdfReader
from openai import OpenAI 
import json
import pandas as pd
import csv

def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=api_key)
    return client

def gpt4_summarize_paper(text, client):
    MODEL="gpt-4o-mini"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "あなたは、文章を要約してくれる有能なアシスタントです。"},
            {"role": "user", "content": f"以下の論文の内容を、日本語で要約してください。特に、要約を読むことで論文全体の構造や主要なポイントが明確になり、実際に論文を読む際に理解が容易になるような形でお願いします。論文の結論や貢献、主要な結果、論点も簡潔に含めてください。:\n\n{text}"}
        ],
        max_tokens=1500
    )
    return response.choices[0].message.content

def gpt4_summarize_page(text, client):
    MODEL="gpt-4o-mini"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "あなたは、文章を要約してくれる有能なアシスタントです。"},
            {"role": "user", "content": f"以下はある論文の1ページの内容です。以下の文章を、日本語で要約してください。文章の内容を簡潔にまとめ、要点を押さえた要約を作成してください。:\n\n{text}"}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

def gpt4_get_title(text, client):
    MODEL="gpt-4o-mini"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "あなたは、論文のタイトルを抽出するアシスタントです。"},
            {"role": "user", "content": f"以下の論文のタイトルを取得してください。回答にはタイトルそのものだけを含めてください。余計な説明や補足は不要です。\n\n{text}"}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content

def gpt4_get_references(text, client):
    MODEL = "gpt-4o-mini"
    prompt_content = (
        "Please extract references from the provided academic text and "
        "format each reference using semicolons `;` as separators for easy parsing. "
        "Each reference should follow this format:\n\n"
        "Author(s); Year; Title of the Paper; Conference or Journal Abbreviation (without year, volume/issue numbers, or period).\n\n"
        "List each reference on a new line and ensure consistent formatting with semicolons separating fields."
        "\n\n"
        "Example:\n"
        "Smith, J., & Doe, A.; 2020; An Example Study on Machine Learning; JMLR\n\n"
        f"Text:\n{text}"
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant for extracting and formatting academic references."},
            {"role": "user", "content": prompt_content}
        ],
        max_tokens=10000
    )
    return response.choices[0].message.content

def parse_references(references):
    ref_list = references.strip().split('\n')
    parsed_refs = []
    
    for ref in ref_list:
        fields = ref.split(';')
        try:
            author = fields[0].strip()
            year = fields[1].strip()
            title = fields[2].strip()
            journal = fields[3].strip()
        except IndexError:
            author, year, title, journal = "", "", "", ""
            continue

        parsed_refs.append({
            "title": title,
            "author": author,
            "year": year,
            "journal": journal
        })

    df = pd.DataFrame(parsed_refs)
    return df

def standardize_title(title):
    # 小文字で残したい単語のリスト
    lowercase_words = {
        "a", "an", "the",      # 冠詞
        "and", "but", "or", "nor", "for", "so", "yet",  # 接続詞
        "at", "by", "in", "on", "of", "up", "to", "with", "as", "from", "into", "over", "under", "about", "after", "before", "between", "through", "during", "without", "within", "along", "around", "despite", "inside", "outside", "toward", "against", "beside", "beneath", "beyond", "near", "than", "upon",  # 前置詞
        "is", "are", "was", "were", "be", "being", "been",  # 動詞のbe動詞系
        "if", "because", "although", "unless", "until", "while", "since", "whether"  # 従属接続詞
    }

    # 特殊文字を置換
    title = title.replace("?", "(question mark)").replace("*", "(asterisk)")

    # タイトルを空白で分割し、各単語を処理する
    words = title.split()
    formatted_words = []

    for i, word in enumerate(words):
        # 最初の単語は常に大文字に
        if i == 0 or word.lower() not in lowercase_words:
            formatted_words.append(word.capitalize())
        else:
            # 小文字で残すべき単語は小文字に
            formatted_words.append(word.lower())
    
    # 最後にスペースで結合して、フォーマットされたタイトルを返す
    return " ".join(formatted_words)

if __name__ == '__main__':
    pdf_folder = 'pdf'
    paper_folder = 'paper'
    papers_json_path = "paper/papers.json"
    client = get_openai_client()

    # pdfフォルダが存在しない場合は終了
    if not os.path.exists(pdf_folder):
        print('pdf folder does not exist.')
        exit()

    # paperフォルダを作成
    os.makedirs(paper_folder, exist_ok=True)
    paper_folder_list = os.listdir(paper_folder)

    # pdfフォルダ内のファイルを処理
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, pdf_file)

            if not os.path.isfile(pdf_path):
                continue
            if not pdf_file.endswith('.pdf'):
                continue

            with open(pdf_path, 'rb') as f:
                pdf_file_name = os.path.splitext(pdf_file)[0]
                # もし pdf_file_name を含むフォルダが存在している場合はスキップ
                exist = False
                for folder in paper_folder_list:
                    if pdf_file_name in folder:
                        exist = True
                        break
                if exist:
                    continue

                reader = PdfReader(f)
                title = gpt4_get_title(reader.pages[0].extract_text(), client)
                title = standardize_title(title)

                # もし title を含むフォルダが存在している場合はスキップ
                exist = False
                for folder in paper_folder_list:
                    if title in folder:
                        exist = True
                        break
                if exist:
                    continue

                # タイトルと同じ名前のフォルダを作成
                paper_path = os.path.join(paper_folder, title + ' (' + os.path.splitext(pdf_file)[0] + ')')
                # もしすでにフォルダが存在している場合はスキップ
                if os.path.exists(paper_path):
                    continue

                os.makedirs(paper_path, exist_ok=True)
                os.makedirs(os.path.join(paper_path, 'text'), exist_ok=True)
                os.makedirs(os.path.join(paper_path, 'summary'), exist_ok=True)
                os.makedirs(os.path.join(paper_path, 'references'), exist_ok=True)
                
                # copy the pdf file to the paper folder
                os.system(f'cp "{pdf_path}" "{paper_path}"')

                # ページごとにテキストを抽出
                concatenate_text = ''
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()

                    # ページごとのテキストを保存
                    with open(os.path.join(paper_path, 'text', f'{i}.txt'), 'w') as f:
                        f.write(text)

                    # ページごとのテキストを要約
                    summary = gpt4_summarize_page(text, client)

                    # 要約を保存
                    with open(os.path.join(paper_path, 'summary', f'{i}_summary.md'), 'w') as f:
                        f.write(summary)

                    concatenate_text += text

                # 全体のテキストを保存
                with open(os.path.join(paper_path, 'all_text.txt'), 'w') as f:
                    f.write(concatenate_text)

                # 全体のテキストを要約
                summary = gpt4_summarize_paper(concatenate_text, client)

                # 全体の要約を保存
                with open(os.path.join(paper_path, 'all_summary.md'), 'w') as f:
                    f.write(summary)

                # referencesを取得
                references = gpt4_get_references(concatenate_text, client)

                # referencesを保存
                with open(os.path.join(paper_path, 'references', 'references.txt'), 'w') as f:
                    f.write(references)

                references_df = parse_references(references)

                # referencesをcsvで保存
                references_df.to_csv(
                    os.path.join(paper_path, 'references', 'references.csv'),
                    index=False,
                    quoting=csv.QUOTE_ALL
                )

                print(f'{pdf_file} has been processed.')

    # papers.json を作成
    papers_json = {}
    for folder in os.listdir(paper_folder):
        folder_path = os.path.join(paper_folder, folder)
        if not os.path.isdir(folder_path):
            continue

        pdf_file = None
        for file in os.listdir(folder_path):
            if file.endswith('.pdf'):
                pdf_file = os.path.join(folder_path, file)
                break

        if pdf_file is None:
            continue

        page_num = len(os.listdir(os.path.join(folder_path, 'summary')))

        papers_json[folder] = {
            "name": folder,
            "folder": folder_path,
            "pdf": pdf_file,
            "summaries_folder": os.path.join(folder_path, 'summary'),
            "references_folder": os.path.join(folder_path, 'references'),
            "all_summary": os.path.join(folder_path, 'all_summary.md'),
            "page_num": page_num
        }

    with open(papers_json_path, 'w') as f:
        json.dump(papers_json, f, indent=4)
