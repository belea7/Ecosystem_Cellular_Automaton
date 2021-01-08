import cell
import constants as const
import tkinter as tk
from statistics import stdev
import matplotlib.pyplot as plt


class EchoSystem:
    """
    Class representing the Echo System containing the cells.
    """
    def __init__(self):
        self.world = []         # Array containing the cells
        self.generation = 0     # Keeps count on the cells generations
        self.stats = {}         # Stores data about the world
        self.glaciers = 0       # Counts the number of glaciers
        self.forests = 0        # Counts the number of forests
        self.sea = 0            # Counts the number of sea cells
        self.createWorld()      # Initiates the world

    def createWorld(self):
        """
        Creates (initiates) the world using the world.dat.
        """
        # Init the world with the data from world.dat file
        with open(const.WORLD_FILE, 'r') as f:
            for row in range(const.WORLD_SIZE):
                self.world.append([])
                for col in range(const.WORLD_SIZE):
                    c = f.read(1)
                    while c not in const.WORLD_CELLS:
                        c = f.read(1)
                    if c == "E":
                        # Create cell of type 'earth'
                        self.world[row].append(cell.Cell(echoSystem=self, coordinates=(row, col), cellType="earth"))
                    if c == "C":
                        # Create cell of type 'city'
                        self.world[row].append(cell.Cell(echoSystem=self, coordinates=(row, col), cellType="city"))
                    if c == "F":
                        # Create cell of type 'forest' and update the forests counter
                        self.world[row].append(cell.Cell(echoSystem=self, coordinates=(row, col), cellType="forest"))
                        self.forests += 1
                    if c == "S":
                        # Create cell of type 'sea' and update the seas counter
                        self.world[row].append(cell.Cell(echoSystem=self, coordinates=(row, col), cellType="sea"))
                        self.sea += 1
                    if c == "G":
                        # Create cell of type 'glaciers' and update the glaciers count
                        self.world[row].append(cell.Cell(echoSystem=self, coordinates=(row, col), cellType="glacier"))
                        self.glaciers += 1

        # Let every cell update its neighbors
        for row in self.world:
            for column in row:
                column.updateNeighbors()

    def updateWorld(self):
        """
        Updates the world.
        First each cell calculates its changes.
        After all cells calculated the changes, they apply them.
        """
        # Update the 'stats' dict which saves data about the system
        self.calcStats()
        self.generation += 1
        # Calculate for each cell what changes need to made
        for row in self.world:
            for column in row:
                column.calcChanges()

        # Apply the changes in each cell
        for row in self.world:
            for column in row:
                column.applyChanges()

    def calcStats(self):
        """
        Update the data dict.
        The dict stores data about the world (pollution, temperature etc.) for every generation.
        :return:
        """
        temp = []
        pollution = []
        for row in self.world:
            for col in row:
                temp.append(col.temperature)
                pollution.append(col.pollution)
        data = {}
        data["temp"] = temp
        data["pollution"] = pollution
        data["forests"] = self.forests
        data["sea"] = self.sea
        data["glaciers"] = self.glaciers
        self.stats[self.generation] = data


