"""classes and functions for conversion of df files to usable data

functions:
    loadColorScheme(filename)
    saveColorScheme(colors,filename)

classes:
    Tile : enum for tile types
    ZLevel
    Map

notes:

                            character      tile           colours
        empty                 '# ',          0          see d_init.txt
        chasm                 'C',          35          DGRAY, BLACK
        floor                 '.',          43          LGRAY, BLACK
        wall                  'P',          79          LGRAY, BLACK
        ramp                  'R',          30          LGRAY, BLACK
        fortification         'F',          206         LGRAY, BLACK
        water source          '+',          247         CYAN, BLACK
        water                 'W',          247         LBLUE, BLACK
        water+ramp            'w',          30          LBLUE, BLACK
        magma                 'L',          247         RED, BLACK
        magma+ramp            'l',          30          LRED, BLACK
        grass                 'g',      39,44,46,96     GREEN, BLACK
        tree                  'T',          79          BROWN, BLACK
        sand                  '~',        126,247       YELLOW|LRED, BLACK
        soil                  ','         126,247       BROWN, BLACK
        water+downramp        'dw'          31          LBLUE, BLACK
        lava+downramp         'dl'          31          RED, BLACK
        open1                 '# 1'         250         TILE BELOW,
        sky                   '# 2'         178         CYAN, BLACK
        openlava              '# L'         247         RED, BLACK
        openwater             '# W'         247
        walls (orientation):
        column                              79
        north                               79
        south                               79
        east                                79
        west                                79
        NS                                  186
        EW                                  205
        NE                                  201
        SE                                  200
        SW                                  187
        NW                                  188
        NSE                                 204
        NSW                                 185
        EWS                                 203
        EWN                                 202
        ALL                                 206

    #  open spaces : 178 if more than 1 levels above any kind of surface, 46(.)
       if one level with the colour depending of the one from the tile below.
    #                Depends on d_init.txt for additional inconvenience
    #  water : tiles above have the dark blue '~' (247),
    #  lava : tiles above are red '~' (247)
    #  walls : can be other tiles too, tile above has a floor
    #  ramps (+water/lava ramps) : tile above has a downward ramp
    #  trees : ouch. we'll start by using the pillar tile for the trunk

"""
from enum import Enum

from profiling import benchmark

# some constants
ARENA_WIDTH, ARENA_HEIGHT = 144, 144


class Tile(Enum):
    #  original tiles from the game's text file
    CHASM = 0x00
    FLOOR = 0x01
    RAMP = 0x02
    FORTIFICATION = 0x03
    WATER = 0x04
    WATER_SOURCE = 0x05
    WATER_RAMP = 0x06
    LAVA = 0x07
    LAVA_RAMP = 0x08
    GRASS = 0x09
    TREE = 0x0A
    SAND = 0x0B
    SOIL = 0x0C
    WALL = 0x80
    EMPTY = 0x40
    # both WALL and EMPTY are just temporary states.
    # Further process mark them with one of the following values, which are
    # deduced from the map's configuration.
    OPEN_GRAY = 0x41
    OPEN_DGRAY = 0x42
    OPEN_BLUE = 0x43
    OPEN_CYAN = 0x44
    OPEN_RED = 0x45
    OPEN_GREEN = 0x46
    OPEN_YELLOW = 0x47
    OPEN_BROWN = 0x48
    OPEN_WATER = 0x49
    OPEN_LAVA = 0x4A
    OPEN_LRAMP = 0x4B
    OPEN_WRAMP = 0x4C
    OPEN_RAMP = 0x4D
    OPEN_WALL = 0x4E
    SKY = 0x4F
    WALL_C = 0x81
    WALL_N = 0x82
    WALL_S = 0x83
    WALL_E = 0x84
    WALL_W = 0x85
    WALL_NS = 0x86
    WALL_NE = 0x87
    WALL_NW = 0x88
    WALL_SE = 0x89
    WALL_SW = 0x8A
    WALL_EW = 0x8B
    WALL_NSE = 0x8C
    WALL_NSW = 0x8D
    WALL_NEW = 0x8E
    WALL_SEW = 0x8F
    WALL_ALL = 0x90


TypeFromChar = {
    'C': [Tile.CHASM],
    '.': [Tile.FLOOR],
    'R': [Tile.RAMP],
    'F': [Tile.FORTIFICATION],
    '+': [Tile.WATER_SOURCE],
    'W': [Tile.WATER],
    'w': [Tile.WATER_RAMP],
    'L': [Tile.LAVA],
    'l': [Tile.LAVA_RAMP],
    'g': [Tile.GRASS],
    'T': [Tile.TREE],
    '~': [Tile.SAND],
    ',': [Tile.SOIL],
    'P': [Tile.WALL],
    '#': [Tile.EMPTY],
}


