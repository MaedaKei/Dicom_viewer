import os,glob
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider,Button,RectangleSelector,SpanSelector
from matplotlib import gridspec
#https://www.useful-python.com/matplotlib-layout-grid/
#https://matplotlib.org/stable/api/widgets_api.html
import pydicom as dicom
import numpy as np
from colormap import colormap
from functools import partial

class dicom_viwer_base:
    """
    Dicom_viewerの基本の機能を実装したクラス

    画像の表示と画像の階調の機能を担っている。

    引数
    args : dicom_viewer_v??.pyから渡されてくるファイルのパスなどのコマンドライン引数
    ax_rows : dicom_viewer_v??.pyでユーザーが設定した機能を表示するために必要な行数

    戻り値

    """
    need_ROWs=2#画像,メニュー
    def __init__(self,args,ax_rows):
        #画像を読み込むための関数を切り替え
        if args.image_type=='dcm':
            img2ndarray=self.dicom2ndarray
        elif args.image_type=='png':
            img2ndarray=self.png2ndarray
        #各ディレクトリのdcmファイルのパスをまとめる。このとき、枚数を合わせる
        file_num_list=[]#各ディレクトリのファイル数を格納
        dcm_path_list=[]#各ディレクトリのファイルパスを格納
        self.row_counter=0#行をカウントしておく
        for dcm_folder in args.img_folders:
            if os.path.isdir(dcm_folder)!=True:
                print(f"引数にディレクトリではないものがある :{dcm_folder}")
                return
            dcm_path_list.append(glob.glob(os.path.join(dcm_folder,'*.'+args.image_type)))
            file_num_list.append(len(dcm_path_list[-1]))
        max_file_num=max(file_num_list)
        start_dir=os.getcwd()
        self.color_sets=[('gray',None)]
        self.SEG_OR_NOT=[]
        self.hist_list=[]
        self.all_images=[]
        max_pixel_range=1
        for dir_num in range(len(dcm_path_list)):#ディレクトリ毎に画像を読み込んでいく
            dcm_pathes=dcm_path_list[dir_num]
            now_file_num=len(dcm_pathes)
            add_num=max_file_num-now_file_num
            end=add_num//2
            start=add_num-end
            images=[]#各ディレクトリ内の画像を読み込んで格納
            print(f"{args.img_folders[dir_num]},{now_file_num} \t:",end='')
            os.chdir(args.img_folders[dir_num])
            for load_dcm_path in sorted(dcm_pathes):
                img=img2ndarray(os.path.basename(load_dcm_path))
                images.append(img)
            images=np.array(images)#(pic_num,H,W)
            _,H,W=images.shape
            images=np.concatenate([np.zeros((start,H,W)),images,np.zeros((end,H,W))])
            #セグメンテーションかどうか判断
            pixel_unique,pixel_hist=np.unique(images,return_counts=True)
            print(f"{pixel_unique[0]} ~ {pixel_unique[-1]}")
            #ヒストグラムで一番個数が多いのは多分無駄なバックグラウンドなのでここを0にする
            pixel_hist[np.argmax(pixel_hist)]=0
            self.hist_list.append([pixel_unique,(pixel_hist+10000)**(1/3)])
            #ユニークの最大値と最小値から予測されるユニークの種類
            pixel_range=pixel_unique[-1]-pixel_unique[0]+1
            #print(pixel_unique,pixel_range)
            seg_check=0
            if len(pixel_unique)<=pixel_range and pixel_range<=args.col_limit:
                seg_check=1
                max_pixel_range=max(max_pixel_range,pixel_range)
            self.SEG_OR_NOT.append(seg_check)
            print(len(images),images.shape)
            self.all_images.append(images)
            os.chdir(start_dir)
        self.all_images=np.array(self.all_images)
        if sum(self.SEG_OR_NOT)>0:#どこかに1がある
            print(f"色付きセグメンテーション画像あり{int(max_pixel_range)}色")
            self.color_sets.append(colormap(color_num=int(max_pixel_range)))
        #画素値毎の出現回数を調べる？
        #各画像群を調べて初期場所を確定
        init_slice=0
        check=(self.all_images!=self.all_images[:,:,0:1,0:1])#これで次元が保持されるためブロードキャストできる#(dir_num,pic_num,H,W)
        check=check.sum(axis=(2,3))#(dir_num,pic_num)
        check=check.prod(axis=0)
        check=(check!=0)
        #print(check,check.ndim)
        """
        check=np.array(np.where(check==1))#tuple
        if len(check)>0:
            init_slice=int(check[:,0])
        else:
            print("異常事態")
        """
        dir_num=len(self.all_images)
        height_ratios=np.ones(ax_rows)*0.3
        height_ratios[0]=20
        self.gs=gridspec.GridSpec(ax_rows,dir_num,height_ratios=height_ratios,hspace=0.01,wspace=0.05,top=0.99,bottom=0.01,right=0.99,left=0.01)
        self.img_ax_list=[]
        self.img_table_list=[]
        #self.tone_button_list=[]
        #画像ごとに表示する
        self.fig=plt.figure()
        print(self.all_images.shape)
        self.button_list=[]
        for dir_i in range(len(self.all_images)):
            self.row_counter=0
            #ディレクトリ毎の画像表示
            img_ax=self.fig.add_subplot(self.gs[self.row_counter,dir_i])
            self.row_counter+=1
            img_ax.axis('off')
            self.img_ax_list.append(img_ax)
            cmap,norm=self.color_sets[self.SEG_OR_NOT[dir_i]]
            self.img_table_list.append(img_ax.imshow(self.all_images[dir_i,init_slice],cmap=cmap,norm=norm))
            #ディレクトリ毎の階調ボタン設置
            tone_button_ax=self.fig.add_subplot(self.gs[self.row_counter,dir_i])
            self.button_list.append(Button(tone_button_ax,'tone change',color='#c0c000',hovercolor='#f0f000'))
            self.button_list[-1].on_clicked(partial(self.push_tone_button,image_table=self.img_table_list[dir_i],hist=self.hist_list[dir_i]))
        self.row_counter+=1
        """
        self.fig,self.all_image, self.hist_list, self.ax_list, self.image_table_listを外側から参照して使う
        """
    #諧調ボタンが押された時の動き
    def push_tone_button(self,dammy_ars,image_table,hist):
        #画像のもとの
        tone_window_fig=plt.figure(figsize=(5,5),tight_layout=True)
        tone_window_gs=gridspec.GridSpec(3,1,height_ratios=[20,0.5,0.5])
        hist_ax=tone_window_fig.add_subplot(tone_window_gs[0,0])
        center_slice_ax=tone_window_fig.add_subplot(tone_window_gs[1,0],sharex=hist_ax)
        range_slice_ax=tone_window_fig.add_subplot(tone_window_gs[2,0])
        hist_table=hist_ax.plot(*hist,color='#000000')
        hist_ax.tick_params(labelleft=False)
        #現在の画素値範囲,元の画素値範囲
        now_lower,now_upper=image_table.norm.vmin,image_table.norm.vmax
        original_lower,original_upper=hist[0][0],hist[0][-1]
        #スライダーを動かして更新されるやつらは変数に入れておく
        value_text=hist_ax.set_title(f"{now_lower} ~ {now_upper}")
        lower_limit_line=hist_ax.axvline(now_lower,color="#FF0000",alpha=0.5)
        upper_limit_line=hist_ax.axvline(now_upper,color="#FF0000",alpha=0.5)
        center_slice=Slider(ax=center_slice_ax,label='center',valmin=original_lower,valmax=original_upper,
                            valinit=(now_lower+now_upper)/2,valstep=1,valfmt='%d',handle_style={'size':5})
        range_slice=Slider(ax=range_slice_ax,label='range',valmin=0,valmax=original_upper-original_lower,
                            valinit=now_upper-now_lower,valstep=1,valfmt='%d',handle_style={'size':5})
        def tone_slice_update(val):
            half_range=range_slice.val/2
            min=center_slice.val-half_range
            max=center_slice.val+half_range
            image_table.norm.vmin=min
            image_table.norm.vmax=max
            value_text.set_text(f"{min} ~ {max}")
            lower_limit_line.set_xdata([min,min])
            upper_limit_line.set_xdata([max,max])
            tone_window_fig.canvas.draw_idle()
            self.fig.canvas.draw_idle()
        center_slice.on_changed(tone_slice_update)
        range_slice.on_changed(tone_slice_update)
        """
        def span_select(xmin,xmax):
            pass
        span=SpanSelector(hist_ax,span_select,"horizontal",useblit=True,props=dict(alpha=0.5,facecolor="tab:blue"),interactive=True,drag_from_anywhere=True)
        """
        plt.show()
    def dicom2ndarray(self,dicom_file):
        ref=dicom.dcmread(dicom_file,force=True)
        img=ref.pixel_array
        return img
    def show(self):
        plt.show()

