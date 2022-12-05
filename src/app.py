import tkinter as tk
import tkinter.font
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from spectrum import *
from film import *


"""定数"""
PADX = 5
PADY = 5


class App(tk.Frame):
    """
    GUIアプリクラス
    
    Attributes
    ----------
    window: Tk
        ウィンドウ
    spd : Spectrum
        グラフプロットするSPD(Spectral Power Distribution)
    var_radian : DoubleVar
        SPDを評価する入射角を指定するバー
    var_thickness : DoubleVar
        薄膜の膜厚を指定するバー
    var_eta_film : DoubleVar
        薄膜の屈折率を指定するバー
    var_eta_base : DoubleVar
        ベース材質の屈折率
    var_kappa_base : DoubleVar
        ベース材質の消失係数
    irid : Irid
        薄膜干渉計算クラス
    irid_texture : PhotoImage
        薄膜干渉反射率テクスチャ
    canvas_texture : Canvas
        テクスチャ描画用キャンバス
    fig_2D : Figure
        2Dグラフ描画用のmatplotlibのFigureオブジェクト
    ax_2D : AxesSubplot
        2Dグラフ描画用のmatplotlibのAxesオブジェクト
    canvas_graph_2D : FigureCanvasTkAgg
        2Dグラフ描画用のmatplotlibキャンバス
    fig_3D : Figure
        3Dグラフ描画用のmatplotlibのFigureオブジェクト
    ax_3D : AxesSubplot
        3Dグラフ描画用のmatplotlibのAxesオブジェクト
    canvas_graph_3D : FigureCanvasTkAgg
        3Dグラフ描画用のmatplotlibキャンバス
    """

    def __init__(self, window):
        """
        GUIの初期化
        
        Parameters
        ----------
        window: Tk
            ウィンドウ
        """
        
        super().__init__(window)
        # ウィンドウの設定       
        self.window = window
        self.window.title("Thinfilm Tester")
        self.window.geometry("960x540")
        # フォント
        font_label = tk.font.Font(self.window, family="Arial", size=12)
        # スタイル
        style = ttk.Style()
        style.configure("Temp.TLabel", foreground="white", background="black", font=font_label) # ラベル
        style.configure("Back.TFrame", background="#1D1D1D") # フレーム(奥)
        style.configure("Temp.TFrame", background="#333333") # フレーム(手前)
        # スペクトルデータ
        self.spd = Spectrum(constv=0.5)
        self.var_radian = tk.DoubleVar()
        self.var_radian.set(0)
        # 薄膜
        self.var_thickness = tk.DoubleVar()
        self.var_thickness.set(500)
        self.var_eta_film = tk.DoubleVar()
        self.var_eta_film.set(1.34)
        self.var_eta_base = tk.DoubleVar()
        self.var_eta_base.set(1.00)
        self.var_kappa_base = tk.DoubleVar()
        self.var_kappa_base.set(0.00)
        film1 = ThinFilm(0., Spectrum(constv=1.0), Spectrum(constv=0.0))
        film2 = ThinFilm(self.var_thickness.get(), Spectrum(constv=self.var_eta_film.get()), Spectrum(constv=0.0))
        film3 = ThinFilm(0., Spectrum(constv=self.var_eta_base.get()), Spectrum(constv=self.var_kappa_base.get()))
        films = [film1, film2, film3]
        self.irid = Irid(films)
        self.irid_texture = None # 画像
        # メインフレーム
        frm_main = ttk.Frame(master=self.window, style="Back.TFrame")
        frm_main.pack(fill=tk.BOTH, expand=True)
        # 左フレーム
        frm_lft = ttk.Frame(master=frm_main, width=200, style="Back.TFrame")
        frm_lft.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=PADX, pady=PADY)
        # 右フレーム
        frm_rgt = ttk.Frame(master=frm_main, width=600, style="Back.TFrame")
        frm_rgt.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=PADX, pady=PADY)
        # パラメータ調整フレーム
        frm_param_ajust = ttk.Frame(master=frm_lft, style="Temp.TFrame")
        frm_param_ajust.pack(fill=tk.BOTH, expand=True)
        # スライドバー
        frm_lft_lbl_top = ttk.Frame(master=frm_param_ajust, width=200, style="Temp.TFrame")
        frm_lft_lbl_top.pack(fill=tk.BOTH, side=tk.TOP, padx=PADX, pady=PADY)
        frm_lft_var_top = ttk.Frame(master=frm_param_ajust, width=200, style="Temp.TFrame")
        frm_lft_var_top.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        frm_thickness = ttk.Frame(master=frm_lft_var_top, width=200, style="Temp.TFrame")
        frm_thickness.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        frm_eta_film = ttk.Frame(master=frm_lft_var_top, width=200, style="Temp.TFrame")
        frm_eta_film.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        frm_eta_base = ttk.Frame(master=frm_lft_var_top, width=200, style="Temp.TFrame")
        frm_eta_base.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        frm_kappa_base = ttk.Frame(master=frm_lft_var_top, width=200, style="Temp.TFrame")
        frm_kappa_base.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)        
        # ラベル
        lbl_param = ttk.Label(master=frm_lft_lbl_top, text="Parameter", font=font_label, style="Temp.TLabel")
        lbl_param.pack()
        # 膜厚
        lbl_thickness_name = ttk.Label(master=frm_thickness, text="D  ")
        self.lbl_thickness_value = ttk.Label(master=frm_thickness, text="")
        scl_thickness = ttk.Scale(master=frm_thickness, command=self.set_label_thickness, variable=self.var_thickness, 
                                  from_=100., to=900., length=200)
        lbl_thickness_name.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        scl_thickness.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY, expand=True)
        self.lbl_thickness_value.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        # 薄膜屈折率
        lbl_eta_film_name = ttk.Label(master=frm_eta_film, text="n1")
        self.lbl_eta_film_value = ttk.Label(master=frm_eta_film, text="")
        scl_eta_film = ttk.Scale(master=frm_eta_film, command=self.set_label_eta_film, variable=self.var_eta_film, 
                                 from_=0.0, to=2.0, length=200)
        lbl_eta_film_name.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        scl_eta_film.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY, expand=True)
        self.lbl_eta_film_value.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        # ベース屈折率
        lbl_eta_base_name = ttk.Label(master=frm_eta_base, text="n2")
        self.lbl_eta_base_value = ttk.Label(master=frm_eta_base, text="")
        scl_eta_base = ttk.Scale(master=frm_eta_base, command=self.set_label_eta_base, variable=self.var_eta_base, 
                                 from_=0.0, to=2.0, length=200)
        lbl_eta_base_name.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        scl_eta_base.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY, expand=True)
        self.lbl_eta_base_value.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        # ベース消失係数
        lbl_kappa_base_name = ttk.Label(master=frm_kappa_base, text="k2")
        self.lbl_kappa_base_value = ttk.Label(master=frm_kappa_base, text="")
        scl_kappa_base = ttk.Scale(master=frm_kappa_base, command=self.set_label_kappa_base, variable=self.var_kappa_base, 
                                   from_=0.0, to=2.0, length=200)
        lbl_kappa_base_name.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        scl_kappa_base.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY, expand=True)
        self.lbl_kappa_base_value.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        # スケールラベルの初期化
        self.set_label_thickness(self.var_thickness.get())
        self.set_label_eta_film(self.var_eta_film.get())
        self.set_label_eta_base(self.var_eta_base.get())
        self.set_label_kappa_base(self.var_kappa_base.get())

        # ラベル(評価角度)
        # パラメータ調整フレーム
        frm_eval_angle = ttk.Frame(master=frm_lft, style="Temp.TFrame")
        frm_eval_angle.pack(fill=tk.BOTH, expand=True, pady=PADY)
        frm_radian_lbl = ttk.Frame(master=frm_eval_angle, width=200, style="Temp.TFrame")
        frm_radian_lbl.pack(fill=tk.BOTH, side=tk.TOP, padx=PADX, pady=PADY)
        frm_radian = ttk.Frame(master=frm_eval_angle, width=200, style="Temp.TFrame")
        frm_radian.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        frm_radian_var = ttk.Frame(master=frm_radian, style="Temp.TFrame")
        frm_radian_var.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        lbl_radian = ttk.Label(master=frm_radian_lbl, text="Evaluation Angle", font=font_label, style="Temp.TLabel")
        lbl_radian.pack(padx=PADX, pady=PADY)
        scl_radian = ttk.Scale(master=frm_radian_var, length=200, variable=self.var_radian, from_=0.0, to=90.0)
        scl_radian.pack(fill=tk.BOTH, padx=PADX, pady=PADY, expand=True)
        # ボタン
        frm_lft_btm = tk.Frame(master=frm_eval_angle, width=200, bg="orange")
        frm_lft_btm.pack(side=tk.TOP, padx=PADX, pady=PADY)
        frm_lft_btm.rowconfigure(0, minsize=20)
        frm_lft_btm.columnconfigure([0, 1, 2], minsize=60)
        btn_load = ttk.Button(master=frm_lft_btm, text="Csv", command=self.create_csv, width=6, padding=[2,2,2,2])
        btn_load.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="ew")
        btn_update = ttk.Button(master=frm_lft_btm, text="Calc", command=self.draw_texture, width=6, padding=[2,2,2,2])
        btn_update.grid(row=0, column=1, padx=PADX, pady=PADY, sticky="ew")
        btn_plot = ttk.Button(master=frm_lft_btm, text="2DPlot", command = self.graph_plot_2D, width=6, padding=[2,2,2,2])
        btn_plot.grid(row=0, column=2, padx=PADX, pady=PADY, sticky="ew")

        # テクスチャ描画(右上)
        frm_rgt_top = tk.Frame(master=frm_rgt, width=400, bg="deepskyblue")
        frm_rgt_top.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        frm_texture_lbl = tk.Frame(master=frm_rgt_top, width=400, bg="skyblue")
        frm_texture_lbl.pack(fill=tk.BOTH, side=tk.TOP, padx=PADX, pady=PADY)
        frm_texture_prev = tk.Frame(master=frm_rgt_top, width=400, bg="skyblue")
        frm_texture_prev.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        lbl_texture = ttk.Label(master=frm_texture_lbl, text="Thin-film Texture", font=font_label, style="Temp.TLabel")
        lbl_texture.pack(padx=PADX, pady=PADY)
        self.canvas_texture = tkinter.Canvas(master=frm_texture_prev, bg="white", height=100)
        self.canvas_texture.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        canvas_width = self.canvas_texture.winfo_width()
        canvas_height = self.canvas_texture.winfo_height()
        self.canvas_texture.create_image(canvas_width/2,canvas_height/2,image=self.irid_texture) # 画像の描画
        # グラフ描画(右下)
        frm_graph = tk.Frame(master=frm_rgt, bg="deepskyblue")
        frm_graph.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        frm_graph_lbl = tk.Frame(master=frm_graph, bg="skyblue")
        frm_graph_lbl.pack(fill=tk.BOTH, side=tk.TOP, padx=PADX, pady=PADY)
        frm_graph_outer = tk.Frame(master=frm_graph, bg="skyblue")
        frm_graph_outer.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        note_graph = ttk.Notebook(master=frm_graph_outer)
        note_graph.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        frm_graph_2D = tk.Frame(master=note_graph, bg="green")
        frm_graph_2D.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        frm_graph_3D = tk.Frame(master=note_graph, bg="green")
        frm_graph_3D.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        note_graph.add(frm_graph_3D, text="3D")        
        note_graph.add(frm_graph_2D, text="2D")
        # ラベル
        lbl_graph = ttk.Label(master=frm_graph_lbl, text="Spectral Refrectance", font=font_label, style="Temp.TLabel")
        lbl_graph.pack()
        # 2D描画
        self.fig_2D = plt.Figure()
        self.ax_2D = self.fig_2D.add_subplot(1, 1, 1)
        self.ax_2D.set_xlabel("wavelength(nm)")
        self.ax_2D.yaxis.set_major_locator(ticker.MaxNLocator(4))
        self.canvas_graph_2D = FigureCanvasTkAgg(self.fig_2D, frm_graph_2D)
        self.canvas_graph_2D.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # 3D描画
        self.fig_3D = plt.Figure()
        self.fig_3D.subplots_adjust(left=0, right=1, bottom=0.03, top=1.05) # プロット領域調整
        self.ax_3D = self.fig_3D.add_subplot(1, 1, 1, projection="3d")
        self.ax_3D.set_xlabel("wavelength(nm)")
        self.ax_3D.set_ylabel("angle")
        self.ax_3D.zaxis.set_major_locator(ticker.MaxNLocator(4))
        self.ax_3D.view_init(elev=20, azim=-45) # グラフ角度調整
        self.canvas_graph_3D = FigureCanvasTkAgg(self.fig_3D, frm_graph_3D)
        self.canvas_graph_3D.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        
    def graph_plot_2D(self):
        """2Dグラフを描画"""
        self.ax_2D.cla() #前の描画データの削除
        cosTerm = np.cos(to_radian(self.var_radian.get()))
        self.spd = self.irid.evaluate(cosTerm)
        inv_gamma = 1 / 2.2
        linecolor = self.spd.to_rgb()
        linecolor = np.clip(linecolor, 0.0, 1.0) ** inv_gamma
        c_max = linecolor.max()
        if c_max < 0.7 and c_max > 0:
            linecolor *= 0.7/c_max
        self.spd.name = str(int(self.var_radian.get())) + "°"
        self.ax_2D.plot(self.spd.wl, self.spd.c, label=self.spd.name, color=np.clip(linecolor, 0.0, 1.0))
        self.ax_2D.set_xlabel("wavelength(nm)")
        self.ax_2D.set_ylim(0, 1.0)
        self.ax_2D.yaxis.set_major_locator(ticker.MaxNLocator(4))        
        self.ax_2D.legend()
        self.canvas_graph_2D.draw()
        
    
    def graph_plot_3D(self):
        """3Dグラフを描画"""
        self.ax_3D.view_init(elev=20, azim=-45) # グラフ角度リセット
        spd = Spectrum()
        x = spd.wl
        y = np.linspace(0, 89, 90) # 0-90
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)
        for i in range(90):
            temp = self.irid.evaluate(np.cos(np.pi/180 * i))
            for j in range(NSAMPLESPECTRUM):
                Z[i][j] = temp.c[j]
        self.ax_3D.plot_surface(X, Y, Z, cmap=cm.plasma, linewidth=0, antialiased=False)
        self.ax_3D.plot_wireframe(X, Y, Z, rstride=10, cstride=NSAMPLESPECTRUM//3, color="red",linewidth=1)
        self.ax_3D.set_zlim(0.0, 1.0)
        self.ax_3D.zaxis.set_major_locator(ticker.MaxNLocator(4))
        self.ax_3D.yaxis.set_major_locator(ticker.MaxNLocator(4))
        self.ax_3D.set_xlabel("wavelength(nm)")
        self.ax_3D.set_ylabel("angle")    
        self.canvas_graph_3D.draw()
        
        
    def draw_texture(self):
        """テクスチャを描画"""
        self.ax_2D.cla() #前の描画データの削除
        self.ax_3D.cla() #前の描画データの削除
        d = round(self.var_thickness.get(),1)
        n1 = round(self.var_eta_film.get(),2)
        n2 = round(self.var_eta_base.get(),2)
        k2 = round(self.var_kappa_base.get(),2)
        film1 = ThinFilm(0.0, Spectrum(constv=1.0), Spectrum(constv=0.0))
        film2 = ThinFilm(d, Spectrum(constv=n1), Spectrum(constv=0.0))
        film3 = ThinFilm(0.0, Spectrum(constv=n2), Spectrum(constv=k2))
        films = [film1, film2, film3]
        self.irid.films = films
        self.update()
        canvas_width = self.canvas_texture.winfo_width()
        canvas_height = self.canvas_texture.winfo_height()
        self.create_texture(canvas_width, canvas_height)
        self.canvas_texture.create_image(canvas_width/2,canvas_height/2,image=self.irid_texture)
        self.graph_plot_3D() # 3Dの描画        
    
    
    def create_texture(self, width, height):
        """
        テクスチャを生成

        Parameters
        ----------
        width : int
            テクスチャ幅
        height : int
            テクスチャ高さ
        """
        inv_gamma = 1 / 2.2
        array = self.irid.create_texture(width, height)
        array = 255 * (array ** inv_gamma) # ガンマ補正
        array = array.astype(np.uint8)

        img = Image.fromarray(np.uint8(array))
        self.irid_texture = ImageTk.PhotoImage(image=img)


    def create_csv(self, path='out.csv'):
        """
        分光反射率をCSV出力する

        Parameters
        ----------
        path : string
            ファイル名
        """
        self.irid.create_csv(path)
        
        
    def set_label_thickness(self, value):
        """
        膜厚ラベルの更新

        Parameters
        ----------
        value : float
            膜厚値

        """
        self.lbl_thickness_value['text'] = str(round(float(value), 1))
        

    def set_label_eta_film(self, value):
        """
        薄膜屈折率ラベルの更新

        Parameters
        ----------
        value : float
            薄膜の屈折率

        """
        s = str(round(float(value), 2))
        self.lbl_eta_film_value['text'] = s.rjust(6)

        
    def set_label_eta_base(self, value):
        """
        ベース材質屈折率ラベルの更新

        Parameters
        ----------
        value : float
            ベース材質の屈折率

        """
        s = str(round(float(value), 2))
        self.lbl_eta_base_value['text'] = s.rjust(6)


    def set_label_kappa_base(self, value):
        """
        ベース材質消衰係数ラベルの更新

        Parameters
        ----------
        value : float
            ベース材質の消衰係数

        """
        s = str(round(float(value), 2))
        self.lbl_kappa_base_value['text'] = s.rjust(6)