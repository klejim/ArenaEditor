# -*- coding: UTF-8 -*-
import array
from enum import Enum
import os
from random import choice
import sys
import time

import wx
import wx.lib.newevent
import wx.lib.scrolledpanel as scrolled

import df_files as df
import commented_json as c_json
from childframes import ConfigFrame, EditColorFrame
from profiling import benchmark, profile
import op_handler

if getattr(sys, 'frozen', False):
    CWD = sys._MEIPASS
else:
    CWD = "../"
__PROFILE__ = False
IMG = CWD + "ressources/"
# some constants
EDIT_SIZE_X, EDIT_SIZE_Y = 1600, 1600
TILENUMBER_X, TILENUMBER_Y = 16, 16
# used for event handling
# MyFrame
NewEventMiniatures, EVT_LOAD_MINIATURES = wx.lib.newevent.NewEvent()
ID_LOAD = wx.NewId()
ID_NEW_DEFAULT = wx.NewId()
ID_NEW = wx.NewId()
ID_SAVE = wx.NewId()
ID_SAVE_AS = wx.NewId()
ID_SAVE_IMAGE = wx.NewId()
ID_SAVE_ALL_IMAGES = wx.NewId()
ID_CLOSE = wx.NewId()
ID_UNDO = wx.NewId()
ID_REDO = wx.NewId()
ID_CUT = wx.NewId()
ID_COPY = wx.NewId()
ID_PASTE = wx.NewId()
ID_SELECT_ALL = wx.NewId()
ID_ZOOM_IN = wx.NewId()
ID_ZOOM_OUT = wx.NewId()
ID_HELP = wx.NewId()
ID_ABOUT = wx.NewId()
ID_LEVEL_UP = wx.NewId()
ID_LEVEL_DOWN = wx.NewId()
ID_LOAD_TILESET = wx.NewId()
ID_LOAD_COLORSCHEME = wx.NewId()
ID_OPEN_CONFIG = wx.NewId()
ID_EDIT_COLORSCHEME = wx.NewId()
# Toolbar
ID_TOOL_NEW = wx.NewId()
ID_TOOL_LOAD = wx.NewId()
ID_TOOL_PENSIZE = wx.NewId()
ID_TOOL_SELECT_PEN = wx.NewId()
ID_TOOL_RECT_SEL = wx.NewId()
ID_TOOL_LABEL_PENSIZE = wx.NewId()


class Colour(Enum):
    (BLACK,
     DGRAY,
     BLUE,
     LBLUE,
     GREEN,
     LGREEN,
     CYAN,
     LCYAN,
     RED,
     LRED,
     MAGENTA,
     LMAGENTA,
     BROWN,
     YELLOW,
     LGRAY,
     WHITE) = range(16)


charFromType = {
    df.Tile.CHASM: "C",
    df.Tile.FLOOR: ".",
    df.Tile.RAMP: "R",
    df.Tile.FORTIFICATION: "F",
    df.Tile.WATER: "W",
    df.Tile.WATER_SOURCE: "+",
    df.Tile.WATER_RAMP: "w",
    df.Tile.LAVA: "L",
    df.Tile.LAVA_RAMP: "l",
    df.Tile.GRASS: "g",
    df.Tile.TREE: "T",
    df.Tile.SAND: "~",
    df.Tile.SOIL: ",",
    df.Tile.WALL: "P",
    df.Tile.EMPTY: "#",
    df.Tile.OPEN_LRAMP: "#",
    df.Tile.OPEN_WRAMP: "#",
    df.Tile.OPEN_RAMP: "#",
}

colorMaterial = {
    df.Tile.CHASM: [Colour.DGRAY],
    df.Tile.FLOOR: [Colour.LGRAY],
    df.Tile.RAMP: [Colour.LGRAY],
    df.Tile.FORTIFICATION: [Colour.LGRAY],
    df.Tile.WATER: [Colour.LBLUE],
    df.Tile.WATER_SOURCE: [Colour.CYAN],
    df.Tile.WATER_RAMP: [Colour.LBLUE],
    df.Tile.LAVA: [Colour.LRED],
    df.Tile.LAVA_RAMP: [Colour.LRED],
    df.Tile.GRASS: [Colour.GREEN],
    df.Tile.TREE: [Colour.BROWN],
    df.Tile.SAND: [Colour.YELLOW],
    df.Tile.SOIL: [Colour.BROWN],
    df.Tile.OPEN_DGRAY: [Colour.DGRAY],
    df.Tile.OPEN_GRAY: [Colour.LGRAY],
    df.Tile.OPEN_BLUE: [Colour.LBLUE],
    df.Tile.OPEN_CYAN: [Colour.CYAN],
    df.Tile.OPEN_RED: [Colour.LRED],
    df.Tile.OPEN_GREEN: [Colour.GREEN],
    df.Tile.OPEN_YELLOW: [Colour.YELLOW],
    df.Tile.OPEN_BROWN: [Colour.BROWN],
    df.Tile.OPEN_WATER: [Colour.BLUE],
    df.Tile.OPEN_LAVA: [Colour.RED],
    df.Tile.OPEN_LRAMP: [Colour.LRED],
    df.Tile.OPEN_WRAMP: [Colour.LBLUE],
    df.Tile.OPEN_RAMP: [Colour.LGRAY],
    df.Tile.OPEN_WALL: [Colour.LGRAY],
    df.Tile.SKY: [Colour.CYAN],
    df.Tile.WALL_C: [Colour.LGRAY],
    df.Tile.WALL_N: [Colour.LGRAY],
    df.Tile.WALL_S: [Colour.LGRAY],
    df.Tile.WALL_E: [Colour.LGRAY],
    df.Tile.WALL_W: [Colour.LGRAY],
    df.Tile.WALL_NS: [Colour.LGRAY],
    df.Tile.WALL_NE: [Colour.LGRAY],
    df.Tile.WALL_NW: [Colour.LGRAY],
    df.Tile.WALL_SE: [Colour.LGRAY],
    df.Tile.WALL_SW: [Colour.LGRAY],
    df.Tile.WALL_EW: [Colour.LGRAY],
    df.Tile.WALL_NSE: [Colour.LGRAY],
    df.Tile.WALL_NSW: [Colour.LGRAY],
    df.Tile.WALL_NEW: [Colour.LGRAY],
    df.Tile.WALL_SEW: [Colour.LGRAY],
    df.Tile.WALL_ALL: [Colour.LGRAY],
    df.Tile.WALL: [Colour.LGRAY],
    df.Tile.EMPTY: [Colour.CYAN],
}

tileFromType = {
    df.Tile.CHASM: [35],
    df.Tile.FLOOR: [43],
    df.Tile.RAMP: [30],
    df.Tile.FORTIFICATION: [206],
    df.Tile.WATER: [247],
    df.Tile.WATER_SOURCE: [247],
    df.Tile.WATER_RAMP: [30],
    df.Tile.LAVA: [247],
    df.Tile.LAVA_RAMP: [30],
    df.Tile.GRASS: [39, 44, 46, 96],
    df.Tile.TREE: [79],
    df.Tile.SAND: [126, 247],
    df.Tile.SOIL: [126, 247],
    df.Tile.WALL: [205],
    df.Tile.EMPTY: [178],
    df.Tile.OPEN_DGRAY: [250],
    df.Tile.OPEN_GRAY: [250],
    df.Tile.OPEN_BLUE: [250],
    df.Tile.OPEN_CYAN: [250],
    df.Tile.OPEN_RED: [250],
    df.Tile.OPEN_GREEN: [250],
    df.Tile.OPEN_YELLOW: [250],
    df.Tile.OPEN_BROWN: [250],
    df.Tile.OPEN_WATER: [247],
    df.Tile.OPEN_LAVA: [247],
    df.Tile.OPEN_LRAMP: [31],
    df.Tile.OPEN_WRAMP: [31],
    df.Tile.OPEN_RAMP: [31],
    df.Tile.OPEN_WALL: [43],
    df.Tile.SKY: [178],
    df.Tile.WALL_C: [79],
    df.Tile.WALL_N: [79],
    df.Tile.WALL_S: [79],
    df.Tile.WALL_E: [79],
    df.Tile.WALL_W: [79],
    df.Tile.WALL_NS: [186],
    df.Tile.WALL_NE: [200],
    df.Tile.WALL_NW: [188],
    df.Tile.WALL_SE: [201],
    df.Tile.WALL_SW: [187],
    df.Tile.WALL_EW: [205],
    df.Tile.WALL_NSE: [204],
    df.Tile.WALL_NSW: [185],
    df.Tile.WALL_NEW: [202],
    df.Tile.WALL_SEW: [203],
    df.Tile.WALL_ALL: [206]
}


