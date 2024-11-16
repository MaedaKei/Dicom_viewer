import argparse
from dicom_viewer_classes import *

def dicom_viewer_arguments(args_list=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('img_folders',type=str,nargs='*',help='dcmファイルがまとめられているフォルダを入力')
    parser.add_argument('--image_type','-it',type=str,default='dcm',help='対象とする画像の拡張子を指定')
    parser.add_argument('--col_limit','-cl',type=int,default=30,help='表示したい画像の画素値幅と比較して、グレイスケールかカラー画像か変える')
    #parser.add_argument('--clip_image','-ci',nargs=2,type=float,help='画像の画素値を諧調する')
    args=parser.parse_args(args_list)
    return args
    
def dicom_viewer(args):
    need_ROWs=dicom_viwer_base.need_ROWs+image_slice.need_ROWs+image_clip.need_ROWs
    #need_ROWs=dicom_viwer_base.need_ROWs+image_clip.need_ROWs
    #必要な変数を持っているので何か機能を追加するときは引数にbase_instanceを渡すようにする
    #dicom_viwer_baseの略
    base_instance=dicom_viwer_base(args,need_ROWs)
    image_slice_instance=image_slice(base_instance)
    image_clip_instance=image_clip(base_instance)
    base_instance.show()


if __name__=='__main__':
    args_text=None
    dicom_viewer_args=dicom_viewer_arguments(args_text)
    dicom_viewer(dicom_viewer_args)