def loadColorScheme(filename):
    """Expect a file following the df format and return a dict of COLOR:(r,g,b)
        file format :
        [BLACK_R:0]
        [BLACK_G:0]
        [BLACK_B:0]
        (other colors)
    """
    colorscheme = {}
    print("loading colorscheme...")
    with open(filename, 'r') as file:
        pixels = []
        for line in file:
            if line[0] == '[':
                name = line.split(':')[0]
                value = line.split(':')[1]
                name = name[1:name.find('_')]
                value = value[:value.find(']')]
                pixels.append(int(value))
                if (len(pixels) == 3):
                    colorscheme[name] = (pixels[0], pixels[1], pixels[2])
                    pixels.clear()
    return colorscheme


def saveColorScheme(colors, filename):
    """Expect a dict of COLOR:value where value can be unpacked into a (r,g,b,a)
    tuple. Save it to a valid .txt file using the game's format."""
    string = ""
    for color, value in colors.items():
        r, g, b, a = value
        string += '[' + color.upper() + "_R:" + str(r) + "]\n"
        string += '[' + color.upper() + "_G:" + str(g) + "]\n"
        string += '[' + color.upper() + "_B:" + str(b) + "]\n"
    with open(filename, 'w') as file:
        file.write(string)


class ZLevel:
    def __init__(self, level):
        # self.pixels = ['#']*144*144
        self.types = [Tile.SKY] * 144 * 144
        self.width = 144
        self.height = 144
        self.level = level

    def __getitem__(self, index):
        return self.types[index]

    def __setitem__(self, index, value):
        self.types[index] = value

    def loadFromTxt(self, string):
        # self.pixels = []
        self.types = []
        for char in string:
            # self.pixels += char
            self.types += TypeFromChar[char]

    def saveToTxt(self, filename):
        try:
            open(filename, 'r')
        except FileNotFoundError:
            open(filename, 'w')
        with open(filename, 'a') as file:
            strings = []
            tmp = ""
            for type in self.types:
                if type == Tile.FLOOR: tmp += '.'
                elif type == Tile.CHASM: tmp += 'C'
                elif type == Tile.RAMP: tmp += 'R'
                elif type == Tile.FORTIFICATION: tmp += 'F'
                elif type == Tile.WATER: tmp += 'W'
                elif type == Tile.WATER_SOURCE: tmp += '+'
                elif type == Tile.WATER_RAMP: tmp += 'w'
                elif type == Tile.LAVA: tmp += 'L'
                elif type == Tile.LAVA_RAMP: tmp += 'l'
                elif type == Tile.GRASS: tmp += 'g'
                elif type == Tile.TREE: tmp += 'T'
                elif type == Tile.SAND: tmp += '~'
                elif type == Tile.SOIL: tmp += ','
                elif type.value & Tile.EMPTY.value: tmp += '#'
                else: tmp += 'P'
            strings.append("Z={} (must leave this line here)\n".format(self.level))
            for i in range(144):
                strings.append("".join(tmp[144 * i:144*i + 144]) + '\n')
            # print(strings)
            string = "".join(strings)
            file.write(string)


