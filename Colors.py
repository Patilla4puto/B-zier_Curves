class Colors:
    colors=["#030508",
    "#00be00",
    "#936862",
    "#147a6f",
    "#f2c8a0",
    "#fcc5a8",
    "#704e38",
    "#00c000",
    "#1155ff",
    "#ff5511",
    "#dbe5f1",
    "#8db3e2",
    "#88ddbb",
    "#f2dcdb",
    "#ff22dd",
    "#114400",
    "#552233",
    "#523140",
    "#e3d3f0",
    "#a5b2c8",
    "#182c25",
    "#2c4c3b",
    "#004242",
    "#f4dcdc",
    "#4d8679",
    "#006f62",
    "#a2cab9",
    "#00584e",
    "#faefd3",
    "#9d867e",
    "#ebdfd4",
    "#cbcba9",
    "#005758",
    "#ce9a84",
    "#e54f6e",
    "#ccc6ee"]
    index = 0
    def __init__(self):
        pass
    def getColor(self):
        if self.index == 36:
            self.index=0
            return(self.colors[self.index])
        else:
            aux= self.index
            self.index +=1
            return(self.colors[aux])
    def resetIndex(self):
        self.index=0
