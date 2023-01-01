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
    var_angle : DoubleVar
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

        # パラメータ
        self.var_angle = tk.DoubleVar()
        self.var_angle.set(0.0)
        self.var_thickness = tk.DoubleVar()
        self.var_thickness.set(500)
        self.var_eta_film = tk.DoubleVar()
        self.var_eta_film.set(1.34)
        self.var_eta_base = tk.DoubleVar()
        self.var_eta_base.set(1.00)

        # 薄膜干渉計算用クラス
        film1 = ThinFilm(0, Spectrum(constv=1.0))
        film2 = ThinFilm(self.var_thickness.get(), Spectrum(constv=self.var_eta_film.get()))
        film3 = ThinFilm(0, Spectrum(constv=self.var_eta_base.get()))
        self.irid = Irid([film1, film2, film3])
        # 画像
        self.irid_texture = None

        # メインフレーム
        frm_main = ttk.Frame(master=self.window)
        frm_main.pack(fill=tk.BOTH, expand=True, padx=PADX, pady=PADY)


        # 右フレーム
        frm_rgt = ttk.Frame(master=frm_main)
        frm_rgt.pack(fill=tk.BOTH, expand=True, padx=PADX, pady=PADY, side=tk.LEFT)

        # 左フレーム
        frm_lft = ttk.Frame(master=frm_main)
        frm_lft.pack(fill=tk.BOTH, expand=True, padx=PADX, pady=PADY, side=tk.LEFT)

        # パラメータ調整フレーム(左)
        frm_param_ajust = ttk.LabelFrame(master=frm_lft, text="Parameter")
        frm_param_ajust.pack(fill=tk.BOTH, expand=True, padx=PADX, pady=PADY)

        # テクスチャ描画
        frm_texture_prev = ttk.Frame(master=frm_param_ajust)
        frm_texture_prev.pack(fill=tk.Y, padx=PADX, pady=PADY)
        self.canvas_texture = tk.Canvas(master=frm_texture_prev, bg="white", height=60)
        self.canvas_texture.pack(fill=tk.BOTH, expand=True)
        canvas_width = self.canvas_texture.winfo_width()
        canvas_height = self.canvas_texture.winfo_height()
        self.canvas_texture.create_image(canvas_width/2,
                                         canvas_height/2,
                                         image=self.irid_texture
                                         )

        # セパレータ
        separator = ttk.Separator(master=frm_param_ajust)
        separator.pack(fill=tk.X, padx=PADX, pady=PADY)

        # 膜厚
        frm_thickness = ttk.Frame(master=frm_param_ajust)
        frm_thickness.pack(padx=PADX, pady=PADY)
        lbl_thickness_name = ttk.Label(master=frm_thickness, text="D ")
        lbl_thickness_name.grid(row=0, column=0, padx=(0,PADX), sticky="ew")
        self.spinbox_thickness = ttk.Spinbox(master=frm_thickness, 
                                             from_=100, 
                                             to=1000, 
                                             increment=1.0,
                                             textvariable=self.var_thickness
                                             )
        self.spinbox_thickness.grid(row=0, column=1, sticky="ewns")

        # 薄膜屈折率
        frm_eta_film = ttk.Frame(master=frm_param_ajust)
        frm_eta_film.pack(padx=PADX, pady=PADY)
        lbl_eta_film_name = ttk.Label(master=frm_eta_film, text="n1")
        lbl_eta_film_name.grid(row=0, column=0, padx=(0,PADX), sticky="ew")
        self.spinbox_eta_film = ttk.Spinbox(master=frm_eta_film, 
                                            from_=1, 
                                            to=3, 
                                            increment=0.01,
                                            textvariable=self.var_eta_film
                                            )
        self.spinbox_eta_film.grid(row=0, column=1, sticky="ew")

        # ベース屈折率
        frm_eta_base = ttk.Frame(master=frm_param_ajust)
        frm_eta_base.pack(padx=PADX, pady=PADY)
        lbl_eta_base_name = ttk.Label(master=frm_eta_base, text="n2")
        lbl_eta_base_name.grid(row=0, column=0, padx=(0,PADX), sticky="ew")
        self.spinbox_eta_base = ttk.Spinbox(master=frm_eta_base, 
                                            from_=1, 
                                            to=3, 
                                            increment=0.01,
                                            textvariable=self.var_eta_base
                                            )
        self.spinbox_eta_base.grid(row=0, column=1, sticky="ew")

        # 入射角
        frm_incident = ttk.Frame(master=frm_param_ajust)
        frm_incident.pack(padx=PADX, pady=PADY)
        lbl_incident_angle = ttk.Label(master=frm_incident, text="θ")
        lbl_incident_angle.grid(row=0, column=0, padx=(0,PADX), sticky="ew")
        self.spinbox_incident = ttk.Spinbox(master=frm_incident, 
                                            from_=0, 
                                            to=90, 
                                            increment=0.1,
                                            textvariable=self.var_angle
                                            )
        self.spinbox_incident.grid(row=0, column=1, sticky="ew")

        # セパレータ
        separator2 = ttk.Separator(master=frm_param_ajust)
        separator2.pack(fill=tk.X, padx=PADX, pady=PADY)

        # 偏光状態の選択
        frm_polarized = ttk.Frame(master=frm_param_ajust)
        frm_polarized.pack(padx=PADX, pady=PADY)
        self.var_polarized = tk.IntVar()
        self.var_polarized.set(UNPOLARIZED)
        # 無偏光
        radio_unpolarized = ttk.Radiobutton(master=frm_polarized,
                                          text="unpolarized",
                                          value=UNPOLARIZED,
                                          variable=self.var_polarized
                                          )
        radio_unpolarized.grid(row=0, column=0, padx=PADX, sticky="ew")
        # p偏光
        radio_p_polarized = ttk.Radiobutton(master=frm_polarized,
                                          text="p-wave",
                                          value=P_POLARIZED,
                                          variable=self.var_polarized
                                          )
        radio_p_polarized.grid(row=0, column=1, padx=PADX, sticky="ew")
        # s偏光
        radio_s_polarized = ttk.Radiobutton(master=frm_polarized,
                                          text="s-wave",
                                          value=S_POLARIZED,
                                          variable=self.var_polarized
                                          )
        radio_s_polarized.grid(row=0, column=2, padx=PADX, sticky="ew")


        # セパレータ
        separator3 = ttk.Separator(master=frm_param_ajust)
        separator3.pack(fill=tk.X, padx=PADX, pady=PADY)

        # 保存ボタン
        btn_load   = ttk.Button(master=frm_param_ajust, 
                                text="Save Csv", 
                                command=self.create_csv, 
                                )
        btn_load.pack(fill=tk.BOTH, expand=True, padx=PADX, pady=PADY)
        # 計算ボタン
        btn_update = ttk.Button(master=frm_param_ajust, 
                                text="Calculate", 
                                command=self.draw_texture, 
                                )
        btn_update.pack(fill=tk.BOTH, expand=True, padx=PADX, pady=PADY)
        # グラフ描画ボタン
        btn_plot   = ttk.Button(master=frm_param_ajust, 
                                text="Plot Graph", 
                                command = self.graph_plot_2D, 
                                )
        btn_plot.pack(fill=tk.BOTH, expand=True, padx=PADX, pady=PADY)
        # グラフリセットボタン
        btn_reset  = ttk.Button(master=frm_param_ajust, 
                                text="Reset Graph", 
                                command = self.graph_reset_2D, 
                                )
        btn_reset.pack(fill=tk.BOTH, expand=True, padx=PADX, pady=PADY)

        # スイッチ(ONにすると反射率の表示領域が[0,1)になる)
        self.is_graph_ajust = tk.BooleanVar()
        self.is_graph_ajust.set(False)
        switch_graph_ajust = ttk.Checkbutton(master=frm_param_ajust,
                                                  text="Graph Ajust",
                                                  variable=self.is_graph_ajust,
                                                  onvalue=True,
                                                  offvalue=False,
                                                  style="Switch.TCheckbutton",
                                                  )
        switch_graph_ajust.pack(padx=PADX, pady=PADY)


        # グラフ描画(右)
        frm_graph = ttk.LabelFrame(master=frm_rgt, text="Spectral Reflectance")
        frm_graph.pack(fill=tk.BOTH, expand=True, padx=PADX, pady=PADY)

        frm_graph_outer = ttk.Frame(master=frm_graph)
        frm_graph_outer.pack(fill=tk.BOTH, expand=True, padx=PADX, pady=PADY)

        note_graph = ttk.Notebook(master=frm_graph_outer)
        note_graph.pack(fill=tk.BOTH, expand=True)

        # 2Dグラフ描画
        frm_graph_2D = ttk.Frame(master=note_graph)
        frm_graph_2D.pack(fill=tk.BOTH, expand=True)
        self.fig_2D = plt.Figure()
        self.fig_2D.subplots_adjust(bottom=0.15, top=0.9) # 領域調整
        self.ax_2D = self.fig_2D.add_subplot(1, 1, 1)
        self.ax_2D.set_xlabel("wavelength(nm)")
        self.ax_2D.yaxis.set_major_locator(ticker.MaxNLocator(4))
        self.canvas_graph_2D = FigureCanvasTkAgg(self.fig_2D, frm_graph_2D)
        self.canvas_graph_2D.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 3Dグラフ描画
        frm_graph_3D = ttk.Frame(master=note_graph)
        frm_graph_3D.pack(fill=tk.BOTH, expand=True)
        self.fig_3D = plt.Figure()
        self.fig_3D.subplots_adjust(left=0, right=1, bottom=0.03, top=1.05) # 領域調整
        self.ax_3D = self.fig_3D.add_subplot(1, 1, 1, projection="3d")
        self.ax_3D.set_xlabel("wavelength(nm)")
        self.ax_3D.set_ylabel("angle")
        self.ax_3D.zaxis.set_major_locator(ticker.MaxNLocator(4))
        self.ax_3D.view_init(elev=20, azim=-45) # グラフ角度調整
        self.canvas_graph_3D = FigureCanvasTkAgg(self.fig_3D, frm_graph_3D)
        self.canvas_graph_3D.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # ノートブックに追加
        note_graph.add(frm_graph_2D, text="2D")
        note_graph.add(frm_graph_3D, text="3D")


    def graph_reset_2D(self):
        """2Dグラフのリセット"""
        self.ax_2D.cla() #前の描画データの削除
        # 空プロット
        self.ax_2D.set_xlabel("wavelength(nm)")
        self.ax_2D.yaxis.set_major_locator(ticker.MaxNLocator(4))
        self.canvas_graph_2D.draw()


    def graph_plot_2D(self):
        """2Dグラフを描画"""
        cosTerm = np.cos(to_radian(self.var_angle.get())) # 入射角余弦
        self.spd = self.irid.evaluate(cosTerm, self.var_polarized.get())
        linecolor = self.spd.to_rgb()
        # ガンマ補正
        inv_gamma = 1 / 2.2
        linecolor = np.clip(linecolor, 0.0, 1.0) ** inv_gamma
        c_max = linecolor.max()
        if c_max < 0.7 and c_max > 0:
            linecolor *= 0.7/c_max
        # プロット
        self.spd.name = str(int(self.var_angle.get())) + "°"
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