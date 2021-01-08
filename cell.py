import random
import constants as const


class Cell:
    """
    Class representing a cell int he EchoSystem
    """
    def __init__(self, echoSystem, coordinates, cellType):
        """
        Init function for class Cell
        """
        self.echoSystem = echoSystem
        self.coordinates = coordinates                              # The location of the cell
        self.type = cellType                                        # Cell type (sea, forest etc.)
        self.windDirection = random.choice(const.WIND_DIRECTIONS)   # Wind direction (north, south-west, etc)
        self.pollution = const.INIT_POLLUTION                       # Pollution rate in the cell
        self.neighbors = {}                                         # the neighbors and their locations

        # A glacier is created with temp -20, sea level height and 10 winds speed
        if self.type == "glacier":
            self.temperature = const.GLACIER_TEMP
            self.height = "sea level"
            self.windSpeed = 10

        # A sea is created with sea level height and 39 wind speed
        elif self.type == "sea":
            self.height = "sea level"
            self.temperature = const.HEIGHTS_TEMP[self.height]
            self.windSpeed = 30

        # All other cell types are created at random heights and 20 wind speed
        else:
            self.height = random.choice(const.HEIGHTS)
            self.temperature = const.HEIGHTS_TEMP[self.height]
            self.windSpeed = 20

        self.clouds = random.choice([True, False])
        self.rain = False
        if self.clouds == "clouds":
            self.rain = random.choice([True, False])

        # These variables are storing the cell changes
        self.nextType = self.type
        self.nextWindSpeed = self.windSpeed
        self.nextWindDirection = self.windDirection
        self.nextPollution = self.pollution
        self.nextTemperature = self.temperature
        self.nextClouds = self.clouds
        self.nextRain = self.rain

    def updateNeighbors(self):
        """
        Updated neighbors dict.
        The world is circular (the north continues to the south, the east continues to the west).
        """
        row, col = self.coordinates
        if row > 0:
            self.neighbors["north"] = self.echoSystem.world[row-1][col]
        else:
            self.neighbors["north"] = self.echoSystem.world[const.WORLD_SIZE-1][col]

        if col > 0:
            self.neighbors["west"] = self.echoSystem.world[row][col-1]
        else:
            self.neighbors["west"] = self.echoSystem.world[row][const.WORLD_SIZE-1]

        if row < const.WORLD_SIZE-1:
            self.neighbors["south"] = self.echoSystem.world[row+1][col]
        else:
            self.neighbors["south"] = self.echoSystem.world[0][col]

        if col < const.WORLD_SIZE-1:
            self.neighbors["east"] = self.echoSystem.world[row][col + 1]
        else:
            self.neighbors["east"] = self.echoSystem.world[row][0]

    def calcChanges(self):
        """
        Calculate the changes in the cells.
        """

        if self.type == "city":
            self.updateCity()

        elif self.type == "forest":
            self.updateForest()

        elif self.type == "glacier":
            self.updateGlacier()

        if self.type == "sea":
            self.updateSea()

        if self.rain:
            self.updateRain()

        self.updatePollution()
        self.updateWind()

    def applyChanges(self):
        """
        Update the changes that were calculated.
        """
        self.type = self.nextType
        self.windSpeed = self.nextWindSpeed
        self.windDirection = self.nextWindDirection
        self.pollution = self.nextPollution
        self.temperature = self.nextTemperature
        self.rain = self.nextRain
        self.clouds = self.nextClouds

    def updateCity(self):
        """
        City increases pollution by 5%
        """
        self.increasePollution(5)

    def updatePollution(self):
        """
        If pollution in cell is above 50% - the temperature is increased by 0.3 degrees.
        If temperature is lower than 10 - the pollution is decreased bu 2%.
        """
        if self.pollution > 50:
            self.nextTemperature += 0.3
        if self.temperature < 10:
            self.increasePollution(-2)

    def updateSea(self):
        """
        If the sea temperature is higher than 100 - it becomes earth.
        If the sea temperature is less than -10 - it becomes a glacier.
        """
        if self.temperature > 100:
            self.nextType = "earth"
            self.echoSystem.sea -= 1
        elif self.temperature < -10:
            self.nextType = "glacier"
            self.echoSystem.sea -= 1
            self.echoSystem.glaciers += 1

    def updateForest(self):
        """
        If temperature reaches 60 or pollution is 100% - forest turns to earth.
        Forest reduces pollution by 5%.
        """
        if self.temperature >= 60 or self.pollution >= 100:
            self.nextType = "earth"
            self.echoSystem.forests -= 1
        else:
            self.increasePollution(-2)

    def updateGlacier(self):
        """
        If temperature reaches 0 or pollution is 100% - glacier turns into sea.
        """
        if self.temperature > 0 or self.pollution >= 100:
            self.nextType = "sea"
            self.echoSystem.sea += 1
            self.echoSystem.glaciers -= 1

    def updateWind(self):
        """
        Update the wind speed & direction, pollution, clouds and rain of the neighbor cells.
        """
        originCell = self
        direction = self.windDirection
        i = 1
        # A cell distributes the wind to the neighbor cells according to its wind speed and direction
        while i <= int(self.windSpeed/10):
            destCell = originCell.neighbors[direction]
            # Wind distributes clouds and rain
            if originCell.clouds:
                destCell.nextClouds = True
                originCell.nextClouds = False
                if originCell.rain:
                    destCell.nextRain = True
                    originCell.nextClouds = False

            # Increase wind speed in destination cell
            destCell.increaseWindSpeed(10)

            # Change wind direction of the destination cell
            direction = self.calcWindDirection(originCell, destCell)
            destCell.nextWindDirection = direction

            # Wind distributes pollution
            if destCell.pollution < self.pollution:
                destCell.increasePollution(5)
            elif destCell.pollution > self.pollution:
                destCell.increasePollution(-2)
            originCell = destCell
            i += 1
        self.increaseWindSpeed(-10)

    def calcWindDirection(self, cell1, cell2):
        """
        Calculates the new wind direction in the destination cell.
        :return: The new wind direction.
        """
        direction1 = cell1.windDirection
        direction2 = cell2.windDirection
        if direction1 == "north" and direction2 == "south":
            return "east"
        elif direction1 == "south" and direction2 == "north":
            return "west"
        elif direction1 == "east" and direction2 == "west":
            return "north"
        elif direction1 == "west" and direction2 == "east":
            return "south"
        else:
            return direction1

    def updateRain(self):
        """
        Rain reduces pollution by 2%.
        """
        self.increasePollution(-2)
        self.nextTemperature -= 0.1

    def increaseWindSpeed(self, value):
        """
        Increases wind speed by a given value (negative value reduces speed).
        Wind speed can't be lower than 0 or higher than 30.

        :param value: value to add to the wind speed (can be positive or negative).
        """
        self.nextWindSpeed += value
        if self.nextWindSpeed > const.MAX_WIND_SPEED:
            self.nextWindSpeed = const.MAX_WIND_SPEED
        elif self.nextWindSpeed < const.MIN_WIND_SPEED:
            self.nextWindSpeed = const.MIN_WIND_SPEED

    def increasePollution(self, value):
        """
        Increases pollution by a given value (negative value reduces pollution).
        Pollution can't be higher than 100 or lower than 0.

        :param value: value to add to the pollution (can be positive or negative).
        """
        self.nextPollution += value
        if self.nextPollution > const.MAX_POLLUTION:
            self.nextPollution = const.MAX_POLLUTION
        elif self.nextPollution < const.MIN_POLLUTION:
            self.nextPollution = const.MIN_POLLUTION
