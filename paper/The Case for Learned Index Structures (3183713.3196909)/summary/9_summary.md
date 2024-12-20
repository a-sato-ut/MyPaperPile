この論文の主要な内容は、「学習済みブルームフィルター」に関する研究です。従来のブルームフィルターは、特定の誤陽性率を保証しますが、提案されているアプローチでは、特定のクエリに対して実現可能な誤陽性率を提供しつつ、偽陰性率をゼロに保つことを目指しています。具体的には、クエリの配布を学習し、データベースに存在するキーとそうでないものを区別するモデルを構築します。

アクセシビリティの観点から、冷ストレージへのアクセス遅延を考慮し、複雑なモデルを用いてインデックスの空間を最小化し、誤陽性の数を減らすことが重要です。このモデルは、リカレントニューラルネットワークや畳み込みニューラルネットワークを用いて実装され、ニューラルネットワークの出力を基にして、クエリがキーである確率を計算します。設定した閾値を超える場合はキーが存在するものと判断し、そうでなければオーバーフローブルームフィルターで再確認します。

また、代替手法として、キーと非キー間の衝突を最小化しつつ、同じクラス内の衝突を最大化するようなハッシュ関数を学習する方法も提案されています。これにより、メモリの使用効率や計算の迅速化を図ることができます。