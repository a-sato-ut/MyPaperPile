# MyPaperPile

## 初回セットアップ
1. Settings > Actions > General > Workflow permissions で `Read and write permissions` を選択してsave
2. Settings > Secrets and variables > Actions > New repository secret で `OPENAI_API_KEY` を追加
3. Settings > Pages > Build and deployment > Branch で `main`, `/ (root)` でsave

## 論文の追加
1. `pdf` フォルダに論文pdfを追加
2. `add_pdf.command` をクリック (`pull & add & commit & push` が実行され、GitHub Actions が走る)
3. `https://[username].github.io/MyPaperPile/` で論文が表示される

## ローカルで実行する場合
- セットアップ
```bash
pip install -r requirements.txt
```
- 論文の追加
```bash
python3 src/main.py 
```
- 引用グラフの解析
```bash
python3 src/analyze_refs.py
```
- ローカルでページを表示
```bash
python3 -m http.server
```