"""
各種機能を追加する↓
引数 : base_instance
dicom_viewer_baseクラスをインスタンス化したもの。必要な情報をインスタンス変数として保持してあるので、各種機能の実装で必要なものを参照する。
"""
class image_slice:
    """
    画像を送り見するための機能を実装したクラス

    画像ごとに個別に送り見するためのスライダー、並べた画像を同時に送るスライダー、画像ごとの表示位置を揃えるためのボタンを持っている
    """
    need_ROWs=3#個別のスライサー、統合スライサー、調整ボタン
    def __init__(self,base_instance):
        self.slicer_len=len(base_instance.all_images[0])
        dir_num=len(base_instance.all_images)
        self.each_slicer_list=[]
        self.fig=base_instance.fig
        for dir_i in range(dir_num):
            ax=base_instance.fig.add_subplot(base_instance.gs[base_instance.row_counter,dir_i])
            slicer=Slider(
                ax=ax,label=None,valinit=0,valmin=0,valmax=self.slicer_len-1,
                valfmt='%d',valstep=1,orientation='horizontal',
                handle_style={'size':5}
            )
            slicer.on_changed(partial(
                self.each_slicer_changed,slicer=slicer,
                image_table=base_instance.img_table_list[dir_i],dir_images=base_instance.all_images[dir_i]
            ))
            self.each_slicer_list.append(slicer)
        base_instance.row_counter+=1
        ax=base_instance.fig.add_subplot(base_instance.gs[base_instance.row_counter,:])
        self.group_slicer=Slider(
            ax=ax,label=None,valinit=0,valmin=0,valmax=self.slicer_len-1,
            valfmt='%d',valstep=1,orientation='horizontal',
            handle_style={'size':5}
        )
        base_instance.row_counter+=1
        self.gp_preval=0
        self.group_slicer.on_changed(self.group_slicer_changed)
        ax=base_instance.fig.add_subplot(base_instance.gs[base_instance.row_counter,:])
        base_instance.row_counter+=1
        self.align_button=Button(ax=ax,label='align slice',color='#f0f0f0',hovercolor='#FFFFFF')
        self.align_button.on_clicked(self.push_align)
    
    def each_slicer_changed(self,dammy_args,slicer,image_table,dir_images):
        image_table.set_data(dir_images[slicer.val])
        self.fig.canvas.draw_idle()
    def group_slicer_changed(self,dammy):
        change_value=self.group_slicer.val-self.gp_preval
        for slicer in self.each_slicer_list:
            slicer.set_val(max(0,min(slicer.val+change_value,self.slicer_len-1)))
        self.gp_preval=self.group_slicer.val
        self.fig.canvas.draw_idle()
    def push_align(self,dammy):
        for slicer in self.each_slicer_list:
            slicer.set_val(self.group_slicer.val)
        self.gp_preval=self.group_slicer.val
        self.fig.canvas.draw_idle()

