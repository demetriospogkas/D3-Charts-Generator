# Generate D3 charts from the command line
Python flask script that lets you generate from the command line D3 basic code for three types of charts: bar, scatter and timeseries plots. Use it for quick previews of your charts, or build on the generated code to create interactive visualizations.

## Usage 

### Dependencies

[Pipenv](https://docs.pipenv.org/) is used for virtualenv/dependency management.

```bash
pipenv install
pipenv shell
```

### Try it out!

For bar plots:

```bash
python generate_D3.py Milwuakee-Bucks_All-Players_2016-2017.csv bar -x PPG -y PLAYER_NAME -xl "points per game" -he 500 -wm 850 5 5 -xs 0.1 600 -sfv lightblue 1 -ssv "#000000" 1 1 -t "Milwuakee Bucks 2016-2017 Season Performance" -ts "stats.nba.com" -l -lp 8000
```

![D3 Charts Generator - Bars](examples/example_bar.png)

### Details


#### Positional arguments


#### Optional Arguments / Flags


## Known issues

- The script only works for data sets in `.csv` format.
- The script uses v4.2.2 of D3.

## More examples

For scatter plots:  

```bash
python generate_D3.py GTD_2016_Per-Population.csv scatter -x kills_per_pop_2016 -y wound_per_pop_2016 -r population_2016 -xs 0 80 -ys 0 40 -rs 3 35 -xt 20 40 60 80 -yt 0 10 20 30 40 -xl "per 100k" -yl "per 100k" -wm 800 100 60 -sfv lightblue 0.5 -ssv "#000000" 1 1 -t "Terrorism Victims: Killed and wounded per population in 2016" -ts "Global Terrorism Database - University of Maryland. Data for countries with at least one victim in 2016." -l -lp 8000
```

![D3 Charts Generator - Scatter](examples/example_scatter.png)

For timeseries plots:

```bash
python generate_D3.py WTI_Historical_1986-2018.csv timeseries -x date -y dollars_per_barrel -xs 1/1/2000 12/31/2017 -ys 0 150 -xt 1/1/05 1/1/10 1/1/15 -yt 0 75 150 -yl "$ per barrel" -wm 800 120 60 -ssv lightblue 1 3 -t "Cushing, OK WTI Spot Price FOB, 2010-2017" -ts "U.S. Energy Information Administration" -l -lp 8000
```

![D3 Charts Generator - Timeseries](examples/example_timeseries.png)

#### Acknowledgements

[D3 JavaScript library](https://github.com/d3/d3) created by Mike Bostock; News Cycle font by Nathan Willis via [1001fonts.com](http://www.1001fonts.com/news-cycle-font.html); the Stack Overflow community.
