この論文では、Bツリーを学習モデルで置き換えるための試みについて述べています。200百万件のウェブサーバーログを使用し、TensorFlowを用いて前処理したデータを基に二層の全結合ニューラルネットワークをトレーニングしました。このアプローチでは、約1250予測/秒の性能を達成しましたが、いくつかの制限もあります。具体的には、TensorFlowのオーバーヘッドや、Bツリーの効率性と比べた場合の処理性能の低下が挙げられます。

その後、学習インデックスフレームワーク（LIF）や再帰モデルインデックス（RMI）を開発し、Bツリーの性能を改善または置き換えるための新しい方法を探求しました。LIFはインデックスの合成システムであり、異なるインデックス構成を自動的に生成し最適化します。また、RMIでは、キーに基づいて異なるモデルを選択し、最終的な位置を予測する階層的なモデルの構築を提案しています。この手法により、予測精度の向上が図れるとしています。