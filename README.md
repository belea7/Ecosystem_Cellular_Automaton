Cellular automaton that simulates the effect of air pollution on the world's temperature
-----------
**The program implements the cellular automaton entirely (without using external modules).**

**Python modules: tkinter, matplotlib, numpy.**

**Biological Computation course at The Open University of Israel**

I implemented a Cellular Automaton which represents the world as an ecological system. It measures the how pollution levels impact the temperature of the world and the different elemants in it, such as the number of forests, glaciers etc.

The world is represented as a grid, which contains cells from different types: land, seas, glaciers, cities and forests. Every cell has cell has the following parameters: height, temperature, wind speed, wind direction, rain, clouds, and pollution.
The grid has an initial setup and it changes overtime:
- The cities produce pollution
- Forests, rain and low temperature reduce pollution
- The wind travels the grid according to its speed and direction
- Clouds travel with the wind and can strat/stop raining randomly
- Hight pollution increases temperature
- High levels of pollution and temperature causes glaciers to melt, forests to be destroyed, and seas to evaporate.

The program displays the initial state of the world and updates it every generation (using tkinter).

The program keeps track of different statistics, such as:
- Global temperature and pollution levels
- Number of forests, glaciers, and seas

When the program finishes running, it displays reports:
