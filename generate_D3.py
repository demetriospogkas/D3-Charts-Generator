import argparse
from flask import Flask
from flask import render_template
from flask_flatpages import FlatPages
from flask_frozen import Freezer
import os
import pandas as pd
import re
import shutil
import subprocess
from termcolor import colored
import webbrowser


def set_args():
        parser = argparse.ArgumentParser()
        parser.add_argument("data_file", type=str,
                            help="Path to your data set file.")
        parser.add_argument("chart_type", type=str,
                            choices=['bar', 'timeseries', 'scatter'],
                            help="The type of chart you wish to generate. Choose between line, bar, or scatter plots.")

        parser.add_argument("-l", "--localhost", action='store_true',
                            help="If used while you 'build' the script, it will also set up a local server for previewing the output.")
        parser.add_argument("-lp", "--localhost-port", type=str,
                            help="If you 'run' the script or if you request a local server when you 'build', use this argument to assign a specific port to run the server. If no specific port is assigned, it defaults to 8000.")

        parser.add_argument("-x", "--x-axis", type=str,
                            help="Column from your data set to used for the X axis of your plot.")
        parser.add_argument("-y", "--y-axis", type=str,
                            help="Column from your data set to used for the Y axis of your plot.")
        parser.add_argument("-xs", "--x-axis-scale", type=str,
                            nargs='+',
                            help="Pass a custom scale for the X axis of your plot. Pass numerical values for bar and scatter plots, and dates with %%m/%%d/%%y format for timeseries plot. Pass only min and max values. If not used, X axis scale will be automatically created from the data you're generate the X axis from.")
        parser.add_argument("-ys", "--y-axis-scale", type=float,
                            nargs='+',
                            help="Pass a custom scale for the Y axis of your plot. Use it only for bar and scatter plots. Pass only min and max values. If not used, Y axis scale will be automatically created from the data you're generate the Y axis from.")
        parser.add_argument("-he", "--height", type=int,
                            help="Pass a custom height for your plot. Use it only for bar plot to adjust the scale of the y axis. If not used, it defaults to 1200.")
        parser.add_argument("-xt", "--x-axis-ticks", type=str,
                            nargs='+',
                            help="Pass custom ticks to the x-axis of your plot. Use it only for scatter and timeseries plots. Enter 1 value if you want to specify the number of ticks D3 should generate, or enter multiple values to create a custom list of ticks. If not used, it defaults to the default D3 behavior.")
        parser.add_argument("-yt", "--y-axis-ticks", type=float,
                            nargs='+',
                            help="Pass custom ticks to the y-axis of your plot. Use it only for scatter and timeseries plots. Enter 1 value if you want to specify the number of ticks D3 should generate, or enter multiple values to create a custom list of ticks. If not used, it defaults to the default D3 behavior.")
        parser.add_argument("-xl", "--x-axis-label", type=str,
                            help="Specify a key label for the x-axis ticks of your plot. It will be added to the last tick of the axis. Use it only for the bar and scatter plots.")
        parser.add_argument("-yl", "--y-axis-label", type=str,
                            help="Specify a key label for the y-axis ticks of your plot. It will be added to the last tick of the axis. Use it only for the scatter and timeseries plots.")

        parser.add_argument("-r", "--radius", type=str,
                            help="Column from your data set to be used for the radius scale of your scatter plot. If not used all dots in your scatter plot will have a default radius of 7px.")
        parser.add_argument("-rs", "--radius-scale", type=str,
                            nargs='+',
                            help="Pass a custom scale for the radius scale domain of your scatter plot. If not used, it will default to a domain of [3,45].")

        parser.add_argument("-wm", "--widths-margins", type=int,
                            nargs='+',
                            help="Specify the width, the left margin and the right margin of the SVG element of the plot. Pass exactly 3 values. If not used, default values will be passed.")

        parser.add_argument("-sfv", "--style-fill-values", type=str,
                            nargs='+',
                            help="Pass custom fill styles for the elements of your plot. Accepts only two values (color and opacity).")
        parser.add_argument("-ssv", "--style-stroke-values", type=str,
                            nargs='+',
                            help="Pass custom stroke styles for the elements of your plots. Accepts only three values (color, opacity and width).")

        parser.add_argument("-t", "--title", type=str,
                            help="Set title for the map. If not specified the name of the data file will be used.")
        parser.add_argument("-ts", "--title-source", type=str,
                            help="Set source line. If not specified source line will return empty.")

        return parser.parse_args()

def msg_warning(msg):
    return colored(msg, "magenta")

