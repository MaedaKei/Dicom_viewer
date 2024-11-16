# Dicom_viewer
セグメンテーションの結果確認のためのプログラムです。連続CT画像、連続正解MASK画像、連続予測MASK画像を並べて表示し、同時にスライスを移動することができます。
並べて表示した画像のどれかに対してドラックアンドドロップを行うと、赤線の枠が表示され、すべての画像が同様にズームアップされます。
ズームアップは下段に表示されるreset clipでリセットすることができます。

動作に必要なファイルはdicom_viewer_v??.py, dicom_viewer_classes.py, colormap.pyの3つです。
使用する機能の追加、削除はdicom_viewer_v??.pyを編集することで行えます。
機能の実装はdicom_viewer_classes.pyにされています。
colormap.pyはセグメンテーションのマスク画像に色を付けるために必要です。
dicom_viewer_v??.py, dicom_viwer_classes.py, colormap.pyが同一ディレクトリにある必要があります。 

使用例   
python dicom_viwer_v??.py dir1(dicom画像のディレクトリまでのパス) dir2 ...  

オプション  
-cl x:  
最大と最小の画素値の差がx以下かつ画措置の種類がx種類以下の場合にマスク画像として画素値ごとに色を付けて表示します。 
このオプションで0を指定するとマスク画像であってもグレースケールで表示されるようになります。

動作にはnumpy, matplotlib, pydicomが必要です。
よろしければwikiの参考映像もご覧ください。