class image_clip:
    """
    画像の拡大機能を実装したクラス。画像の縮小はできないのでリセットボタンで元に戻す。

    画像を並べている状態でどれかの画像を拡大すると、並べてある画像すべてで同じように拡大できる。
    """
    need_ROWs=1#clip_reset_button
    def __init__(self,base_instance):
        self.fig=base_instance.fig
        self.img_ax_list=base_instance.img_ax_list
        self.clips=[]
        for ax in self.img_ax_list:
            self.clips.append(RectangleSelector(
                ax,self.clip_callback,useblit=True,
                #これ以下のピクセル範囲だったらアクティブにならないってこと
                minspanx=5,minspany=5,spancoords='pixels',interactive=False,
                props=dict(edgecolor='#FF0000',alpha=1,fill=False)
            ))
        clip_reset_ax=self.fig.add_subplot(base_instance.gs[base_instance.row_counter,:])
        self.clip_reset_button=Button(clip_reset_ax,label='reset clip',color='#0000b0',hovercolor='#0000f0')
        self.clip_reset_button.on_clicked(self.push_clip_reset)
        self.original_H,self.original_W=base_instance.all_images.shape[2:]#H,W

    def clip_callback(self,eclick,erelease):
        w1,h1=int(eclick.xdata),int(eclick.ydata)
        w2,h2=int(erelease.xdata),int(erelease.ydata)
        if h1<h2 and w1<w2:
            for ax in self.img_ax_list:
                ax.set_xlim(w1,w2)
                ax.set_ylim(h2,h1)
            self.fig.canvas.draw_idle()
    def push_clip_reset(self,dammy):
        for ax in self.img_ax_list:
            ax.set_xlim(0,self.original_W)
            ax.set_ylim(self.original_H,0)
        self.fig.canvas.draw_idle()