class Gui:
    def __init__(self):
        """
        Class for handling the GUI.
        """
        self.items = []
        self.echoSystem = EchoSystem()
        self.root = tk.Tk()
        self.root.title("Maman 11 - Biological Computation - Lea Ben Zvi")
        self.label = tk.Label(self.root)
        self.label.pack()

        height = const.WORLD_SIZE * const.CELL_SIZE
        # Create canvas for displaying the world
        self.canvas = tk.Canvas(self.root,
                                height=height,
                                width=height)
        self.canvas.pack()

        # Add label which contains the current generation
        self.label.config(text="Generation {}".format(self.echoSystem.generation))
        self.updateCanvas()

        # Refresh the screen every interval
        self.root.after(const.REFRESH_RATE, self.refreshScreen)
        self.root.mainloop()

    def refreshScreen(self):
        """
        Refreshes the screen every interval, displaying the new generations.
        """
        # Update the world and display it
        self.echoSystem.updateWorld()
        generation = self.echoSystem.generation
        self.label.config(text="Generation {}".format(generation))
        self.updateCanvas(new=False)
        if generation < const.STOP_GEN:
            self.root.after(const.REFRESH_RATE, self.refreshScreen)
        else:
            # If the last generation is reached - print graphs
            self.printStats()
            self.createGraphs()

    def updateCanvas(self, new=True):
        """
        Updates the canvas containing the echo system world.
        """
        # If first iteration - create the GUI
        if new:
            for row in range(len(self.echoSystem.world)):
                self.items.append([])
                # Create the cell objects in the GUI
                for col in range(0, len(self.echoSystem.world)):
                    cell = self.echoSystem.world[row][col]
                    cellText = "{}".format(int(cell.temperature))
                    rectID = self.canvas.create_rectangle(row*const.CELL_SIZE,
                                                          col*const.CELL_SIZE,
                                                          (row+1)*const.CELL_SIZE,
                                                          (col + 1) * const.CELL_SIZE,
                                                          fill=const.CELL_TYPES[cell.type])
                    textId = self.canvas.create_text((row+0.5)*const.CELL_SIZE,
                                                     (col+0.5)*const.CELL_SIZE,
                                                     text=cellText, font="Arial 8 bold")
                    self.items[row].append((rectID, textId))
        # Else - update it
        else:
            items = len(self.items)
            # Update the display of the cells
            for row in range(items):
                for col in range(items):
                    cell = self.echoSystem.world[row][col]
                    cellText = "{}".format(int(cell.temperature))
                    (rectID, textId) = self.items[row][col]
                    self.canvas.itemconfig(rectID, fill=const.CELL_TYPES[cell.type])
                    self.canvas.itemconfig(textId, text=cellText)

    def printStats(self):
        """
        Prints data about the temperature and the pollution levels.
        :return:
        """
        # Print temperatures
        temperatures = []
        for gen in self.echoSystem.stats.values():
            temperatures += gen["temp"]
        print("Temperature max = {}".format(max(temperatures)))
        print("Temperature min = {}".format(min(temperatures)))
        avg = sum(temperatures) / len(temperatures)
        print("Temperature avg = {}".format(avg))
        print("Temperature stdev = {}\n".format(stdev(temperatures)))

        # Print pollution values
        pollutions = []
        for gen in self.echoSystem.stats.values():
            pollutions += gen["pollution"]
        print("Pollution max = {}".format(max(pollutions)))
        print("Pollution min = {}".format(min(pollutions)))
        avg = sum(pollutions) / len(pollutions)
        print("Pollution avg = {}".format(avg))
        print("Pollution stdev = {}".format(stdev(pollutions)))

    def createGraphs(self):
        """
        Creates three figures (windows) with the following graphs:
            1. Temperature avg and stdev overtime (figure 1).
            2. Pollution avg and stdev overtime (figure 1).
            3. Normalized temperature overtime (figure 2).
            4. Normalized pollution overtime (figure 2).
            5. Avg pollution level impact on temperature, forests, seas and glaciers (figure 3).
        :return:
        """
        gens = self.echoSystem.stats.keys()
        plt.figure(1)
        plt.subplots_adjust(hspace=0.5)

        # Create temperature overtime graph
        temp_avgs = []
        temp_stdevs = []
        for gen in gens:
            values = self.echoSystem.stats[gen]["temp"]
            temp_avgs.append(sum(values) / len(values))
            temp_stdevs.append(stdev(values))
        plt.subplot(211, title="Temperature avg and stdev overtime")
        plt.plot(gens, temp_avgs, label="temp_avg", color="blue")
        plt.plot(gens, temp_stdevs, label="temp_stdev", linestyle="dashed")
        plt.grid(True)
        plt.xlabel("Generations")
        plt.ylabel("Temperature")
        plt.legend()

        # Create normalized temperature graph overtime
        plt.figure(2)
        plt.subplots_adjust(hspace=0.5)
        plt.subplot(211, title="Normalized temperature overtime")
        year_avg = sum(temp_avgs) / len(temp_avgs)
        year_stdev = stdev(temp_avgs)
        new_avgs = [(x-year_avg)/year_stdev for x in temp_avgs]
        plt.plot(gens, new_avgs, label="normalized_temp")
        plt.grid(True)
        plt.xlabel("Generations")
        plt.ylabel("Temperature")
        plt.legend()

        # Create pollution graph overtime
        plt.figure(1)
        pollution_avgs = []
        pollution_stdevs = []
        for gen in gens:
            values = self.echoSystem.stats[gen]["pollution"]
            pollution_avgs.append(sum(values) / len(values))
            pollution_stdevs.append(stdev(values))
        plt.subplot(212, title="Pollution avg and and stdev overtime")
        plt.plot(gens, pollution_avgs, label="pollution_avg", color="blue")
        plt.plot(gens, pollution_stdevs, label="pollution_stdev", linestyle="dashed")
        plt.grid(True)
        plt.xlabel("Generations")
        plt.ylabel("Pollution")
        plt.legend()

        # Create normalized pollution graph overtime
        plt.figure(2)
        plt.subplot(212, title="Normalized pollution overtime")
        year_avg = sum(pollution_avgs) / len(pollution_avgs)
        year_stdev = stdev(pollution_avgs)
        new_avgs = [(x - year_avg) / year_stdev for x in pollution_avgs]
        plt.plot(gens, new_avgs, label="normalized_pollution")
        plt.grid(True)
        plt.xlabel("Generations")
        plt.ylabel("Pollution")
        plt.legend()

        plt.figure(3, figsize=(8, 8))
        plt.subplots_adjust(hspace=0.9)
        glaciers = []
        forests = []
        sea = []
        for gen in gens:
            glaciers.append(self.echoSystem.stats[gen]["glaciers"])
            forests.append(self.echoSystem.stats[gen]["forests"])
            sea.append(self.echoSystem.stats[gen]["sea"])

        # Create pollution and temperature correlation graph
        plt.subplot(411, title="Pollution and temperature")
        plt.plot(pollution_avgs, temp_avgs, label="temp_avg", color="red")
        plt.grid(True)
        plt.xlabel("Pollution")
        plt.ylabel("Temperature")
        plt.legend()

        # Create pollution and forests correlation graph
        plt.subplot(412, title="Pollution and forests number")
        plt.plot(pollution_avgs, forests, label="forests", color="green")
        plt.grid(True)
        plt.xlabel("Pollution")
        plt.ylabel("Forests")
        plt.legend()

        # Create pollution and seas correlation graph
        plt.subplot(413, title="Pollution and seas number")
        plt.plot(pollution_avgs, sea, label="seas", color="blue")
        plt.grid(True)
        plt.xlabel("Pollution")
        plt.ylabel("Sea")
        plt.legend()

        # Create pollution and glaciers correlation graph
        plt.subplot(414, title="Pollution and glaciers number")
        plt.plot(pollution_avgs, glaciers, label="glaciers", color="grey")
        plt.grid(True)
        plt.xlabel("Pollution")
        plt.ylabel("Glaciers")
        plt.legend()

        plt.show()


if __name__ == "__main__":
    Gui()
