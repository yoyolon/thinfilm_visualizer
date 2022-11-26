import tkinter as tk
from tkinter import ttk
import tkinter.font
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
    fig2D : Figure
        2Dグラフ描画用のmatplotlibのFigureオブジェクト
    ax2D : AxesSubplot
        2Dグラフ描画用のmatplotlibのAxesオブジェクト
    canvas_2Dgraph : FigureCanvasTkAgg
        2Dグラフ描画用のmatplotlibキャンバス
    fig3D : Figure
        3Dグラフ描画用のmatplotlibのFigureオブジェクト
    ax3D : AxesSubplot
        3Dグラフ描画用のmatplotlibのAxesオブジェクト
    canvas_3Dgraph : FigureCanvasTkAgg
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
        # スタイル
        style = ttk.Style()
        # ウィンドウの設定       
        self.window = window
        self.window.title("Thinfilm Tester")
        self.window.geometry("640x480")
        # フォント
        font_label = tk.font.Font(self.window, family="Arial", weight="bold", size=15)
        # スペクトルデータ
        self.spd = Spectrum(constv=0.5)
        self.var_radian = tk.DoubleVar()
        self.var_radian.set(0)
        # 薄膜
        self.var_thickness = tk.DoubleVar()
        self.var_thickness.set(500)
        self.var_eta_film = tk.DoubleVar()
        self.var_eta_film.set(1.6)
        self.var_eta_base = tk.DoubleVar()
        self.var_eta_base.set(1.8)
        self.var_kappa_base = tk.DoubleVar()
        self.var_kappa_base.set(1.9)
        film1 = ThinFilm(0., Spectrum(constv=1.0), Spectrum(constv=0.0))
        film2 = ThinFilm(self.var_thickness.get(), Spectrum(constv=self.var_eta_film.get()), Spectrum(constv=0.0))
        film3 = ThinFilm(0., Spectrum(constv=self.var_eta_base.get()), Spectrum(constv=self.var_kappa_base.get()))
        films = [film1, film2, film3]
        self.irid = Irid(films)
        self.irid_texture = None # 画像
        # メインフレーム
        frm_main = tk.Frame(master=self.window, bg="green")
        frm_main.pack(fill=tk.BOTH, expand=True)
        # 左フレーム
        frm_lft = tk.Frame(master=frm_main, width=200, bg="red")
        frm_lft.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=PADX, pady=PADY)
        # 右フレーム
        frm_rgt = tk.Frame(master=frm_main, width=400, bg="blue")
        frm_rgt.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=PADX, pady=PADY)
        # パラメータ調整スライドバー(左上)
        frm_lft_lbl_top = tk.Frame(master=frm_lft, width=200, bg="orange")
        frm_lft_lbl_top.pack(fill=tk.BOTH, side=tk.TOP, padx=PADX, pady=PADY)
        frm_lft_var_top = tk.Frame(master=frm_lft, width=200, bg="orange")
        frm_lft_var_top.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        frm_thickness = tk.Frame(master=frm_lft_var_top, width=200, bg="yellow")
        frm_thickness.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        frm_eta_film = tk.Frame(master=frm_lft_var_top, width=200, bg="yellow")
        frm_eta_film.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        frm_eta_base = tk.Frame(master=frm_lft_var_top, width=200, bg="yellow")
        frm_eta_base.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        frm_kappa_base = tk.Frame(master=frm_lft_var_top, width=200, bg="yellow")
        frm_kappa_base.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)        
        # ラベル
        lbl_param = ttk.Label(master=frm_lft_lbl_top, text="Parameter", font=font_label)
        lbl_param.pack(padx=PADX, pady=PADY)
        # 膜厚
        lbl_thickness_name = ttk.Label(master=frm_thickness, text="D  ")
        self.lbl_thickness_value = ttk.Label(master=frm_thickness, text="")
        scl_thickness = ttk.Scale(master=frm_thickness, command=self.SetLabelThickness, variable=self.var_thickness, 
                                  from_=100., to=900., length=200)
        lbl_thickness_name.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        scl_thickness.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY, expand=True)
        self.lbl_thickness_value.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        # 薄膜屈折率
        lbl_eta_film_name = ttk.Label(master=frm_eta_film, text="n1")
        self.lbl_eta_film_value = ttk.Label(master=frm_eta_film, text="")
        scl_eta_film = ttk.Scale(master=frm_eta_film, command=self.SetLabelEtaFilm, variable=self.var_eta_film, 
                                 from_=0.0, to=2.0, length=200)
        lbl_eta_film_name.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        scl_eta_film.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY, expand=True)
        self.lbl_eta_film_value.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        # ベース屈折率
        lbl_eta_base_name = ttk.Label(master=frm_eta_base, text="n2")
        self.lbl_eta_base_value = ttk.Label(master=frm_eta_base, text="")
        scl_eta_base = ttk.Scale(master=frm_eta_base, command=self.SetLabelEtaBase, variable=self.var_eta_base, 
                                 from_=0.0, to=2.0, length=200)
        lbl_eta_base_name.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        scl_eta_base.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY, expand=True)
        self.lbl_eta_base_value.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        # ベース消失係数
        lbl_kappa_base_name = ttk.Label(master=frm_kappa_base, text="k2")
        self.lbl_kappa_base_value = ttk.Label(master=frm_kappa_base, text="")
        scl_kappa_base = ttk.Scale(master=frm_kappa_base, command=self.SetLabelKappaBase, variable=self.var_kappa_base, 
                                   from_=0.0, to=2.0, length=200)
        lbl_kappa_base_name.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        scl_kappa_base.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY, expand=True)
        self.lbl_kappa_base_value.pack(side=tk.LEFT, fill=tk.BOTH, padx=PADX, pady=PADY)
        # スケールラベルの初期化
        self.SetLabelThickness(self.var_thickness.get())
        self.SetLabelEtaFilm(self.var_eta_film.get())
        self.SetLabelEtaBase(self.var_eta_base.get())
        self.SetLabelKappaBase(self.var_kappa_base.get())
        # ラベル(評価角度)
        frm_radian_lbl = tk.Frame(master=frm_lft, width=200, bg="orange")
        frm_radian_lbl.pack(fill=tk.BOTH, side=tk.TOP, padx=PADX, pady=PADY)
        frm_radian = tk.Frame(master=frm_lft, width=200, bg="orange")
        frm_radian.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        frm_radian_var = tk.Frame(master=frm_radian, bg = "yellow")
        frm_radian_var.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        lbl_radian = ttk.Label(master=frm_radian_lbl, text="Evaluation Angle", font=font_label)
        lbl_radian.pack(padx=PADX, pady=PADY)
        scl_radian = ttk.Scale(master=frm_radian_var, length=200, variable=self.var_radian, from_=0.0, to=90.0)
        scl_radian.pack(fill=tk.BOTH, padx=PADX, pady=PADY, expand=True)
        # ボタン
        frm_lft_btm = tk.Frame(master=frm_lft, width=200, bg="orange")
        frm_lft_btm.pack(side=tk.TOP, padx=PADX, pady=PADY)
        frm_lft_btm.rowconfigure(0, minsize=20)
        frm_lft_btm.columnconfigure([0, 1, 2], minsize=60)
        btn_load = ttk.Button(master=frm_lft_btm, text="Csv", command=self.CreateCSV, width=6, padding=[2,2,2,2])
        btn_load.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="ew")
        btn_update = ttk.Button(master=frm_lft_btm, text="Calc", command=self.DrawTexture, width=6, padding=[2,2,2,2])
        btn_update.grid(row=0, column=1, padx=PADX, pady=PADY, sticky="ew")
        btn_plot = ttk.Button(master=frm_lft_btm, text="2DPlot", command = self.GraphPlot2D, width=6, padding=[2,2,2,2])
        btn_plot.grid(row=0, column=2, padx=PADX, pady=PADY, sticky="ew")
        # テクスチャ描画(右上)
        frm_rgt_top = tk.Frame(master=frm_rgt, width=400, bg="deepskyblue")
        frm_rgt_top.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        frm_texture_lbl = tk.Frame(master=frm_rgt_top, width=400, bg="skyblue")
        frm_texture_lbl.pack(fill=tk.BOTH, side=tk.TOP, padx=PADX, pady=PADY)
        frm_texture_prev = tk.Frame(master=frm_rgt_top, width=400, bg="skyblue")
        frm_texture_prev.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=PADX, pady=PADY)
        lbl_texture = ttk.Label(master=frm_texture_lbl, text="Thin-film Texture", font=font_label)
        lbl_texture.pack(padx=PADX, pady=PADY)
        self.canvas_texture = tkinter.Canvas(master=frm_texture_prev, bg="white", height=50)
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
        lbl_graph = ttk.Label(master=frm_graph_lbl, text="Spectral Refrectance", font=font_label)
        lbl_graph.pack(padx=PADX, pady=PADY)
        # 2D描画
        self.fig2D = plt.Figure()
        self.ax2D = self.fig2D.add_subplot(1, 1, 1)
        self.ax2D.set_xlabel("wavelength(nm)")
        self.ax2D.yaxis.set_major_locator(ticker.MaxNLocator(4))
        self.canvas_2Dgraph = FigureCanvasTkAgg(self.fig2D, frm_graph_2D)
        self.canvas_2Dgraph.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # 3D描画
        self.fig3D = plt.Figure()
        self.ax3D = self.fig3D.add_subplot(1, 1, 1, projection="3d")
        self.ax3D.set_xlabel("wavelength(nm)")
        self.ax3D.set_ylabel("angle")
        self.ax3D.zaxis.set_major_locator(ticker.MaxNLocator(4))
        self.canvas_3Dgraph = FigureCanvasTkAgg(self.fig3D, frm_graph_3D)
        self.canvas_3Dgraph.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        
    def GraphPlot2D(self):
        """2Dグラフを描画"""
        cosTerm = np.cos(DegreeToRadian(self.var_radian.get()))
        self.spd = self.irid.Evaluate(cosTerm)
        linecolor = self.spd.ToRGB()
        self.spd.name = str(int(self.var_radian.get())) + "°"
        self.ax2D.plot(self.spd.wl, self.spd.c, label=self.spd.name, color=np.clip(linecolor, 0.0, 1.0))
        self.ax2D.set_xlabel("wavelength(nm)")
        self.ax2D.set_ylim(0, 1.0)
        self.ax2D.yaxis.set_major_locator(ticker.MaxNLocator(4))        
        self.ax2D.legend()
        self.canvas_2Dgraph.draw()
        
    
    def GraphPlot3D(self):
        """3Dグラフを描画"""
        spd = Spectrum()
        x = spd.wl
        y = np.linspace(0, 89, 90)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)
        for i in range(90):
            temp = self.irid.Evaluate(np.cos(np.pi/180 * i))
            for j in range(NSAMPLESPECTRUM):
                Z[i][j] = temp.c[j]
#         self.ax3D.plot_surface(X, Y, Z, cmap=cm.plasma, linewidth=0, antialiased=False)
        self.ax3D.plot_wireframe(X, Y, Z, rstride=10, cstride=NSAMPLESPECTRUM//10, color="red")
        self.ax3D.set_zlim(0.0, 1.0)
        self.ax3D.zaxis.set_major_locator(ticker.MaxNLocator(4))
        self.ax3D.yaxis.set_major_locator(ticker.MaxNLocator(4))
        self.ax3D.set_xlabel("wavelength(nm)")
        self.ax3D.set_ylabel("angle")        
        self.ax3D.legend()
        self.canvas_3Dgraph.draw()
        
        
    def DrawTexture(self):
        """テクスチャを描画"""
        self.ax2D.cla() #前の描画データの削除
        self.ax3D.cla() #前の描画データの削除
        film1 = ThinFilm(0., Spectrum(constv=1.0), Spectrum(constv=0.0))
        film2 = ThinFilm(self.var_thickness.get(), Spectrum(constv=self.var_eta_film.get()), Spectrum(constv=0.0))
        film3 = ThinFilm(0., Spectrum(constv=self.var_eta_base.get()), Spectrum(constv=self.var_kappa_base.get()))
        films = [film1, film2, film3]
        self.irid.films = films
        self.update()
        canvas_width = self.canvas_texture.winfo_width()
        canvas_height = self.canvas_texture.winfo_height()
        self.CreateTexture(canvas_width, canvas_height)
        self.canvas_texture.create_image(canvas_width/2,canvas_height/2,image=self.irid_texture)
        self.GraphPlot3D() # 3Dの描画        
    
    
    def CreateTexture(self, width, height):
        """
        テクスチャを生成

        Parameters
        ----------
        width : int
            テクスチャ幅
        height : int
            テクスチャ高さ
        """
        array = self.irid.CreateTexture(width, height)
        img = Image.fromarray(np.uint8(array))
        self.irid_texture = ImageTk.PhotoImage(image=img)


    def CreateCSV(self, path='out.csv'):
        """
        分光反射率をCSV出力する

        Parameters
        ----------
        path : string
            ファイル名
        """
        self.irid.CreateCSV(path)
        
        
    def SetLabelThickness(self, value):
        """
        膜厚ラベルの更新

        Parameters
        ----------
        value : float
            膜厚値

        """
        self.lbl_thickness_value['text'] = str(round(float(value), 1))
        

    def SetLabelEtaFilm(self, value):
        """
        薄膜屈折率ラベルの更新

        Parameters
        ----------
        value : float
            薄膜の屈折率

        """
        s = str(round(float(value), 1))
        self.lbl_eta_film_value['text'] = s.rjust(7)

        
    def SetLabelEtaBase(self, value):
        """
        ベース材質屈折率ラベルの更新

        Parameters
        ----------
        value : float
            ベース材質の屈折率

        """
        s = str(round(float(value), 1))
        self.lbl_eta_base_value['text'] = s.rjust(7)


    def SetLabelKappaBase(self, value):
        """
        ベース材質消衰係数ラベルの更新

        Parameters
        ----------
        value : float
            ベース材質の消衰係数

        """
        s = str(round(float(value), 1))
        self.lbl_kappa_base_value['text'] = s.rjust(7)



print("app.py loading.")
