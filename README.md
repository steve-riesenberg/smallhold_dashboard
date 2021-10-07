# smallhold_dashboard
A plotly-dash dashboard hosted on Heroku displaying data from a mushroom farm.

You can view the dashboard at https://smallhold-dashboard.herokuapp.com/

The dashboard gives:
  1. The current status at the farm based on the latest sensor reading.
  2. The count of "incidents" over a time frame, or anything needing attention. This could be defined a variety of ways, such as co2, temperature, or humidity going above or below pre-defined values or using an anomaly detection algorithm. In this example I looked for points three standard deviations away from the mean.
  3. A whole view of all the sensor data over time, with outliers highlighted in orange. 

The user can change the period of time they are viewing the data with the buttons in the model, this changes both the graphs and the logic counting the number of outliers. 
The data is also smoothed into 5 minute intervals to make the visualizations a little nicer.



The dashboard is hosted on Heroku to make it easy to view. If you'd like to run it locally, you can follow these steps:
1. Clone this repo
2. Install the requirements listed in the requirements file, except gunicorn (gunicorn is required by Heroku but not required to run the app locally and is often difficult to install).
3. Run "python app.py" from the terminal

