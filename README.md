# Dicom_viewer
Dicomファイルを見るためのプログラム。dicom_viewer_v??.py, dicom_viwer_classes.py, colormap.pyが同一ディレクトリにある必要があります。 
使用例   
python dicom_viwer_v??.py dir1(dicom画像のディレクトリ) dir2 ...  
オプション  
-cl x:  
Dicom画像の画素値がx以下の時に画素値ごとに色を付けて表示する。セグメンテーションのマスク画像の表示を想定している。  
--shuffle 1:  
画素値の色をシャッフルする。セグメンテーションの色はHSV色空間で自動的に決定される影響で、マスク画像の臓器が増えると近い数字(臓器)で似た色が割り当てられて見づらくなるので、これを回避するために色をシャッフルする。  