def check_axes(x, y):
  if not x or not y:
    if not x:
      wrong_input = "x-"
    elif not y:
      wrong_input = "y-"
    print(msg_warning("WARNING: You haven't specified the column in your data set to generate the " + wrong_input + "axis from."))
    if not x:
      new_x = input(msg_warning("Enter exact column name to generate the x-axis from: "))
      return check_axes(new_x, y)
    elif not y:
      new_y = input(msg_warning("Enter exact column name to generate the y-axis from: "))
      return check_axes(x, new_y)
  elif not x and not y:
    print(msg_warning("WARNING: You haven't specified the columns in your data set to generate the x- and y-axes from."))
    new_x = input(msg_warning("Enter exact column name to generate the x-axis from: "))
    new_y = input(msg_warning("Enter exact column name to generate the y-axis from: "))
    return check_axes(new_x, new_y)
  elif x and y:
    if x not in COLS or y not in COLS:
      if x not in COLS:
        print(msg_warning("WARNING: The column name you're trying to generate the x-axis from doesn't exist in your data set."))
        new_x = input(msg_warning("Enter exact column name to generate the x-axis from: "))
        return check_axes(new_x, y)
      elif y not in COLS:
        print(msg_warning("WARNING: The column name you're trying to generate the y-axis from doesn't exist in your data set."))
        new_y = input(msg_warning("Enter exact column name to generate the y-axis from: "))
        return check_axes(x, new_y)
    elif x in COLS and y in COLS:
      return x, y

def check_lens(alist, which_ax):
      if len(alist) == 2:
        if which_ax == 'timeseries x-axis':
          return alist
        else:
          alist = [float(el) for el in alist]
          return alist
      else:
        print(msg_warning("WARNING: The custom scale you're trying to generate for your " + which_ax + " should have exactly two values (min and max)."))
        new_min = input("Enter min value: ")
        new_max = input("Enter max value: ")
        if which_ax == 'timeseries x-axis':
          return [new_min, new_max]
        else:
          new_min = float(new_min)
          new_max = float(new_max)
          return [new_min, new_max]

def generate_fname(new_x):
      DF[x_ax] = pd.to_datetime(DF[x_ax], infer_datetime_format=True)
      range_date = DF[(DF[x_ax] >= new_x[0]) & (DF[x_ax] <= new_x[1])]
      range_date[x_ax] = range_date[x_ax].dt.strftime('%m/%d/%y')
      fname = DATA_FILE[:-4] + '_sliced.csv'
      range_date.to_csv('./static/data/' + fname, index=False)
      return fname

def check_scales(x, y):
  if CHART_TYPE == 'scatter':
    if not x and not y:
      return [DF[x_ax].min(), DF[x_ax].max()], [DF[y_ax].min(), DF[y_ax].max()], None
    elif not x:
        new_y = check_lens(y, "y-axis")
        print(msg_warning("WARNING: You haven't specified a scale for the x-axis of your plot."))
        new_x = input(msg_warning("Enter min and max values for the x-axis: "))
        new_x = [float(x) for x in new_x.split()]
        new_x = check_lens(new_x, "x-axis")
        return check_scales(new_x, new_y, None)
    elif not y:
        new_x = check_lens(x, "x")
        print(msg_warning("WARNING: You haven't specified a scale for the y-axis of your plot."))
        new_y = input(msg_warning("Enter min and max values for the y-axis: "))
        new_y = [float(y) for y in new_y.split()]
        new_y = check_lens(new_y, "y-axis")
        return check_scales(new_x, new_y, None)
    elif x and y:
        new_x = check_lens(x, "x-axis")
        new_y = check_lens(y, "y-axis")
        return new_x, new_y, None
  elif CHART_TYPE == 'timeseries':
    if not x and not y:
        return DATA_FILE, [DF[y_ax].min(), DF[y_ax].max()], None
    elif not x or not y:
      if not x:
        new_y = check_lens(y, "y-axis")
        print(msg_warning("WARNING: You haven't specified a time range for the x-axis of your plot."))
        new_x = input(msg_warning("Enter min and max values for the x-axis time range: "))
        new_x = [x for x in new_x.split()]
        new_x = check_lens(new_x, "timeseries x-axis")
        fname = generate_fname(new_x)
        return fname, new_y, None
      if not y:
        new_x = check_lens(x, "timeseries x-axis")
        fname = generate_fname(new_x)
        print(msg_warning("WARNING: You haven't specified a scale for the y-axis of your plot."))
        new_y = input(msg_warning("Enter min and max values for the y-axis: "))
        new_y = [float(y) for y in new_y.split()]
        new_y = check_lens(new_y, "y-axis")
        return fname, new_y, None
    elif x and y:
      new_x = check_lens(x, "timeseries x-axis")
      fname = generate_fname(new_x)
      new_y = check_lens(y, "y-axis")
      return fname, new_y, None
  elif CHART_TYPE == 'bar':
    if not x:
      return [DF[x_ax].min(), DF[x_ax].max()], None, "[0.1, widthScale]"
    if x:
      new_x = check_lens(x, "x-axis")
      return [DF[x_ax].min(), DF[x_ax].max()], None, new_x

def check_height(num):
  if num:
    return num
  else:
    return 1400

def check_ticks_len(alist):
  if len(alist) == 1:
    return ".ticks(" + str(alist[0]) + ")"
  else:
    alist = [float(el) for el in alist]
    return ".tickValues(" + str(alist) + ")"

def check_ticks_len_time(alist):
  if len(alist) == 1:
    return ".ticks(" + str(alist[0]) + ")"
  else:
    alist = ['parseTime("' + el + '")' for el in alist]
    return ".tickValues(" + str(alist) + ")"

def check_ticks(x, y):
  if not x and not y:
    return ".ticks()", ".ticks()"
  elif x and y:
    if CHART_TYPE != 'timeseries':
      new_x = check_ticks_len(x)
      new_y = check_ticks_len(y)
      return new_x, new_y
    else:
      new_x = check_ticks_len_time(x)
      new_y = check_ticks_len(y)
      return new_x, new_y
  elif x or y:
    if not x:
      new_x = ".ticks()"
      new_y = check_ticks_len(y)
      return new_x, new_y
    elif not y:
      if CHART_TYPE != 'timeseries':
        new_x = check_ticks_len(x)
      else:
        new_x = check_ticks_len_time(x)
      new_y = ".ticks()"
      return new_x, new_y

def check_ax_labels(x_l, y_l):

  def is_pct(str_):
    if str_ == '%':
      return str_
    else:
      return " " + str_

  if not x_l and not y_l:
    return "", ""
  elif x_l and y_l:
    return is_pct(x_l), is_pct(y_l)
  elif not x_l or not y_l:
    if not x_l:
      if CHART_TYPE != 'timeseries':
        print(msg_warning("WARNING: You haven't specified a label for the x-axis of your plot."))
        new_x_l = input("Enter label: ")
        return is_pct(new_x_l), is_pct(y_l)
      else:
        return None, is_pct(y_l)
    if not y_l:
      if CHART_TYPE != 'bar':
        print(msg_warning("WARNING: You haven't specified a label for the y-axis of your plot."))
        new_y_l = input("Enter label: ")
        return is_pct(x_l), is_pct(new_y_l)
      else:
        return is_pct(x_l), None

def check_radius(r_col, r_scale):
  R = 7
  if not r_col:
    return [0, 0], [0, 0], R
  elif r_col:
    if r_col in COLS:
      R_DOM = [DF[r_col].min(), DF[r_col].max()]
      RS = "radiusScale(+d." + r_col + ")"
      if not r_scale:
        R_RANGE = [3, 45]
        return R_DOM, R_RANGE, RS
      if r_scale:
        new_r_scale = check_lens(r_scale, "radius scale")
        return R_DOM, new_r_scale, RS
    elif r_col not in COLS:
      print(msg_warning("WARNING: The column name you're trying to generate a radius scale from doesn't exist in your data set."))
      new_r_col = input(msg_warning("Enter exact column name to generate the radius scale from: "))
      return check_radius(new_r_col, r_scale)

def check_widths(alist):

  def if_bar(w, ml, mr):
    if not X_SCALE:
      return w, ml, mr
    elif X_SCALE and (w >= x_range[1] + 200):
      return w, ml, mr
    elif X_SCALE and (w < x_range[1] + 200):
      new_w = x_range[1] + 200
      return new_w, ml, mr

  if not alist:
    if CHART_TYPE == 'bar':
      if not X_SCALE:
        return 700, 5, 5
      elif X_SCALE:
        w = x_range[1] + 200
        return w, 5, 5
      return 800, 5, 460
    else:
      return 800, 60, 60
  if alist:
    if len(alist) == 3:
      W = alist[0]
      ML = alist[1]
      MR = alist[2]
      if CHART_TYPE == 'bar':
        return if_bar(W, ML, MR)
      else:
        return W, ML, MR
    else:
      print(msg_warning("WARNING: Your custom widths should have exactly 3 values (width, margin left, and margin right)."))
      NEW_W = input("Enter a width value: ")
      NEW_ML = input("Enter a margin left value: ")
      NEW_MR = input("Enter a margin right value: ")
      if CHART_TYPE == 'bar':
        return if_bar(int(NEW_W), int(NEW_ML), int(NEW_MR))
      else:
        return int(NEW_W), int(NEW_ML), int(NEW_MR)

