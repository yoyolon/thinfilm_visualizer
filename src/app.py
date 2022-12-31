import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import tkinter as tk
from tkinter import ttk
from film import *
from spectrum import *


# 定数
PADX = 10
PADY = 10


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
        self.window.state("zoomed")
        # スペクトルデータ
        self.spd = Spectrum(constv=0.5)
        # 入射角
        self.var_radian = tk.DoubleVar()
        self.var_radian.set(0.0)
        # 薄膜
        self.var_thickness = tk.DoubleVar()
        self.var_thickness.set(500)
        self.var_eta_film = tk.DoubleVar()
        self.var_eta_film.set(1.34)
        self.var_eta_base = tk.DoubleVar()
        self.var_eta_base.set(1.00)
        film1 = ThinFilm(0, Spectrum(constv=1.0))
        film2 = ThinFilm(self.var_thickness.get(), Spectrum(constv=self.var_eta_film.get()))
        film3 = ThinFilm(0, Spectrum(constv=self.var_eta_base.get()))
        films = [film1, film2, film3]
        self.irid = Irid(films)
        # 画像
        self.irid_texture = None

        # メインフレーム
        frm_main = ttk.Frame(master=self.window)
        frm_main.pack(fill=tk.BOTH, expand=True, padx=PADX*2, pady=PADY*2)
        # 左フレーム
        frm_lft = ttk.Frame(master=frm_main)
        frm_lft.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=PADX*2, pady=PADY*2)
        # 右フレーム
        frm_rgt = ttk.Frame(master=frm_main)
        frm_rgt.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=PADX*2, pady=PADY*2)

        # テクスチャ描画(左上)
        frm_texture = ttk.LabelFrame(master=frm_lft, text="Texture")
        frm_texture.pack(fill=tk.BOTH, expand=True,  pady=(0,PADY))
        frm_texture_prev = ttk.Frame(master=frm_texture)
        frm_texture_prev.pack(fill=tk.BOTH, expand=True,  padx=PADX, pady=PADY)
        self.canvas_texture = tk.Canvas(master=frm_texture_prev, bg="white", width=90, height=10)
        self.canvas_texture.pack(fill=tk.BOTH, expand=True, padx=PADX, pady=PADY)
        canvas_width = self.canvas_texture.winfo_width()
        canvas_height = self.canvas_texture.winfo_height()
        self.canvas_texture.create_image(canvas_width/2,
                                         canvas_height/2,
                                         image=self.irid_texture
                                         )

        # パラメータ調整フレーム
        frm_param_ajust = ttk.LabelFrame(master=frm_lft, text="Parameter")
        frm_param_ajust.pack(fill=tk.BOTH, expand=True, pady=(0,PADY))

        # 膜厚
        lbl_thickness_name = ttk.Label(master=frm_param_ajust, text="D")
        lbl_thickness_name.grid(row=0, column=1, padx=PADX, sticky="w")
        self.spinbox_thickness = ttk.Spinbox(master=frm_param_ajust, 
                                             from_=100, 
                                             to=1000, 
                                             increment=1.0,
                                             width=6,
                                             textvariable=self.var_thickness
                                             )
        self.spinbox_thickness.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="ewns")

        # 薄膜屈折率
        lbl_eta_film_name = ttk.Label(master=frm_param_ajust, text="n1")
        lbl_eta_film_name.grid(row=1, column=1, padx=PADX, sticky="ewns")
        self.spinbox_eta_film = ttk.Spinbox(master=frm_param_ajust, 
                                            from_=1, 
                                            to=3, 
                                            increment=0.01,
                                            textvariable=self.var_eta_film
                                            )
        self.spinbox_eta_film.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="ewns")

        # ベース屈折率
        lbl_eta_base_name = ttk.Label(master=frm_param_ajust, text="n2")
        lbl_eta_base_name.grid(row=2, column=1, padx=PADX, sticky="ewns")
        self.spinbox_eta_base = ttk.Spinbox(master=frm_param_ajust, 
                                            from_=1, 
                                            to=3, 
                                            increment=0.01,
                                            textvariable=self.var_eta_base
                                            )
        self.spinbox_eta_base.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="ewns")

        # 入射角
        lbl_incident_angle = ttk.Label(master=frm_param_ajust, text="θ")
        lbl_incident_angle.grid(row=3, column=1, padx=PADX, sticky="ewns")
        self.spinbox_incident = ttk.Spinbox(master=frm_param_ajust, 
                                            from_=0, 
                                            to=90, 
                                            increment=0.1,
                                            textvariable=self.var_radian
                                            )
        self.spinbox_incident.grid(row=3, column=0, padx=PADX, pady=PADY, sticky="ewns")

        # セパレータ
        separator = ttk.Separator(master=frm_param_ajust)
        separator.grid(row=4, column=0, pady=PADY, sticky="ew")

        # ボタン
        btn_load   = ttk.Button(master=frm_param_ajust, 
                                text="Save Csv", 
                                style="Accent.TButton", 
                                command=self.create_csv, 
                                )
        btn_load.grid(row=5, column=0, padx=PADX, pady=PADY, sticky="ew")
        btn_update = ttk.Button(master=frm_param_ajust, 
                                text="Calculate!", 
                                style="Accent.TButton", 
                                command=self.draw_texture, 
                                )
        btn_update.grid(row=6, column=0, padx=PADX, pady=PADY, sticky="ew")
        btn_plot   = ttk.Button(master=frm_param_ajust, 
                                text="Plot Graph!", 
                                style="Accent.TButton", 
                                command = self.graph_plot_2D, 
                                )
        btn_plot.grid(row=7, column=0, padx=PADX, pady=PADY, sticky="ew")

        # スイッチ(ONにすると反射率の表示領域が[0,1)になる)
        frm_switch = ttk.Frame(master=frm_lft)
        frm_switch.pack(fill=tk.BOTH, pady=PADY)
        self.is_graph_ajust = tk.BooleanVar()
        self.is_graph_ajust.set(False)
        self.switch_graph_ajust = ttk.Checkbutton(master=frm_param_ajust,
                                                  text="Graph Ajust",
                                                  variable=self.is_graph_ajust,
                                                  onvalue=True,
                                                  offvalue=False,
                                                  style="Switch.TCheckbutton",
                                                  )
        self.switch_graph_ajust.grid(row=8, column=0, padx=PADX, pady=PADY, sticky="ew")

        # グラフ描画(右下)
        frm_graph = ttk.LabelFrame(master=frm_rgt, text="Spectral Reflectance")
        frm_graph_outer = ttk.Frame(master=frm_graph)
        note_graph = ttk.Notebook(master=frm_graph_outer)
        frm_graph_2D = ttk.Frame(master=note_graph)
        frm_graph_3D = ttk.Frame(master=note_graph)
        frm_graph.pack(fill=tk.BOTH, expand=True)
        frm_graph_outer.pack(fill=tk.BOTH, expand=True, padx=PADX, pady=PADY)
        note_graph.pack(fill=tk.BOTH, expand=True, padx=PADX, pady=PADY)
        frm_graph_2D.pack(fill=tk.BOTH, expand=True)
        frm_graph_3D.pack(fill=tk.BOTH, expand=True)
        note_graph.add(frm_graph_2D, text="2D")
        note_graph.add(frm_graph_3D, text="3D")
        # 2Dグラフ描画
        self.fig_2D = plt.Figure()
        self.fig_2D.subplots_adjust(bottom=0.15, top=0.9) # 領域調整
        self.ax_2D = self.fig_2D.add_subplot(1, 1, 1)
        self.ax_2D.set_xlabel("wavelength(nm)")
        self.ax_2D.yaxis.set_major_locator(ticker.MaxNLocator(4))
        self.canvas_graph_2D = FigureCanvasTkAgg(self.fig_2D, frm_graph_2D)
        self.canvas_graph_2D.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # 3Dグラフ描画
        self.fig_3D = plt.Figure()
        self.fig_3D.subplots_adjust(left=0, right=1, bottom=0.03, top=1.05) # 領域調整
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
        cosTerm = np.cos(to_radian(self.var_radian.get())) # 入射角余弦
        self.spd = self.irid.evaluate(cosTerm)
        linecolor = self.spd.to_rgb()
        # ガンマ補正
        inv_gamma = 1 / 2.2
        linecolor = np.clip(linecolor, 0.0, 1.0) ** inv_gamma
        c_max = linecolor.max()
        if c_max < 0.7 and c_max > 0:
            linecolor *= 0.7/c_max
        # プロット
        self.spd.name = str(int(self.var_radian.get())) + "°"
        self.ax_2D.plot(self.spd.wl, self.spd.c, label=self.spd.name, color=linecolor)
        self.ax_2D.set_xlabel("wavelength(nm)")
        if (self.is_graph_ajust.get() == True):
            self.ax_2D.set_ylim(0, 1.0)
        self.ax_2D.yaxis.set_major_locator(ticker.MaxNLocator(4))
        self.ax_2D.legend()
        self.canvas_graph_2D.draw()


    def graph_plot_3D(self):
        """3Dグラフを描画"""
        self.ax_3D.view_init(elev=20, azim=-45) # グラフ角度リセット
        spd = Spectrum()
        x = spd.wl
        y = np.linspace(0, 89, 90) # 0-90度の入射角
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
        d  = round(self.var_thickness.get(),1)
        n1 = round(self.var_eta_film.get(), 2)
        n2 = round(self.var_eta_base.get(), 2)
        film1 = ThinFilm(0.0, Spectrum(constv=1.0))
        film2 = ThinFilm(d, Spectrum(constv=n1))
        film3 = ThinFilm(0.0, Spectrum(constv=n2))
        films = [film1, film2, film3]
        self.irid.films = films
        self.update()
        canvas_width = self.canvas_texture.winfo_width()
        canvas_height = self.canvas_texture.winfo_height()
        self.create_texture(canvas_width, canvas_height)
        self.canvas_texture.create_image(canvas_width/2,
                                         canvas_height/2,
                                         image=self.
                                         irid_texture
                                         )
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
        img_array = self.irid.create_texture(width, height)
        img_array = 255 * (img_array ** inv_gamma) # ガンマ補正
        img_array = img_array.astype(np.uint8)

        img = Image.fromarray(np.uint8(img_array))
        self.irid_texture = ImageTk.PhotoImage(image=img)


    def create_csv(self):
        """分光反射率をCSV出力する"""
        path = tk.filedialog.asksaveasfilename(filetypes=[("CSV", "csv")], 
                                               defaultextension="csv",
                                               initialdir="out", 
                                               initialfile="out.csv"
                                               )
        self.irid.create_csv(path)