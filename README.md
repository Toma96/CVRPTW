# CVRPTW #
## Capacitated Vehicle Routing Problem with Time Windows ##

There are six input files containing the number of available vehicles, their capacity, depot position, closing time of depot and all the data on customers (position, service time, available time interval, demand). Primary goal is to minimize the number of vehicles, secondary goal is to minimize the total distance.


* 6 instances:
  * i1: 100 customers, 25 vehicles    (best known: 18, my result for running the algorithm for 15 min: 19)
  * i2: 200 customers, 50 vehicles    (best known: 18, my: 21)
  * i3: 400 customers, 100 vehicles   (best known: 11, my: 13)
  * i4: 600 customers, 150 vehicles   (best known: 11, my: 12)
  * i5: 800 customers, 200 vehicles   (best known: 22, my: 29)
  * i6: 1000 customers, 250 vehicles  (best known: 91, my: 94)

Used algorithms for solving the problem are: *greedy search* for initial solution and then *simulated annealing* with parameters specified in parameters.py file.

Make sure to create folder output_files at the same level as the main.py before running the program.
More details are provided in the docx file.

For additional information and questions, feel free to contact me via mail: toma.petrac@gmail.com