def check_opacity(opac, which_style):
  if not opac:
    return 0.5
  if opac:
    if opac >= 0 and opac <= 1:
      return opac
    if opac < 0 or opac > 1:
      print(msg_warning("WARNING: You're trying to set the opacity of your " + which_style + " style to less than 0 or more than 1."))
      new_opac = input("Enter an opacity value between 0 and 1: ")
      return check_opacity(float(new_opac), which_style)

def check_vals(alist, which_style):
  if which_style == "fill":
    if len(alist) == 2:
      color = alist[0]
      opac = check_opacity(float(alist[1]), "fill")
      return color, opac
    else:
      print(msg_warning("WARNING: Your custom " + which_style + " styles should have exactly 2 elements (colour value and opacity)."))
      color = input("Enter a fill color value: ")
      opac = input("Enter a fill opacity value between 0 and 1: ")
      opac = check_opacity(float(opac), "fill")
      return color, opac
  elif which_style == "stroke":
    if len(alist) == 3:
      color = alist[0]
      opac = check_opacity(float(alist[1]), "stroke")
      width = float(alist[2])
      return color, opac, width
    else:
      print(msg_warning("WARNING: Your custom " + which_style + " styles should have exactly 3 elements (colour value, opacity and width)."))
      color = input("Enter a stroke color value: ")
      opac = input("Enter a stroke opacity value between 0 and 1: ")
      opac = check_opacity(float(opac), "stroke")
      width = input("Enter a stroke width value: ")
      width = float(width)
      return color, opac, width

def check_fill(fill_vals):
  if not fill_vals:
    if CHART_TYPE == 'scatter':
      fill = "lightblue"
      fill_op = 0.5
    elif CHART_TYPE == 'bar':
      fill = "lightblue"
      fill_op = 1
    elif CHART_TYPE == 'timeseries':
      fill = "none"
      fill_op = 1
    return fill, fill_op
  elif fill_vals:
    new_vals = check_vals(fill_vals, "fill")
    return new_vals

def check_stroke(stroke_vals):
  if not stroke_vals:
    if CHART_TYPE == 'scatter' or CHART_TYPE == 'bar':
      stroke = "black"
      stroke_op = 1
      stroke_w = 1
    elif CHART_TYPE == 'timeseries':
      stroke = "lightblue"
      stroke_op = 1
      stroke_w = 1
    return stroke, stroke_op, stroke_w
  elif stroke_vals:
    new_vals = check_vals(stroke_vals, "stroke")
    return new_vals

def check_titles(ttl, src):
  TTL = DATA_FILE.split('.csv')[0].split('/')[-1]
  if ttl and src:
    return ttl, src
  elif not ttl and not src:
    return TTL, ""
  elif not ttl or not src:
    if not ttl:
      return TTL, src
    elif not src:
      return ttl, ""

def initiate():
  print("Building static HTML and JS files...")
  freezer.freeze()

  if CHART_TYPE == 'timeseries':
      fname = "./build/js/chart-timeseries.js"
      with open(fname, 'r') as file:
          filedata = file.read()

      filedata = re.sub(r"'(parseTime.*?)'", "\\1", filedata)

      with open(fname, 'w') as file:
        file.write(filedata)

  print("Success.")

  if LOCALHOST:
    port = LOCAL_PORT if LOCAL_PORT else '8000'
    print("Setting up a local server at port", port, "...")
    os.chdir('./build')
    subprocess.Popen(['python', '-m', 'http.server', port])
    print("Success.")
    print("Opening up a new browser tab...")
    webbrowser.open_new_tab('localhost:' + port)
    print("Success.")