class Map:
    def __init__(self, file=None):
        self.levels = []
        for i in range(-4, 5):
            self.levels.append(ZLevel(i))
        self.file = file
        if self.file is not None:
            self.loadFromTxt(file)
            self.processTileTypes()

    @benchmark
    def processTileTypes(self):
        for z in range(9):
            types = self.levels[z].types.copy()
            print("processing level ", z, "...")
            for i in range(len(types)):
                x = i % ARENA_WIDTH
                y = (i - x) // ARENA_WIDTH
                #  special cases are open spaces (EMPTY) and walls (WALL)
                if types[i] == Tile.WATER and z > 0:
                    underTile = self.levels[z-1].types[i]
                    if underTile == Tile.WATER_RAMP:
                        self.levels[z].types[i] = Tile.OPEN_WRAMP
                elif types[i] == Tile.LAVA and z > 0:
                    underTile = self.levels[z-1].types[i]
                    if underTile == Tile.LAVA_RAMP:
                        self.levels[z].types[i] = Tile.OPEN_LRAMP
                elif types[i] == Tile.EMPTY and z > 0:
                    # check the tile below and decide the current tile's colour
                    underTile = self.levels[z-1].types[i]
                    if underTile == Tile.LAVA_RAMP:
                        self.levels[z].types[i] = Tile.OPEN_LRAMP
                    elif underTile == Tile.WATER_RAMP:
                        self.levels[z].types[i] = Tile.OPEN_WRAMP
                    elif underTile == Tile.RAMP:
                        self.levels[z].types[i] = Tile.OPEN_RAMP
                    elif underTile == Tile.OPEN_LRAMP:
                        self.levels[z].types[i] = Tile.OPEN_RED
                    elif underTile == Tile.OPEN_WRAMP:
                        self.levels[z].types[i] = Tile.OPEN_BLUE
                    elif underTile == Tile.OPEN_RAMP:
                        self.levels[z].types[i] = Tile.OPEN_GRAY
                    elif (underTile == Tile.WATER or underTile == Tile.WATER_SOURCE
                          or underTile == Tile.OPEN_WRAMP):
                        self.levels[z].types[i] = Tile.OPEN_WATER
                    elif underTile == Tile.OPEN_WATER:
                        self.levels[z].types[i] = Tile.OPEN_BLUE
                    elif underTile == (Tile.LAVA or Tile.OPEN_LRAMP):
                        self.levels[z].types[i] = Tile.OPEN_LAVA
                    elif underTile == Tile.OPEN_LAVA:
                        self.levels[z].types[i] = Tile.OPEN_RED
                    elif underTile == Tile.CHASM:
                        self.levels[z].types[i] = Tile.OPEN_DGRAY
                    elif underTile == Tile.GRASS:
                        self.levels[z].types[i] = Tile.OPEN_GREEN
                    elif underTile == Tile.SAND:
                        self.levels[z].types[i] = Tile.OPEN_YELLOW
                    elif underTile == Tile.SOIL or underTile == Tile.TREE:
                        self.levels[z].types[i] = Tile.OPEN_BROWN
                    elif (underTile == Tile.OPEN_BLUE or underTile == Tile.OPEN_BROWN
                          or underTile == Tile.OPEN_CYAN or underTile == Tile.OPEN_DGRAY
                          or underTile == Tile.OPEN_GRAY or underTile == Tile.OPEN_GREEN
                          or underTile == Tile.OPEN_RED or underTile == Tile.OPEN_YELLOW
                          or underTile == Tile.SKY or underTile == Tile.EMPTY):
                        self.levels[z].types[i] = Tile.SKY
                    elif underTile.value & Tile.WALL.value:
                        self.levels[z].types[i] = Tile.FLOOR
                    else:
                        self.levels[z].types[i] = Tile.OPEN_GRAY
                elif types[i] == Tile.WALL:
                    # nine cases depending on the coordinates
                    # top-left corner
                    if (x == 0 and y == 0):
                        #  only the eastern and southern tiles are checked
                        east_tile = types[i+1]
                        south_tile = types[i+ARENA_WIDTH]
                        if east_tile == Tile.WALL and south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_SE
                        elif east_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_E
                        elif south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_S
                    # top right corner
                    elif x == ARENA_WIDTH-1 and y == 0:
                        # only the western and southern tiles are checked
                        west_tile = types[i-1]
                        south_tile = types[i+ARENA_WIDTH]
                        if west_tile == Tile.WALL and south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_SW
                        elif west_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_W
                        elif south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_S
                    # bottom right corner
                    elif x == ARENA_WIDTH-1 and y == ARENA_HEIGHT-1:
                        # only the western and northern tiles are checked
                        west_tile = types[i-1]
                        north_tile = types[i-ARENA_WIDTH]
                        if west_tile == Tile.WALL and north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_NW
                        elif west_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_W
                        elif north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_N
                    # bottom left corner
                    elif x == 0 and y == ARENA_HEIGHT-1:
                        # only the eastern and northern tiles are checked
                        east_tile = types[i+1]
                        north_tile = types[i-ARENA_WIDTH]
                        if east_tile == Tile.WALL and north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_NE
                        elif east_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_E
                        elif north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_N
                    # now we check for the four borders
                    # northern border
                    elif y == 0:
                        # only the southern, eastern and western tiles are checked
                        east_tile = types[i+1]
                        west_tile = types[i-1]
                        south_tile = types[i+ARENA_WIDTH]
                        if (east_tile == Tile.WALL and west_tile == Tile.WALL
                           and south_tile == Tile.WALL):
                            self.levels[z].types[i] = Tile.WALL_SEW
                        elif east_tile == Tile.WALL and west_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_EW
                        elif east_tile == Tile.WALL and south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_SE
                        elif west_tile == Tile.WALL and south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_SW
                        elif west_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_W
                        elif east_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_E
                        elif south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_S
                    # eastern border
                    elif x == ARENA_WIDTH-1:
                        # only the northern, southern, and western tiles are checked
                        west_tile = types[i-1]
                        north_tile = types[i-ARENA_WIDTH]
                        south_tile = types[i+ARENA_WIDTH]
                        if (west_tile == Tile.WALL and north_tile == Tile.WALL
                                and south_tile == Tile.WALL):
                            self.levels[z].types[i] = Tile.WALL_NSW
                        elif west_tile == Tile.WALL and north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_NW
                        elif west_tile == Tile.WALL and south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_SW
                        elif south_tile == Tile.WALL and north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_NS
                        elif west_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_W
                        elif north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_N
                        elif south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_S
                    # southern border
                    elif y == ARENA_HEIGHT-1:
                        # only the northern, eastern and western tiles are checked
                        east_tile = types[i+1]
                        west_tile = types[i-1]
                        north_tile = types[i-ARENA_WIDTH]
                        if (east_tile == Tile.WALL and west_tile == Tile.WALL
                                and north_tile == Tile.WALL):
                            self.levels[z].types[i] = Tile.WALL_NEW
                        elif east_tile == Tile.WALL and west_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_EW
                        elif east_tile == Tile.WALL and north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_NE
                        elif west_tile == Tile.WALL and north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_NW
                        elif west_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_W
                        elif east_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_E
                        elif north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_N
                    # western border
                    elif x == 0:
                        # only the northern, southern, and eastern tiles are checked
                        east_tile = types[i+1]
                        north_tile = types[i-ARENA_WIDTH]
                        south_tile = types[i+ARENA_WIDTH]
                        if (east_tile == Tile.WALL and north_tile == Tile.WALL
                                and south_tile == Tile.WALL):
                            self.levels[z].types[i] = Tile.WALL_NSE
                        elif east_tile == Tile.WALL and north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_NE
                        elif east_tile == Tile.WALL and south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_SE
                        elif south_tile == Tile.WALL and north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_NS
                        elif east_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_E
                        elif north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_N
                        elif south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_S
                    # finally, the generic case
                    else:
                        east_tile = types[i+1]
                        west_tile = types[i-1]
                        north_tile = types[i-ARENA_WIDTH]
                        south_tile = types[i+ARENA_WIDTH]
                        # all four
                        if (east_tile == Tile.WALL and west_tile == Tile.WALL
                                and north_tile == Tile.WALL
                                and south_tile == Tile.WALL):
                            self.levels[z].types[i] = Tile.WALL_ALL
                        # combinations of 3
                        elif (east_tile == Tile.WALL and west_tile == Tile.WALL
                                and north_tile == Tile.WALL):
                            self.levels[z].types[i] = Tile.WALL_NEW
                        elif (east_tile == Tile.WALL and west_tile == Tile.WALL
                                and south_tile == Tile.WALL):
                            self.levels[z].types[i] = Tile.WALL_SEW
                        elif (north_tile == Tile.WALL and south_tile == Tile.WALL
                                and west_tile == Tile.WALL):
                            self.levels[z].types[i] = Tile.WALL_NSW
                        elif (north_tile == Tile.WALL and south_tile == Tile.WALL
                                and east_tile == Tile.WALL):
                            self.levels[z].types[i] = Tile.WALL_NSE
                        # combinations of 2
                        elif east_tile == Tile.WALL and west_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_EW
                        elif east_tile == Tile.WALL and south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_SE
                        elif east_tile == Tile.WALL and north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_NE
                        elif north_tile == Tile.WALL and south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_NS
                        elif north_tile == Tile.WALL and west_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_NW
                        elif south_tile == Tile.WALL and west_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_SW
                        # just one
                        elif east_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_E
                        elif west_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_W
                        elif north_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_N
                        elif south_tile == Tile.WALL:
                            self.levels[z].types[i] = Tile.WALL_S
                        # none
                        else: self.levels[z].types[i] = Tile.WALL_C

    @benchmark
    def loadFromTxt(self, filename):
        self.file = filename
        Zlevel_string = []
        levels_correspondances = {'Z=-4': self.levels[0], 'Z=-3': self.levels[1],
                                  'Z=-2': self.levels[2], 'Z=-1': self.levels[3],
                                  'Z=0 ': self.levels[4], 'Z=1 ': self.levels[5],
                                  'Z=2 ': self.levels[6], 'Z=3 ': self.levels[7],
                                  'Z=4 ': self.levels[8],
                                  }
        temp = []
        with open(filename, 'r') as file:
            i = 0
            for line in file:
                if line[:4] in levels_correspondances.keys():

                    temp = file.read(145*144).replace('\n', '')
                    Zlevel_string.append(temp)
                    i += 1
        for i in range(0, 9):
            self.levels[i].loadFromTxt(Zlevel_string[i])

    @benchmark
    def saveToTxt(self, filename):
        open(filename, 'w').close()
        for level in self.levels:
            level.saveToTxt(filename)
