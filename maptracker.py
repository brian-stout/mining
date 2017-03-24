class MapTracker:
    def __init__(self, mapId, graph):
        self.mapId = mapId
        self.graph = graph
        self.zerg = {}
        self.mineralsMined = 0

    def add_zerg(self, zerg):
        self.zerg[id(z)] = zerg

    def add_minerals(self, minerals):
        self.mineralsMined += minerals

    def check_if_fully_mined(self):
        if self.mineralsMined >= 135:
            return True
        else:
            return False
        