if __name__ == "__main__":
  print("Checking all requirements met...")
  pd.options.mode.chained_assignment = None
  args = set_args()

  DATA_FILE = args.data_file
  DF = pd.read_csv("./static/data/" + DATA_FILE)
  COLS = DF.columns
  CHART_TYPE = args.chart_type
  LOCALHOST = args.localhost
  LOCAL_PORT = args.localhost_port
  X_AXIS = args.x_axis
  Y_AXIS = args.y_axis
  X_SCALE = args.x_axis_scale
  Y_SCALE = args.y_axis_scale
  HEIGHT = args.height
  X_TICKS = args.x_axis_ticks
  Y_TICKS = args.y_axis_ticks
  X_LABEL = args.x_axis_label
  Y_LABEL = args.y_axis_label
  RADIUS = args.radius
  RADIUS_SCALE = args.radius_scale
  WIDTHS = args.widths_margins
  FILL_VALUES = args.style_fill_values
  STROKE_VALUES = args.style_stroke_values
  TITLE = args.title
  SOURCE = args.title_source

  x_ax, y_ax = check_axes(X_AXIS, Y_AXIS)
  x_scale, y_scale, x_range = check_scales(X_SCALE, Y_SCALE)
  height = check_height(HEIGHT)
  x_ticks, y_ticks = check_ticks(X_TICKS, Y_TICKS)
  x_label, y_label = check_ax_labels(X_LABEL, Y_LABEL)
  radius_domain, radius_range, radius_attr = check_radius(RADIUS, RADIUS_SCALE)
  width, margin_left, margin_right = check_widths(WIDTHS)
  fill_val, fill_opacity = check_fill(FILL_VALUES)
  stroke_val, stroke_opacity, stroke_width = check_stroke(STROKE_VALUES)
  title, source = check_titles(TITLE, SOURCE)
  print("Success.")

  if os.path.isdir('./build/'):
    print("Removing existing build directory...")
    shutil.rmtree('./build/')
    print("Success.")

  print("Initializing the Flask app...")
  DEBUG = True
  FLATPAGES_AUTO_RELOAD = DEBUG
  FLATPAGES_EXTENSION = '.md'
  app = Flask(__name__)
  app.config.from_object(__name__)
  pages = FlatPages(app)
  freezer = Freezer(app)
  print("Success.")

  print("Rendering the D3 chart...")
  print("Please wait...")

  @app.route('/')
  def index():
    return render_template('index.html', charttype=CHART_TYPE)

  if CHART_TYPE == 'bar':
    @app.route('/js/chart-bar.js')
    def chartJSBar():
      csv = "../static/data/" + DATA_FILE
      return render_template('js/chart-bar.js', csv=csv, x_ax=x_ax, y_ax=y_ax, x_scale=x_scale, height=height, x_range=x_range, x_label=x_label, w=width, m_l=margin_left, m_r=margin_right, title=title, source=source), {'Content-Type': 'application/javascript'}

    @app.route('/css/chart-bar.css')
    def chartCSSBar():
      return render_template('css/chart-bar.css', fill_val=fill_val, fill_op=fill_opacity, stroke_val=stroke_val, stroke_op=stroke_opacity, stroke_w=stroke_width), {'Content-Type': 'text/css'}

  if CHART_TYPE == 'scatter':
    @app.route('/js/chart-scatter.js')
    def chartJSScatter():
      csv = "../static/data/" + DATA_FILE
      return render_template('js/chart-scatter.js', csv=csv, x_ax=x_ax, y_ax=y_ax, x_scale=x_scale, y_scale=y_scale, x_ticks=x_ticks, y_ticks=y_ticks, x_label=x_label, y_label=y_label, r_dom=radius_domain, r_range=radius_range, r_attr=radius_attr, w=width, m_l=margin_left, m_r=margin_right, title=title, source=source), {'Content-Type': 'application/javascript'}

    @app.route('/css/chart-scatter.css')
    def chartCSSScatter():
      return render_template('css/chart-scatter.css', fill_val=fill_val, fill_op=fill_opacity, stroke_val=stroke_val, stroke_op=stroke_opacity, stroke_w=stroke_width), {'Content-Type': 'text/css'}

  if CHART_TYPE == 'timeseries':
    @app.route('/js/chart-timeseries.js')
    def chartJSTime():
      csv = "../static/data/" + x_scale
      return render_template('js/chart-timeseries.js', csv=csv, x_ax=x_ax, y_ax=y_ax, y_scale=y_scale, x_ticks=x_ticks, y_ticks=y_ticks, y_label=y_label, w=width, m_l=margin_left, m_r=margin_right, title=title, source=source), {'Content-Type': 'application/javascript'}

    @app.route('/css/chart-timeseries.css')
    def chartCSSTime():
      return render_template('css/chart-timeseries.css', fill_val=fill_val, fill_op=fill_opacity, stroke_val=stroke_val, stroke_op=stroke_opacity, stroke_w=stroke_width), {'Content-Type': 'text/css'}

  print("Success.")

  initiate()