class Clock(wx.Timer):
    def __init__(self, sb):
        wx.Timer.__init__(self)
        self.sb = sb

    def Notify(self):
        t = time.localtime(time.time())
        st = time.strftime("%d-%b-%Y   %I:%M:%S", t)
        self.sb.SetStatusText(st, 2)


class MyStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.parent = parent
        self.count = 0
        self.SetFieldsCount(6)
        self.SetStatusWidths([-1, -3, 40, 16, 150, 16])
        rect = self.GetFieldRect(1)
        self.g = wx.Gauge(self, wx.ID_ANY, 50)
        self.zoomin = wx.Button(self, wx.ID_ANY, size=(16, 16),
                                style=wx.BORDER_NONE | wx.BU_EXACTFIT)
        bmp = wx.Image(IMG+"icon_zoom_in.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.zoomin.SetBitmap(bmp)
        rect = self.GetFieldRect(5)
        self.zoomin.SetRect(rect)
        self.slider = wx.Slider(self, wx.ID_ANY, 100, 10, 300, size=(250, -1),
                                style=wx.SL_HORIZONTAL)
        self.slider.SetValue(100)
        self.SetStatusText("100%", 2)
        self.zoomout = wx.Button(self, wx.ID_ANY, size=(16, 16),
                                 style=wx.BORDER_NONE | wx.BU_EXACTFIT)
        bmp = wx.Image(IMG+"icon_zoom_out.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.zoomout.SetBitmap(bmp)
        rect = self.GetFieldRect(3)
        self.zoomin.SetRect(rect)
        self.Reposition()
        self.Bind(wx.EVT_SLIDER, self.onSlide)
        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Bind(wx.EVT_IDLE, self.onIdle)
        self.zoomin.Bind(wx.EVT_BUTTON, parent.onZoomIn)
        self.zoomout.Bind(wx.EVT_BUTTON, parent.onZoomOut)

    def onSlide(self, event):
        val = self.slider.GetValue()
        print("setting status text to", val)
        self.SetStatusText(str(val) + "%", 2)
        self.parent.scale = val / 100
        self.parent.redrawMainPanel(True)

    def onSize(self, event):
        event.Skip()
        self.Reposition()
        self.sizeChanged = True

    def onIdle(self, event):
        if self.sizeChanged:
            self.Reposition()

    def Reposition(self):
        self.zoomin.SetRect(self.GetFieldRect(5))
        self.zoomout.SetRect(self.GetFieldRect(3))
        self.slider.SetRect(self.GetFieldRect(4))
        self.g.SetRect(self.GetFieldRect(1))
        self.sizeChanged = False

    def incrementGauge(self, i=1):
        self.count += i
        if self.count == self.g.GetRange():
            self.count = 0
        self.g.SetValue(self.count)


class BrushType(Enum):
    (PEN,
     PAINT_RECTANGLE,
     SELECTION_RECTANGLE) = range(3)


class Brush:
    def __init__(self, brushtype=BrushType.PEN, pensize=1,
                 tileleft=df.Tile.EMPTY, tileright=df.Tile.EMPTY):
        self.type = brushtype
        self.penSize = pensize
        self.tileLeftClick = tileleft
        self.tileRightClick = tileleft


class TilePaintedOp(op_handler.Operation):
    def __init__(self, frame, new, old, level, i):
        self.init(frame, new, old, level, i)

    def init(self, frame, new, old, level, i):
        self.new = new
        self.old = old
        self.frame = frame
        self.level = level
        self.i = i
        self.x = i % df.ARENA_WIDTH
        self.y = (i - self.x) // df.ARENA_HEIGHT

    def do(self):
        self.frame.map.levels[self.level][self.i] = self.new
        tile = self.frame.GetTile(self.new)
        w, h = self.frame.tileWidth, self.frame.tileHeight
        self.frame.images[self.level].Paste(tile, self.x*w, self.y*h)

    @benchmark
    def undo(self):
        self.frame.map.levels[self.level][self.i] = self.old
        tile = self.frame.GetTile(self.old)
        w, h = self.frame.tileWidth, self.frame.tileHeight
        self.frame.images[self.level].Paste(tile, self.x*w, self.y*h)

    def __str__(self):
        string = ("object: "
                  + "new = " + self.new.name + " | old = " + self.old.name
                  + ", level = " + str(self.level)
                  + ", i = " + str(self.i)
                  + ", x = " + str(self.x) + ", y = " + str(self.y))
        return string

    def __repr__(self):
        return self.__str__()


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=wx.GetDisplaySize(),
                          style=wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE)
        self.handler = op_handler.Handler(100000)
        self.config = {}
        self.loadConfig()
        self.arenaChanged = False
        self.tiles = {}
        self.tile_w = 1
        self.tile_h = 1
        self.images = [wx.Image(144, 144, array.array('B', [255, 255, 255]*144*144))for i in range(9)]
        self.current_level = 4
        self.tileRightClick = df.Tile.WATER
        self.currentTilePainted = df.Tile.EMPTY
        self.tileLeftClick = df.Tile.LAVA
        self.selection = []
        self.lastTilePaintedCoords = (0, 0)
        self.brushes = [Brush()]*3
        self.active_brush = 0
        self.loadRessources()
        self.createToolBar()
        self.map = None
        self.current_file = None
        data = array.array('B', [255] * 3*df.ARENA_WIDTH*df.ARENA_HEIGHT)
        img = wx.Image(df.ARENA_WIDTH, df.ARENA_HEIGHT, data)
        img.Rescale(EDIT_SIZE_X, EDIT_SIZE_Y)
        self.buffer = img.ConvertToBitmap()
        self.mainBmp = None
        self.scale = 1.0
        self.tmpMainImg = None
        self.miniatures = []
        self.initUI()
        self.Show()

    def loadConfig(self):
        try:
            open(CWD+"config.json", 'r')
        except FileNotFoundError:
            print("config.json not found. A default file will be created.")
            text = '''\
{
    //fichier contenant les définitions des couleurs utilisées par l'application
    "colorscheme": "./data/colors.txt",
    //emplacement du tileset par défaut
    "tileset": "./data/curses_640x300.bmp",
    //arène par défaut
    "default_arena": "./data/arena.txt",
    //répertoire de sauvegarde par défaut
    "save_directory": "./saved"
}'''
            self.config = c_json.load(text)
            with open("config.json", 'w') as config:
                config.write(text)
        else:
            print("loading config.json...")
            with open(CWD+"config.json", 'r') as config:
                self.config = c_json.load(config.read().replace('\\', '/'))
            for key in self.config:
                self.config[key] = CWD + self.config[key]

    def initUI(self):
        self.sb = MyStatusBar(self)
        self.SetStatusBar(self.sb)

        self.scale_x, self.scale_y = 1, 1
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.imgPanel = scrolled.ScrolledPanel(self, wx.ID_ANY,
                                               wx.Point(0, 0), wx.Size(180, 144*9))
        self.mainPanel = wx.ScrolledWindow(self, wx.ID_ANY, size=wx.Size(1200, 1200),
                                           style=wx.HSCROLL | wx.VSCROLL)
        self.mainPanel.SetCursor(wx.Cursor(wx.CURSOR_PENCIL))
        mainSizer.Add(self.imgPanel, 0)
        mainSizer.Add(self.mainPanel, 1, flag=wx.EXPAND | wx.ALL, border=10)
        self.mainPanel.SetMinSize(self.mainPanel.GetSize())
        self.mainPanel.Bind(wx.EVT_PAINT, self.onpainttest)
        self.mainPanel.SetScrollRate(20, 20)
        self.mainPanel.SetVirtualSize(wx.Size(EDIT_SIZE_X, EDIT_SIZE_Y))
        self.mainPanel.SetBackgroundColour(wx.WHITE)
        self.mainPanel.ClearBackground()
        self.mainPanel.EnableScrolling(True, True)
        # left panel
        self.SetSizer(mainSizer)
        self.imgPanel.SetBackgroundColour(wx.Colour(145, 154, 255))
        self.imgPanel.ClearBackground()
        self.sb.g.SetRange(0)
        self.loadMiniatures()
        self.imgPanel.SetupScrolling()
        # Menus
        fileMenu = wx.Menu()
        newMenu = wx.Menu()
        newMenu.Append(ID_NEW_DEFAULT, "Arène (défaut)\tCtrl+Alt+N",
                       "Créer une nouvelle arène à partir de celle par défaut")
        newMenu.Append(ID_NEW, "Arène vide\tCtrl+N",
                       "Créer une nouvelle arène vide")
        fileMenu.AppendSubMenu(newMenu, "Nouveau", "Créer une nouvelle arène")
        fileMenu.Append(ID_LOAD, "Ouvrir\tCtrl+O",
                        "Charger une arène depuis un fichier texte")
        fileMenu.Append(wx.ID_SEPARATOR)
        fileMenu.Append(ID_SAVE, "Enregistrer\tCtrl+S",
                        "Enregistrer l'arène courante dans un fichier texte")
        fileMenu.Append(ID_SAVE_AS, "Enregistrer sous...\tCtrl+Shift+S",
                        "Enregistrer l'arène courante dans un fichier texte")
        fileMenu.Append(ID_SAVE_IMAGE, "Enregistrer l'image",
                        "Enregistrer le niveau actuel dans un fichier .png")
        fileMenu.Append(ID_SAVE_ALL_IMAGES, "Enregistrer les images",
                        "Enregistrer toute l'arène dans un dossier d'images")
        fileMenu.Append(wx.ID_SEPARATOR)
        fileMenu.Append(ID_CLOSE, "Quitter\tCtrl+Q", "Quitter le programme")
        helpMenu = wx.Menu()
        helpMenu.Append(ID_HELP, "Aide\tF1", "Afficher la fenêtre d'aide")
        helpMenu.AppendSeparator()
        helpMenu.Append(ID_ABOUT, "A propos")
        editMenu = wx.Menu()
        editMenu.Append(ID_UNDO, "Annuler\tCtrl+Z")
        editMenu.Append(ID_REDO, "Rétablir\tCtrl+Y")
        editMenu.AppendSeparator()
        editMenu.Append(ID_COPY, "Copier\tCtrl+C")
        editMenu.Append(ID_CUT, "Couper\tCtrl+X")
        editMenu.Append(ID_PASTE, "Coller\tCtrl+V")
        editMenu.AppendSeparator()
        editMenu.Append(ID_SELECT_ALL, "Sélectionner tout")
        displayMenu = wx.Menu()
        displayMenu.Append(ID_LEVEL_UP, "Aller au niveau supérieur\tCtrl+Up",
                           "Afficher et éditer le niveau supérieur à celui actuel")
        displayMenu.Append(ID_LEVEL_DOWN, "Aller au niveau inférieur\tCtrl+Down",
                           "Afficher et éditer le niveau inférieur à celui actuel")
        displayMenu.AppendSeparator()
        displayMenu.Append(ID_ZOOM_IN, "Zoom avant")
        displayMenu.Append(ID_ZOOM_OUT, "Zoom arrière")

        toolMenu = wx.Menu()
        toolMenu.Append(ID_EDIT_COLORSCHEME, "Editeur de palette\tCtrl+Alt+P",
                        "Ouvrir l'éditeur de palette dans une nouvelle fenêtre")
        toolMenu.Append(ID_OPEN_CONFIG, "Editeur de configuration\tCtrl+Alt+F",
                        "Modifier le fichier de configuration")
        toolMenu.Append(ID_LOAD_TILESET, "Charger un tileset\tCtrl+T",
                        "Changer le tileset actif")
        toolMenu.Append(ID_LOAD_COLORSCHEME, "Charger une palette\tCtrl+P",
                        "Changer la palette active")
        # disabling item which are not implemented
        editMenu.Enable(ID_UNDO, False)
        editMenu.Enable(ID_REDO, False)
        editMenu.Enable(ID_COPY, False)
        editMenu.Enable(ID_CUT, False)
        editMenu.Enable(ID_PASTE, False)
        editMenu.Enable(ID_SELECT_ALL, False)
        helpMenu.Enable(ID_HELP, False)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&Fichier")
        menuBar.Append(editMenu, "Edition")
        menuBar.Append(displayMenu, "Affichage")
        menuBar.Append(toolMenu, "Outils")
        menuBar.Append(helpMenu, "&Aide")
        self.SetMenuBar(menuBar)
        self.menubar = menuBar
        # events binding
        self.Bind(wx.EVT_MENU, self.onLoad, id=ID_LOAD)
        self.Bind(wx.EVT_MENU, self.onNewDefault, id=ID_NEW_DEFAULT)
        self.Bind(wx.EVT_MENU, self.onNew, id=ID_NEW)
        self.Bind(wx.EVT_MENU, self.onSave, id=ID_SAVE)
        self.Bind(wx.EVT_MENU, self.onSaveAs, id=ID_SAVE_AS)
        self.Bind(wx.EVT_MENU, self.onSaveImage, id=ID_SAVE_IMAGE)
        self.Bind(wx.EVT_MENU, self.onSaveAllImages, id=ID_SAVE_ALL_IMAGES)
        self.Bind(wx.EVT_MENU, self.onClose, id=ID_CLOSE)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_MENU, self.onZoomIn, id=ID_ZOOM_IN)
        self.Bind(wx.EVT_MENU, self.onZoomOut, id=ID_ZOOM_OUT)
        self.Bind(wx.EVT_MENU, self.onAbout, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.onChangeLevelUp, id=ID_LEVEL_UP)
        self.Bind(wx.EVT_MENU, self.onChangeLevelDown, id=ID_LEVEL_DOWN)
        self.mainPanel.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)
        self.Bind(EVT_LOAD_MINIATURES, self.loadMiniatures)
        self.Bind(wx.EVT_MENU, self.onToolConfig, id=ID_OPEN_CONFIG)
        self.Bind(wx.EVT_MENU, self.onLoadTileset, id=ID_LOAD_TILESET)
        self.Bind(wx.EVT_MENU, self.onLoadColorscheme, id=ID_LOAD_COLORSCHEME)
        self.Bind(wx.EVT_MENU, self.onEditColorScheme, id=ID_EDIT_COLORSCHEME)
        self.Bind(wx.EVT_MENU, self.onUndo, id=ID_UNDO)
        self.Bind(wx.EVT_MENU, self.onRedo, id=ID_REDO)

    @benchmark
    def onMouseEvent(self, event):
        if self.mainBmp is not None:
            brush = self.brushes[self.active_brush]
            if not (event.LeftDown() or event.LeftUp() or event.RightDown()
                    or event.RightUp() or event.Dragging()):
                event.Skip()
            elif (brush.type == BrushType.PEN
                  and (event.LeftDown() or event.RightDown())):
                print("===LeftDown Event===")
                pos = event.GetPosition()
                posAbs = self.mainPanel.CalcUnscrolledPosition(pos)
                print("in panel coordinates : ", posAbs)
                if event.LeftDown():
                    type = brush.tileLeftClick
                else:
                    type = brush.tileRightClick
                print("type =", type)
                xTile = int(posAbs.x/self.scale // self.tile_w)
                yTile = int(posAbs.y/self.scale // self.tile_h)
                print("xTile =", xTile, ", yTile =", yTile)
                self.selection.clear()
                for i in range(brush.penSize**2):
                    x = xTile + (i % brush.penSize)
                    y = yTile + (i - (i % brush.penSize)) // brush.penSize
                    self.selection.append((x, y))
                self.paintSelection(type, xTile, yTile)
                self.handler.push(op_handler.StartPaintGroup())
                self.redrawMainPanel()
                self.currentTilePainted = type
                self.lastTilePaintedCoords = (xTile, yTile)
            elif brush.type == BrushType.PEN and (event.LeftUp() or event.RightUp()):
                self.handler.push(op_handler.EndPaintGroup())
                # print("done : ", self.handler.done)
                print("undone : ", self.handler.undone)
            elif brush.type == BrushType.PEN and event.Dragging():
                # print("===Dragging event===")
                type = self.currentTilePainted
                posAbs = self.mainPanel.CalcUnscrolledPosition(event.GetPosition())
                # print("current pos =", posAbs)
                xTile = int(posAbs.x/self.scale // self.tile_w)
                yTile = int(posAbs.y/self.scale // self.tile_h)
                if (xTile != self.lastTilePaintedCoords[0]
                   or yTile != self.lastTilePaintedCoords[1]):
                    # print("xTile =", xTile, " and yTile =", yTile)
                    # update selection with the current tile and all the tiles
                    # between this one and the previous event
                    x0, y0 = self.lastTilePaintedCoords
                    if x0 != xTile or y0 != yTile:
                        dx = xTile - self.lastTilePaintedCoords[0]
                        dy = yTile - self.lastTilePaintedCoords[1]
                        sensx, sensy = dx * -1, dy*-1
                        # sensx > 0 if dx negative : the current tile is before
                        # the last in the list
                        dx = abs(dx)
                        dy = abs(dy)
                        # print("last tile painted =", self.lastTilePaintedCoords)
                        # print("dx =", dx, " and dy =", dy)
                        ix, iy = 0, 0
                        self.selection.clear()
                        self.selection.append((x0, y0))
                        while dy > 0 or dx > 0:
                            # print("dx =", dx, " and dy =", dy)
                            if dx >= dy:
                                ix += 1 * (-1 if sensx > 0 else 1)
                                dx -= 1
                            else:
                                iy += 1 * (-1 if sensy > 0 else 1)
                                dy -= 1
                            print("adding tile", (x0+ix, y0+iy), "to selection")
                            # accounting for pensize
                            x = x0+ix
                            y = y0+iy
                            for i in range(brush.penSize**2):
                                x1 = x + (i % brush.penSize)
                                y1 = y + (i - (i % brush.penSize)) // brush.penSize
                                if (x1, y1) not in self.selection:
                                    self.selection.append((x1, y1))
                        self.lastTilePaintedCoords = (x0+ix, y0+iy)
                        # now we paint all the tiles in selection
                        for x, y in self.selection:
                            self.computeChange(type, x, y)
                        self.selection.clear()
                        self.redrawMainPanel()
            elif (brush.type == BrushType.PAINT_RECTANGLE
                  and (event.LeftDown() or event.RightDown())):
                print("==start selection")
                posAbs = self.mainPanel.CalcUnscrolledPosition(event.GetPosition())
                x = int(posAbs.x/self.scale // self.tile_w)
                y = int(posAbs.y/self.scale // self.tile_h)
                self.selection.clear()
                print("pos =", x, y)
                self.selection.append((x, y))
            elif (brush.type == BrushType.PAINT_RECTANGLE
                  and (event.LeftUp() or event.RightUp())):
                print("===End Selection===")
                posAbs = self.mainPanel.CalcUnscrolledPosition(event.GetPosition())
                try:
                    x0 = self.selection[0][0]
                    y0 = self.selection[0][1]
                except IndexError:
                    dlg = wx.MessageDialog(self, "erreur : "+str(posAbs),
                                           style=wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                xTile = int(posAbs.x/self.scale // self.tile_w)
                yTile = int(posAbs.y/self.scale // self.tile_h)
                self.selection.append((xTile, yTile))
                dy = y0 - yTile
                dx = x0 - xTile
                sensx, sensy = dx * (-1), dy * (-1)
                w = abs(dx) + 1
                h = abs(dy) + 1
                # print("x0, y0 =", x0, y0)
                # print("current pos =", xTile, yTile)
                # print("sensx =", sensx, "sensy =", sensy)
                # print(" w et h =", w, h)
                self.selection.clear()
                for i in range(w * h):
                    # print("i =", i)
                    ix = (i % w) * (-1 if sensx < 0 else 1)
                    iy = (i - abs(ix)) // w * (-1 if sensy < 0 else 1)
                    # print("ix, iy =", ix, iy)
                    x = x0 + ix
                    y = y0 + iy
                    # print("x, y =", x, y)
                    self.selection.append((x, y))
                if event.LeftUp():
                    type = brush.tileLeftClick
                else: type = brush.tileRightClick
                self.paintSelection(type, x0, y0)
                self.redrawMainPanel()

    def redrawMainPanel(self, redrawBackground=False):
        size = self.images[self.current_level].GetSize()
        size.x *= self.scale
        size.y *= self.scale
        img = self.images[self.current_level].Copy()
        img.Rescale(size.x, size.y, wx.IMAGE_QUALITY_NORMAL)
        self.mainBmp = img.ConvertToBitmap()
        self.buffer = wx.Bitmap(self.mainBmp.GetSize())
        self.mainPanel.SetVirtualSize(self.mainBmp.GetSize())
        # self.mainPanel.SetSize(self.mainBmp.GetSize())
        dc = wx.BufferedDC(None, self.buffer, wx.BUFFER_VIRTUAL_AREA)
        dc.DrawBitmap(self.mainBmp, 0, 0)
        if (redrawBackground and (size.x < self.mainPanel.GetMinSize().x
                                  or size.y < self.mainPanel.GetMinSize().y)):
            eraseBackground = True
        else:
            eraseBackground = False
        self.mainPanel.Refresh(eraseBackground)
        self.mainPanel.QueueEvent(wx.PaintEvent(self.mainPanel.GetId()))
        self.arenaChanged = True

    @benchmark
    def paintSelection(self, type, x0, y0):
        self.handler.push(op_handler.StartPaintGroup())
        xf, yf = self.selection[-1]  # get the last element
        w = abs(x0 - xf)+1
        h = abs(y0 - yf)+1
        s = set(self.selection)

        for e in s.copy():
            x, y = e
            # if (x0 < x < xf) and (y0 < y < yf):
            if (0 < abs(x-x0) < w-1) and (0 < abs(y-y0) < h-1):
                print("yep")
                if type == df.Tile.EMPTY:
                    self.pushTilePaintedOp(x, y, self.current_level, newtype=type)
                    self.map.levels[self.current_level][y*df.ARENA_WIDTH+x] = type
                    if self.current_level > 0:
                        underType = self.map.levels[self.current_level-1][y*df.ARENA_WIDTH+x]
                    else: underType = df.Tile.EMPTY
                    self.makeSky(underType, x, y, self.current_level-1)
                else:
                    if type == df.Tile.WALL: type = df.Tile.WALL_ALL
                    # computeChange is usually the one to push the TilePaintedOp
                    # event but since we don't use that function here we need to
                    # push it
                    self.pushTilePaintedOp(x, y, self.current_level, newtype=type)
                    self.paint(type, y*df.ARENA_WIDTH+x)
                s.discard(e)
        for x, y in s:
            if x == x0 or y == y0 or x == xf or y == yf:
                self.computeChange(type, x, y)
        self.handler.push(op_handler.EndPaintGroup())
        self.selection.clear()
        # print("done : ", self.handler.done)
        # print("undone : ", self.handler.undone)

    @benchmark
    def computeChange(self, newType, xTile, yTile, walls=True):
        oldtypes = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                if xTile+x < 0 or xTile+x>df.ARENA_WIDTH-1 or yTile+y<0 or yTile+y>df.ARENA_HEIGHT-1:
                    continue
                oldtypes.append(self.map.levels[self.current_level][(yTile+y)*df.ARENA_WIDTH+xTile+x])
        if walls:
            #oldtype = self.map.levels[self.current_level][yTile*df.ARENA_WIDTH+xTile]
            self.DoTheWallThing(newType, xTile, yTile)  # both remove and place walls
        if newType == df.Tile.EMPTY:
            if self.current_level > 0:
                underType = self.map.levels[self.current_level-1][yTile*df.ARENA_WIDTH+xTile]
            else: underType = df.Tile.EMPTY
            self.makeSky(underType, xTile, yTile, self.current_level-1)
        else:
            type = self.map.levels[self.current_level][yTile*df.ARENA_WIDTH+xTile] #newtype if not changed by self.DoTheWallThing
            tile = self.GetTile(type)
            self.images[self.current_level].Paste(tile, xTile*self.tile_w, yTile*self.tile_h)
            self.makeSky(type, xTile, yTile, self.current_level)
            #push paint operation to the handler           
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if xTile+x < 0 or xTile+x>df.ARENA_WIDTH-1 or yTile+y<0 or yTile+y>df.ARENA_HEIGHT-1:
                        continue
                    old = oldtypes.pop(0)
                    self.pushTilePaintedOp(xTile+x, y+yTile, self.current_level, oldtype=old)

    @benchmark
    def DoTheWallThing(self, newType, xTile, yTile):
        self.map.levels[self.current_level][yTile*df.ARENA_WIDTH+xTile] = newType
        for x in range(-1, 2):
            for y in range(-1, 2):
                if (xTile + x < 0 or xTile + x > df.ARENA_WIDTH - 1
                   or yTile + y < 0 or yTile + y > df.ARENA_HEIGHT - 1):
                    continue
                # print("cell :", x, y)
                types = self.map.levels[self.current_level].types
                i = df.ARENA_WIDTH*(yTile+y)+xTile+x
                z = self.current_level
                if types[i].value & df.Tile.WALL.value:
                    # nine cases depending on the coordinates
                    # top-left corner
                    if (xTile+x == 0 and yTile+y == 0):
                        #  only the eastern and southern tiles are checked
                        east_tile = types[i+1]
                        south_tile = types[i+df.ARENA_WIDTH]
                        if east_tile.value & df.Tile.WALL.value and south_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_SE, i)
                        elif east_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_E, i)
                        elif south_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_S, i)
                    # top right corner
                    elif xTile+x == df.ARENA_WIDTH-1 and yTile+y == 0:
                        # only the western and southern tiles are checked
                        west_tile = types[i-1]
                        south_tile = types[i+df.ARENA_WIDTH]
                        if west_tile.value & df.Tile.WALL.value and south_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_SW, i)
                        elif west_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_W, i)
                        elif south_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_S, i)
                    # bottom right corner
                    elif xTile+x == df.ARENA_WIDTH-1 and yTile+y == df.ARENA_HEIGHT-1:
                        # only the western and northern tiles are checked
                        west_tile = types[i-1]
                        north_tile = types[i-df.ARENA_WIDTH]
                        if west_tile.value & df.Tile.WALL.value and north_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_NW, i)
                        elif west_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_W, i)
                        elif north_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_N, i)
                    # bottom left corner
                    elif xTile+x == 0 and yTile+y == df.ARENA_HEIGHT-1:
                        # only the eastern and northern tiles are checked
                        east_tile = types[i+1]
                        north_tile = types[i-df.ARENA_WIDTH]
                        if east_tile.value & df.Tile.WALL.value and north_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_NE, i)
                        elif east_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_E, i)
                        elif north_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_N, i)
                    # now we check for the four borders
                    # northern border
                    elif yTile+y == 0:
                        # only the southern, eastern and western tiles are checked
                        east_tile = types[i+1]
                        west_tile = types[i-1]
                        south_tile = types[i+df.ARENA_WIDTH]
                        if east_tile.value & df.Tile.WALL.value and west_tile.value & df.Tile.WALL.value and south_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_SEW, i)
                        elif east_tile.value & df.Tile.WALL.value and west_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_EW, i)
                        elif east_tile.value & df.Tile.WALL.value and south_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_SE, i)
                        elif west_tile.value & df.Tile.WALL.value and south_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_SW, i)
                        elif west_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_W, i)
                        elif east_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_E, i)
                        elif south_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_S, i)
                    # eastern border
                    elif xTile+x == df.ARENA_WIDTH-1:
                        # only the northern, southern, and western tiles are checked
                        west_tile = types[i-1]
                        north_tile = types[i-df.ARENA_WIDTH]
                        south_tile = types[i+df.ARENA_WIDTH]
                        if (west_tile.value & df.Tile.WALL.value
                           and north_tile.value & df.Tile.WALL.value
                           and south_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NSW, i)
                        elif (west_tile.value & df.Tile.WALL.value
                              and north_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NW, i)
                        elif (west_tile.value & df.Tile.WALL.value
                              and south_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_SW, i)
                        elif (south_tile.value & df.Tile.WALL.value
                              and north_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NS, i)
                        elif west_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_W, i)
                        elif north_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_N, i)
                        elif south_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_S, i)
                    # southern border
                    elif yTile+y == df.ARENA_HEIGHT-1:
                        # only the northern, eastern and western tiles are checked
                        east_tile = types[i+1]
                        west_tile = types[i-1]
                        north_tile = types[i-df.ARENA_WIDTH]
                        if (east_tile.value & df.Tile.WALL.value
                           and west_tile.value & df.Tile.WALL.value
                           and north_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NEW, i)
                        elif (east_tile.value & df.Tile.WALL.value
                              and west_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_EW, i)
                        elif (east_tile.value & df.Tile.WALL.value
                              and north_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NE, i)
                        elif (west_tile.value & df.Tile.WALL.value
                              and north_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NW, i)
                        elif west_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_W, i)
                        elif east_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_E, i)
                        elif north_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_N, i)
                    # western border
                    elif xTile+x == 0:
                        # only the northern, southern, and eastern tiles are checked
                        east_tile = types[i+1]
                        north_tile = types[i-df.ARENA_WIDTH]
                        south_tile = types[i+df.ARENA_WIDTH]
                        if (east_tile.value & df.Tile.WALL.value
                           and north_tile.value & df.Tile.WALL.value
                           and south_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NSE, i)
                        elif (east_tile.value & df.Tile.WALL.value
                              and north_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NE, i)
                        elif (east_tile.value & df.Tile.WALL.value
                              and south_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_SE, i)
                        elif (south_tile.value & df.Tile.WALL.value
                              and north_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NS, i)
                        elif east_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_E, i)
                        elif north_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_N, i)
                        elif south_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_S, i)
                    # finally, the generic case
                    else:
                        east_tile = types[i+1]
                        west_tile = types[i-1]
                        north_tile = types[i-df.ARENA_WIDTH]
                        south_tile = types[i+df.ARENA_WIDTH]
                        # all four
                        if (east_tile.value & df.Tile.WALL.value
                           and west_tile.value & df.Tile.WALL.value
                           and north_tile.value & df.Tile.WALL.value
                           and south_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_ALL, i)
                        # combinations of 3
                        elif (east_tile.value & df.Tile.WALL.value
                              and west_tile.value & df.Tile.WALL.value
                              and north_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NEW, i)
                        elif (east_tile.value & df.Tile.WALL.value
                              and west_tile.value & df.Tile.WALL.value
                              and south_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_SEW, i)
                        elif (north_tile.value & df.Tile.WALL.value
                              and south_tile.value & df.Tile.WALL.value
                              and west_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NSW, i)
                        elif (north_tile.value & df.Tile.WALL.value
                              and south_tile.value & df.Tile.WALL.value
                              and east_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NSE, i)
                        # combinations of 2
                        elif (east_tile.value & df.Tile.WALL.value
                              and west_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_EW, i)
                        elif (east_tile.value & df.Tile.WALL.value
                              and south_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_SE, i)
                        elif (east_tile.value & df.Tile.WALL.value
                              and north_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NE, i)
                        elif (north_tile.value & df.Tile.WALL.value
                              and south_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NS, i)
                        elif (north_tile.value & df.Tile.WALL.value
                              and west_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_NW, i)
                        elif (south_tile.value & df.Tile.WALL.value
                              and west_tile.value & df.Tile.WALL.value):
                            self.paint(df.Tile.WALL_SW, i)
                        # just one
                        elif east_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_E, i)
                        elif west_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_W, i)
                        elif north_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_N, i)
                        elif south_tile.value & df.Tile.WALL.value:
                            self.paint(df.Tile.WALL_S, i)
                        # none
                        else:
                            self.paint(df.Tile.WALL_C, i)
        type = self.map.levels[self.current_level][yTile*df.ARENA_WIDTH+xTile]
        if type == df.Tile.WALL:
            i = yTile*df.ARENA_WIDTH+xTile
            self.map.levels[self.current_level][i] = df.Tile.WALL_C
            tile = self.GetTile(df.Tile.WALL_C)
            self.images[self.current_level].Paste(tile, xTile*self.tile_w, yTile*self.tile_h)

    @benchmark
    def makeSky(self, floorType, x, y, z):
        if z > 7:
            return
        ignoreOthers = (floorType == df.Tile.EMPTY)
        openTypeFromFloor = {
            df.Tile.CHASM: df.Tile.OPEN_DGRAY,
            df.Tile.WATER: df.Tile.OPEN_WATER,
            df.Tile.WATER_SOURCE: df.Tile.OPEN_WATER,
            df.Tile.LAVA: df.Tile.OPEN_LAVA,
            df.Tile.GRASS: df.Tile.OPEN_GREEN,
            df.Tile.TREE: df.Tile.OPEN_BROWN,
            df.Tile.SAND: df.Tile.OPEN_YELLOW,
            df.Tile.SOIL: df.Tile.OPEN_BROWN,
            df.Tile.OPEN_DGRAY: df.Tile.SKY,
            df.Tile.OPEN_GRAY: df.Tile.SKY,
            df.Tile.OPEN_BLUE: df.Tile.SKY,
            df.Tile.OPEN_CYAN: df.Tile.SKY,
            df.Tile.OPEN_RED: df.Tile.SKY,
            df.Tile.OPEN_GREEN: df.Tile.SKY,
            df.Tile.OPEN_YELLOW: df.Tile.SKY,
            df.Tile.OPEN_BROWN: df.Tile.SKY,
            df.Tile.OPEN_WATER: df.Tile.OPEN_BLUE,
            df.Tile.OPEN_LAVA: df.Tile.OPEN_RED,
            df.Tile.OPEN_LRAMP: df.Tile.OPEN_RED,
            df.Tile.OPEN_WRAMP: df.Tile.OPEN_BLUE,
            df.Tile.OPEN_WALL: df.Tile.OPEN_GRAY,
            df.Tile.EMPTY: df.Tile.SKY,
            df.Tile.SKY: df.Tile.SKY,
            df.Tile.FLOOR: df.Tile.OPEN_GRAY,
            df.Tile.FORTIFICATION: df.Tile.OPEN_GRAY,
            df.Tile.OPEN_RAMP: df.Tile.OPEN_GRAY,
            df.Tile.RAMP: df.Tile.OPEN_RAMP,
            df.Tile.WATER_RAMP: df.Tile.OPEN_WRAMP,
            df.Tile.LAVA_RAMP: df.Tile.OPEN_LRAMP,
        }
        skyTypeFromOpen = {
            df.Tile.OPEN_LAVA: df.Tile.OPEN_RED,
            df.Tile.OPEN_WALL: df.Tile.OPEN_GRAY,
            df.Tile.OPEN_WATER: df.Tile.OPEN_BLUE,
            df.Tile.OPEN_LRAMP: df.Tile.OPEN_RED,
            df.Tile.OPEN_WRAMP: df.Tile.OPEN_BLUE,
            df.Tile.OPEN_RAMP: df.Tile.OPEN_GRAY,
        }
        if floorType in openTypeFromFloor.keys():
            overType = openTypeFromFloor[floorType]
        else:
            overType = df.Tile.OPEN_WALL  # wall types
        if overType in skyTypeFromOpen.keys():
            skyType = skyTypeFromOpen[overType]
        else:
            skyType = df.Tile.SKY
        if (self.map.levels[z+1][y*144+x].value & df.Tile.EMPTY.value
           or (not(self.map.levels[z+1][y*144+x].value & df.Tile.EMPTY.value)
               and ignoreOthers)):
            self.pushTilePaintedOp(x, y, z+1, newtype=overType)
            self.map.levels[z+1][y*144+x] = overType
            overTile = self.GetTile(overType)
            self.images[z+1].Paste(overTile, x*self.tile_w, y*self.tile_h)
            if z < 7 and self.map.levels[z+2][y*144+x].value & df.Tile.EMPTY.value:
                self.pushTilePaintedOp(x, y, z+2, newtype=skyType)
                self.map.levels[z+2][y*144+x] = skyType
                skyTile = self.GetTile(skyType)
                self.images[z+2].Paste(skyTile, x*self.tile_w, y*self.tile_h)
            if z < 6 and self.map.levels[z+3][y*144+x].value & df.Tile.EMPTY.value:
                self.pushTilePaintedOp(x, y, z+3, newtype=df.Tile.SKY)
                self.map.levels[z+3][y*144+x] = df.Tile.SKY
                skyTile = self.GetTile(df.Tile.SKY)
                self.images[z+3].Paste(skyTile, x*self.tile_w, y*self.tile_h)

    def paint(self, tiletype, i):
        x = i % df.ARENA_WIDTH
        y = (i - x) // df.ARENA_HEIGHT
        z = self.current_level
        self.map.levels[z][i] = tiletype
        tile = self.GetTile(tiletype)
        self.images[self.current_level].Paste(tile, x*self.tile_w, y*self.tile_h)
        self.makeSky(tiletype, x, y, self.current_level)

    def pushTilePaintedOp(self, x, y, z, newtype=None, oldtype=None, ):
        if newtype is None and oldtype:
            newtype = self.map.levels[z][y*df.ARENA_WIDTH+x]
        if newtype and oldtype is None:
            oldtype = self.map.levels[z][y*df.ARENA_WIDTH+x]
        op = TilePaintedOp(self, newtype, oldtype, z, y*df.ARENA_WIDTH+x)
        self.handler.push(op)
        self.menubar.GetMenu(1).Enable(ID_UNDO, True)

    @benchmark
    def onUndo(self, e):
        self.handler.undoGroup()
        self.redrawMainPanel()
        if self.handler.nothingToUndo():
            self.menubar.GetMenu(1).Enable(ID_UNDO, False)
        self.menubar.GetMenu(1).Enable(ID_REDO, True)
        # print("done : ", self.handler.done)
        # print("undone :", self.handler.undone)

    def onRedo(self, e):
        self.handler.redoGroup()
        self.redrawMainPanel()
        if self.handler.nothingToDo():
            self.menubar.GetMenu(1).Enable(ID_REDO, False)
        self.menubar.GetMenu(1).Enable(ID_UNDO, True)
        # print("done : ", self.handler.done)
        # print("undone :", self.handler.undone)

    @benchmark
    def GetTile(self, type):
        tilenumber = choice(tileFromType[type])
        key = type.name + '_' + str(tilenumber)
        if key in self.tiles.keys():
            newTile = self.tiles[key].Copy()
        else:
            x = tilenumber % TILENUMBER_X
            y = (tilenumber - x) // TILENUMBER_Y
            # print("x =", x, ", y =", y)
            rect = wx.Rect(x * self.tile_w, y * self.tile_h,
                           self.tile_w, self.tile_h)
            newTile = self.tileset.GetSubImage(rect)
            self.colorTile(newTile, type)
            self.tiles[key] = newTile.Copy()
        return newTile

    @benchmark
    def onNew(self, event):
        self.map = df.Map()
        self.loadArena()
        self.arenaChanged = True

    def loadArena(self, map=""):
        self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
        self.sb.g.SetValue(0)
        if map == "":
            self.sb.g.SetRange(19)
        else:
            print("loading map from "+map+"...")
            self.sb.g.SetRange(25)
            self.map = df.Map(map)
            self.current_file = map
            self.sb.incrementGauge(6)
            print("map loaded")
        self.loadImages()
        self.loadMiniatures()
        self.loadMainImg(4)
        self.current_level = 4
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.sb.g.SetValue(0)

    @benchmark
    def onNewDefault(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
        self.loadArena(self.config["default_arena"])
        self.map.file = None
        self.arenaChanged = True

    def createToolBar(self):
        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((16, 16))
        print("loading toolbar...")
        # opening or creating file
        self.toolbar.AddTool(ID_TOOL_LOAD, "Ouvrir",
                             wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN),
                             "Ouvrir depuis un fichier")
        self.toolbar.AddTool(ID_TOOL_NEW, "Nouveau",
                             wx.ArtProvider.GetBitmap(wx.ART_NEW),
                             "Nouvelle arène par défaut")
        self.toolbar.AddSeparator()
        # tile painting
        tiles = [df.Tile.CHASM, df.Tile.FLOOR, df.Tile.RAMP, df.Tile.FORTIFICATION,
                 df.Tile.WATER, df.Tile.WATER_SOURCE, df.Tile.WATER_RAMP,
                 df.Tile.LAVA, df.Tile.LAVA_RAMP, df.Tile.GRASS, df.Tile.TREE,
                 df.Tile.SAND, df.Tile.SOIL, df.Tile.WALL, df.Tile.EMPTY]
        for i, tiletype in enumerate(tiles):
            print("loading "+tiletype.name+"...")
            tile = self.GetTile(tiletype)
            if tile.GetWidth() >= 16 or tile.GetHeight() >= 16:
                tile.Rescale(16, 16)
            else:
                tile.Rescale(2*self.tile_w, 2*self.tile_h)
            help = tiletype.name.lower()
            Nid = wx.NewId()
            self.toolbar.AddTool(Nid, "tool", tile.ConvertToBitmap(), help,
                                 kind=wx.ITEM_CHECK)
            self.toolbar.Bind(wx.EVT_TOOL, self.onSelectToolTile, id=Nid)
            if help == "empty":  # empty is the pen's default value
                self.toolbar.ToggleTool(Nid, True)
        self.toolbar.AddSeparator()
        # tools
        penimg = wx.Image(IMG+"pen.png", wx.BITMAP_TYPE_PNG)
        self.toolbar.AddTool(ID_TOOL_SELECT_PEN, "Peindre une case",
                             penimg.ConvertToBitmap(), "Modifie les cases une à une",
                             wx.ITEM_CHECK)
        self.toolbar.ToggleTool(ID_TOOL_SELECT_PEN, True)
        label = wx.StaticText(self.toolbar, ID_TOOL_LABEL_PENSIZE,
                              "Largeur du pinceau :")
        cb = wx.ComboBox(self.toolbar, ID_TOOL_PENSIZE, "1",
                         choices=[str(i)for i in range(1, 6)],
                         style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.toolbar.AddControl(label)
        self.toolbar.AddControl(cb, label="Largeur du pinceau : ")
        selimg = wx.Image(IMG+"icon_selection.png", wx.BITMAP_TYPE_PNG)
        self.toolbar.AddTool(ID_TOOL_RECT_SEL, "Sélectionner un rectangle",
                             selimg.ConvertToBitmap(),
                             "Sélectionner une zone rectangulaire", wx.ITEM_CHECK)
        print("toolbar loaded.")
        self.toolbar.Bind(wx.EVT_TOOL, self.onLoad, id=ID_TOOL_LOAD)
        self.toolbar.Bind(wx.EVT_TOOL, self.onNewDefault, id=ID_TOOL_NEW)
        self.toolbar.Bind(wx.EVT_TOOL, self.onSelectBrushType, id=ID_TOOL_SELECT_PEN)
        self.toolbar.Bind(wx.EVT_TOOL, self.onSelectBrushType, id=ID_TOOL_RECT_SEL)
        self.toolbar.Bind(wx.EVT_COMBOBOX, self.onPenSize, id=ID_TOOL_PENSIZE)
        self.toolbar.Realize()

    def onSelectBrushType(self, event):
        id = event.Id
        if id == ID_TOOL_SELECT_PEN:
            self.brushes[self.active_brush].type = BrushType.PEN
            self.toolbar.EnableTool(ID_TOOL_LABEL_PENSIZE, True)
            self.toolbar.EnableTool(ID_TOOL_PENSIZE, True)
            self.toolbar.ToggleTool(ID_TOOL_RECT_SEL, False)
        elif id == ID_TOOL_RECT_SEL:
            self.brushes[self.active_brush].type = BrushType.PAINT_RECTANGLE
            self.toolbar.EnableTool(ID_TOOL_LABEL_PENSIZE, False)
            self.toolbar.EnableTool(ID_TOOL_PENSIZE, False)
            self.toolbar.ToggleTool(ID_TOOL_SELECT_PEN, False)

    def onPenSize(self, event):
        print("ID_TOOL_PENSIZE =", ID_TOOL_PENSIZE)
        for i in range(self.toolbar.GetToolsCount()):
            tool = self.toolbar.GetToolByPos(i)
            print(tool.GetId(), tool.GetLabel())
            if tool.GetId() == ID_TOOL_PENSIZE:
                choice = tool.GetControl().GetStringSelection()
                self.brushes[self.active_brush].penSize = int(choice)

    def onSelectToolTile(self, event):
        tiles = {"chasm": df.Tile.CHASM, "floor": df.Tile.FLOOR,
                 "ramp": df.Tile.RAMP, "fortification": df.Tile.FORTIFICATION,
                 "water": df.Tile.WATER, "water_source": df.Tile.WATER_SOURCE,
                 "water_ramp": df.Tile.WATER_RAMP, "lava": df.Tile.LAVA,
                 "lava_ramp": df.Tile.LAVA_RAMP, "grass": df.Tile.GRASS,
                 "tree": df.Tile.TREE, "sand": df.Tile.SAND, "soil": df.Tile.SOIL,
                 "wall": df.Tile.WALL, "empty": df.Tile.EMPTY}
        print("id =", event.Id)
        toolText = self.toolbar.GetToolShortHelp(event.Id)
        self.brushes[self.active_brush].tileLeftClick = tiles[toolText]
        for i in range(self.toolbar.GetToolsCount()-4):
            tool = self.toolbar.GetToolByPos(i)
            if tool.IsButton() and tool.GetKind() == wx.ITEM_CHECK:
                # print(tool.GetShortHelp(), tool.GetId(), tool.IsToggled())
                if tool.GetId() != event.Id and tool.IsToggled():
                    self.toolbar.ToggleTool(tool.GetId(), False)

    def onChangeLevelUp(self, event):
        if self.map is not None and self.current_level < 8:
            self.loadMiniatures(i=self.current_level)
            self.current_level += 1
            self.loadMainImg(self.current_level)

    def onChangeLevelDown(self, event):
        if self.map is not None and self.current_level > 0:
            self.loadMiniatures(i=self.current_level)
            self.current_level -= 1
            self.loadMainImg(self.current_level)

    def onAbout(self, event):
        message = '''ArenaEditor v0.1\n\n\
Ce programme a pour but de permettre la modification des fichiers d'arène de \
Dwarf Fortress par l'intermédiaire d'une interface graphique.\n\nActuellement \
en développement, ses fonctionnalités ne sont pas toutes implémentées.'''
        dlg = wx.MessageDialog(None, message, caption="A propos d'ArenaEditor",
                               style=wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def onToolConfig(self, event):
        print(ConfigFrame.count)
        if ConfigFrame.count < 1:
            ConfigFrame(self, "Paramètres").Show()

    def onEditColorScheme(self, event):
        if EditColorFrame.count < 1:
            EditColorFrame(self, "Editeur de palette").Show()

    def loadRessources(self, loadColors=True):
        if loadColors:
            dfColors = df.loadColorScheme(self.config["colorscheme"]).items()
            self.colorscheme = {key: wx.Colour(value) for key, value in dfColors}
        self.tileset = wx.Image(self.config["tileset"], wx.BITMAP_TYPE_ANY)
        self.tile_w = self.tileset.GetWidth() // TILENUMBER_X
        self.tile_h = self.tileset.GetHeight() // TILENUMBER_Y
        self.loadMainTiles()

    def onLoadTileset(self, event):
        dlg = wx.FileDialog(self, "Choisissez un fichier", "", "",
                            wildcard="fichiers PNG ou BMP (*.png;*.bmp)|*.png;*.bmp",
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
            self.config["tileset"] = file
            self.tileset = wx.Image(file, wx.BITMAP_TYPE_ANY)
            self.tile_w = self.tileset.GetWidth() // TILENUMBER_X
            self.tile_h = self.tileset.GetHeight() // TILENUMBER_Y
            if self.map is not None:
                self.loadRessources()
                self.loadArena()
                self.arenaChanged = False
        dlg.Destroy()

    def onLoadColorscheme(self, event):
        dlg = wx.FileDialog(self, "Choisissez un fichier", "", "",
                            wildcard="fichiers texte (*.txt)|*.txt",
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
            self.config["colorscheme"] = CWD+file
            dfColors = df.loadColorScheme(file).items()
            self.colorscheme = {key: wx.Colour(value)for key, value in dfColors}
            if self.map is not None:
                self.loadRessources()
                self.loadArena()
                self.arenaChanged = False

    @benchmark
    def loadImages(self, i=None):
        if i is not None:
            img = self.tileListToImage(self.map.levels[i].types)
            data = img.GetData()
            self.images[i] = wx.Image(self.tile_w*144, self.tile_h*144, data)
        else:
            self.images.clear()
            self.sb.count = 0
            print("starting to load the images...")
            for i in range(0, 9):
                img = self.tileListToImage(self.map.levels[i].types)
                data = img.GetData()
                img = wx.Image(self.tile_w*144, self.tile_h*144, data)
                self.images.append(img)
                self.sb.incrementGauge(2)
            print("all images loaded.")

    @benchmark
    def colorTile(self, tile, tiletype):
        w = tile.GetWidth()
        h = tile.GetHeight()
        for i in range(w*h):
            x = i % w
            y = (i-x)//w
            r = tile.GetRed(x, y)
            g = tile.GetGreen(x, y)
            b = tile.GetBlue(x, y)
            color = wx.Colour(r, g, b)
            a = 255
            mask = wx.Colour(255, 0, 255)  # MAGENTA is default mask for .bmp files
            if tile.HasAlpha() or tile.HasMask():
                mask = tile.GetOrFindMaskColour()
                if tile.HasAlpha(): a = tile.GetAlpha(x, y)
            matColor = self.colorscheme[choice(colorMaterial[tiletype]).name]
            # matColor is a wx.Colour
            if (a == 0 or color == mask):  # pixel is transparent
                r, g, b, a = self.colorscheme[Colour.BLACK.name]  # default bg color
                tile.SetRGB(x, y, r, g, b)
            else:
                r &= matColor.Red()
                g &= matColor.Green()
                b &= matColor.Blue()
                tile.SetRGB(x, y, r, g, b)
        return tile

    @benchmark
    def tileListToImage(self, tiles):
        """ Convert a list of tiles to an image.

        Load a tileset from a .bmp or .png and construct an image from the tiles
        corresponding to the input list.
        notes :
        # trees are evil """
        wx.Image.AddHandler(wx.PNGHandler())
        image = wx.Image(self.tile_w*df.ARENA_WIDTH, self.tile_h*df.ARENA_HEIGHT)
        for i, tiletype in enumerate(tiles):
            tile = self.GetTile(tiletype)
            # now that the tile is colored, we just paste it on the target image
            xi = i % df.ARENA_WIDTH
            yi = (i-xi) // df.ARENA_WIDTH
            image.Paste(tile, xi*self.tile_w, yi*self.tile_h)
            # then move on to the next tiletype
        return image

    @benchmark
    def loadMainTiles(self):
        self.tiles = {}
        tiles = [df.Tile.CHASM, df.Tile.FLOOR, df.Tile.RAMP, df.Tile.FORTIFICATION,
                 df.Tile.WATER, df.Tile.WATER_SOURCE, df.Tile.WATER_RAMP,
                 df.Tile.LAVA, df.Tile.LAVA_RAMP, df.Tile.GRASS, df.Tile.TREE,
                 df.Tile.SAND, df.Tile.SOIL, df.Tile.WALL, df.Tile.EMPTY]
        for tiletype in tiles:
            tilenumber = choice(tileFromType[tiletype])
            key = tiletype.name+'_'+str(tilenumber)
            if key not in self.tiles.keys():
                print("computing tile for", key, "...")
                x = tilenumber % TILENUMBER_X
                y = (tilenumber-x) // TILENUMBER_X
                rect = wx.Rect(x*self.tile_w, y*self.tile_h, self.tile_w, self.tile_h)
                tile = self.tileset.GetSubImage(rect)
                self.colorTile(tile, tiletype)
                self.tiles[key] = tile.Copy()

    @benchmark
    def loadMainImg(self, image):
        self.current_level = image
        self.redrawMainPanel()
        self.sb.incrementGauge(2)

    @benchmark
    def loadMiniatures(self, event=None, i=None):
        if i is not None:  # reload just a level
            data = self.images[i].GetData()
            img = wx.Image(self.images[i].GetSize(), data).Rescale(144, 144)
            self.miniatures[i] = img
        else:  # we reload everything
            print("starting to create the bitmaps...")
            self.miniatures.clear()
            for i in range(0, 9):
                data = self.images[i].GetData()
                img = wx.Image(self.images[i].GetSize(), data).Rescale(144, 144)
                self.miniatures.append(img)
                self.sb.incrementGauge(2)
        # now we redraw all the bitmaps on the panel
        print("bitmaps created.")
        # freeze the window so the user don't see the StaticBitmaps being replaced
        self.Freeze()
        self.imgPanel.DestroyChildren()
        # then we can draw the new ones
        print("adding the bitmaps to the image panel...")
        sizer = wx.BoxSizer(wx.VERTICAL)
        for i, bmp in enumerate(self.miniatures):
            id = wx.NewId()
            item = wx.StaticBitmap(self.imgPanel, id, bmp.ConvertToBitmap())
            sizer.Add(item, 0, wx.TOP | wx.ALIGN_CENTER, 5)
            item.Bind(wx.EVT_LEFT_DOWN, self.onClickMiniature, id=id)
        self.imgPanel.SetSizer(sizer)
        self.imgPanel.SetupScrolling()
        self.Thaw()
        print("all done!")

    def onClickMiniature(self, event):
        if self.map is not None:
            print("===LeftDown Event on imgPanel===")
            y = event.GetPosition().y
            id = event.GetId()
            children = self.imgPanel.GetChildren()
            for child in children:
                if child.GetId() == id:
                    pos = child.GetPosition()
                    y = self.imgPanel.CalcUnscrolledPosition(pos).y
                    i = (y-5) // 149
                    print("pos :", pos, "relates to images n°"+str(i))
                    if i != self.current_level:
                        self.loadMainImg(i)
                        self.current_level = i
                        # modifying the miniatures during this event's processing
                        # causes a crash, so we queue an event to do the thing
                        # self.loadMiniatures is the event's handler
                        self.QueueEvent(NewEventMiniatures())
        event.Skip()

    def onZoomIn(self, event):
        # dieu que c'est laid, changer ça quand j'arriverai à réfléchir
        if self.scale < 0.25: self.scale = 0.25
        elif self.scale < 0.5: self.scale = 0.5
        elif self.scale < 0.67: self.scale = 0.67
        elif self.scale < 1.0: self.scale = 1.0
        elif self.scale < 1.5: self.scale = 1.5
        elif self.scale < 2.0: self.scale = 2.0
        elif self.scale < 2.5: self.scale = 2.5
        elif self.scale < 3.0: self.scale = 3.0
        strScale = str(self.scale*100)
        self.sb.SetStatusText(strScale[:strScale.index('.')]+"%", 2)
        self.sb.slider.SetValue(int(self.scale*100))
        self.redrawMainPanel(True)
        print("buffer size: ", self.buffer.GetSize())
        print("tmp size: ", self.mainBmp.GetSize())

    def onZoomOut(self, event):
        # idem, honte à moi
        if self.scale <= 0.5: self.scale = 0.25
        elif self.scale <= 0.67: self.scale = 0.5
        elif self.scale <= 1.0: self.scale = 0.67
        elif self.scale <= 1.5: self.scale = 1.0
        elif self.scale <= 2.0: self.scale = 1.5
        elif self.scale <= 2.5: self.scale = 2.0
        elif self.scale <= 3.0: self.scale = 2.5
        strScale = str(self.scale*100)
        self.sb.SetStatusText(strScale[:strScale.index('.')]+"%", 2)
        self.sb.slider.SetValue(int(self.scale*100))
        self.redrawMainPanel(True)
        print("buffer size: ", self.buffer.GetSize())
        print("tmp size: ", self.mainBmp.GetSize())

    def onpainttest(self, event):
        dc = wx.BufferedPaintDC(self.mainPanel, self.buffer, wx.BUFFER_VIRTUAL_AREA)

    @benchmark
    def onLoad(self, event):
        dlg = wx.FileDialog(self, "Chose a file", "", "",
                            wildcard="text files (*.txt)|*.txt",
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
            self.loadArena(file)
            self.arenaChanged = False
        dlg.Destroy()

    @benchmark
    def onSaveAs(self, event=None):
        if self.map is None:
            dlg = wx.MessageDialog(None, "Il n'y a aucune arène de chargée!")
            dlg.ShowModal()
        else:
            dlg = wx.FileDialog(None, "Save file", self.config["save_directory"],
                                "arena.txt", wildcard="text files (*.txt)|*.txt",
                                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if dlg.ShowModal() == wx.ID_OK:
                file = dlg.GetPath()
                print("saving arena to " + file)
                self.map.saveToTxt(file)
                self.arenaChanged = False

    @benchmark
    def onSave(self, event=None):
        if self.map is None:
            dlg = wx.MessageDialog(None, "Il n'y a aucune arène de chargée!")
            dlg.ShowModal()
        else:
            if self.current_file is not None:
                self.map.saveToTxt(self.current_file)
            else:
                self.onSaveAs()
            self.arenaChanged = False

    def onSaveImage(self, event=None):
        print(self.config["save_directory"])
        if self.map is None:
            dlg = wx.MessageDialog(None, "Il n'y a aucune arène de chargée!")
            dlg.ShowModal()
        else:
            filename = self.config["save_directory"] + "/image.png"
            self.images[self.current_level].SaveFile(filename, wx.BITMAP_TYPE_PNG)

    def onSaveAllImages(self, event):
        if self.map is None:
            dlg = wx.MessageDialog(None, "Il n'y a aucune arène de chargée!")
            dlg.ShowModal()
        else:
            dlg = wx.DirDialog(None, "Directory", self.config["save_directory"],
                               style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
            if dlg.ShowModal() == wx.ID_OK:
                dir = os.getcwd()
                os.chdir(dlg.GetPath())
                for i, img in enumerate(self.images):
                    img.SaveFile("level n°"+str(i-4)+".png", wx.BITMAP_TYPE_PNG)
                os.chdir(dir)

    def onClose(self, event):
        if self.arenaChanged:
            msg = "Il y a des modifications non enregistrées. Voulez-vous les enregistrer?"
            dlg = wx.MessageDialog(self, msg, "Modifications non enregistrées",
                                   style=wx.YES_NO | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_YES:
                self.onSave()
        print("closing")
        if __PROFILE__: profile()
        self.Destroy()


if __name__ == "__main__":
    app = wx.App()
    window = MyFrame(None, "Arena Editor")
    app.MainLoop()
