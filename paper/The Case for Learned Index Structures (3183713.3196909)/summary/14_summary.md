この論文では、Hash-mapの設計におけるデータサイズの管理と、異なるHash-mapアーキテクチャに対する学習したハッシュ関数の効果を評価しています。具体的には、空のスロットを最小化するためにデータサイズより少ないスロットを強制し、長いリンクリストを扱うことになります。固定長のレコードを扱うことで、メモリの効率を向上させ、ランダムなハッシュ関数を使用した場合と比較して大幅な空きスロットの削減が見られました。

他のHash-mapアーキテクチャとの比較で、学習したハッシュ関数を使用したインプレース型の鎖型Hash-mapが最も高いパフォーマンスを示し、従来のCuckoo Hash-mapよりも有利であることが確認されました。特に、ペイロードのサイズがパフォーマンスに大きな影響を与えることや、異なるデータ構造への適用の可能性も示唆されています。

将来的な研究として、学習したインデックスが挿入や更新にどのように対応できるかが議論されています。特に、タイムスタンプや順序に基づく挿入は、モデルが将来のデータパターンを学習することで、効率的に処理可能になる可能性があります。