import argparse
from dicom_viewer_classes import *

"""
ディレクトリのみに対応
PAPXXXまでは指定できるようにする
v5複数画像に個別のスライス操作可能
v6枚数合わせの際に最大枚数に併せて足りないところは0うめにする
v7個別のスライス位置をずらした状態で同時にスライス移動可能.リセットボタン設置
v8諧調機能追加.画像表示中もスライスでいじれるようにしたい
v10セグメンテーション画像をカラー画像にする
v11画像を拡大縮小表示できるようにしたい
v13 画像拡大機能搭載
v14 画像拡大の重ね掛け
v15 各機能をクラスとして整理して、ほしい機能だけ使えるように改良
"""
def dicom_viewer_arguments(args_list=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('img_folders',type=str,nargs='*',help='dcmファイルがまとめられているフォルダを入力')
    parser.add_argument('--image_type','-it',type=str,default='dcm',help='対象とする画像の拡張子を指定')
    parser.add_argument('--col_limit','-cl',type=int,default=30,help='表示したい画像の画素値幅と比較して、グレイスケールかカラー画像か変える')
    args=parser.parse_args(args_list)
    return args
    
def dicom_viewer(args):
    #使用する機能が必要とする行数を計算する
    need_ROWs=dicom_viwer_base.need_ROWs+image_slice.need_ROWs+image_clip.need_ROWs
    
    base_instance=dicom_viwer_base(args,need_ROWs)

    #使用したい機能をインスタンス化
    #ここでは画像スライスと画像拡大を使用する
    image_slice_instance=image_slice(base_instance)
    image_clip_instance=image_clip(base_instance)
    base_instance.show()


if __name__=='__main__':
    args_text=None
    dicom_viewer_args=dicom_viewer_arguments(args_text)
    dicom_viewer(dicom_viewer_args)
