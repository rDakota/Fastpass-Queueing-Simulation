"""
Implementation of an M/M/1 queue using the discret-event advance strategy

Simulator for a two-class priority queueing system
Find the most fast passes to give out for least wait time
The ride runs at two utilization levels:

50% during periods of low activity 
95% during periods of high activity.

@Author Rowan Richter
@Date 04/16/2002
"""
import matplotlib.pyplot as plt
from math import log
from random import random
from heapq import heappush, heappop, heapify # Priority queue operations


def rand_exp(rate):
  """ 
  Generate an exponential random variate
  input: rate, the parameter of the distribution
  returns: the exponential variate
  """
  return -log(random()) / rate

def is_fp(fastpass_fraction):
  """ 
  Determine if the customer has a fastpass
  input: fastpass_frac, the fraction of customers with FastPasses
  returns: True if customer is a fastpass holder, False otherwise
  """
  if random() < fastpass_fraction:
    return 0  # 0 means the customer is fastpass
  else:
    return 1 # 1 means the customer is regular

#--- main simulation function
def simulate(arrival_rate, fp_frac):
  """ 
  Simulate a two-class priority queueing system
  input: fastpass_rate, the fraction of customers with FastPasses
  returns: the average simulated residence times for both classes
  """
  
  # Stopping condition and basic parameters
  max_num_arrivals = 50000
  service_rate = 1.0
  time = 0.0
  num_in_queue = [0, 0] # [0] == fp, [1] == reg

  # Necessary Queue lists ---- [0] == fp, [1] == reg
  arrival_times = [[], []] 
  enter_service_times = [[], []]
  departure_times = [[], []]
  
  fel = []  # future event list == empty list

  # Make the first arrival event
  interarrival_time = rand_exp(arrival_rate)
  
  # determine the type of priority and create a new event
  priority = (is_fp(fp_frac), time + interarrival_time)
  new_event = (priority, 'arrival')

  # Insert with a heap operation
  heappush(fel, new_event)

  while (len(fel) > 0) and (len(arrival_times[1]) + len(arrival_times[0])) < max_num_arrivals:
    # Pop the next event with a heap operation
    event = heappop(fel)

    # Event attributes
    event_priority = event[0] # entire priority tuple
    event_type = event[1] # 'arrival' or 'departure'

    # Advance simulated time
    time = event_priority[1] # (time + interarrival_time) part

    
#---Process events-------------------------------------------------------
    # If event is arrival and fastpass
    # event_priority[0] == 0 is fastpass
    if event_type == 'arrival' and event_priority[0] == 0: 

      # Log fastpass arrival time
      arrival_times[0].append(time)

      # Increment fastpass queue size
      num_in_queue[0] += 1

      # Generate next arrival
      interarrival_time = rand_exp(arrival_rate)
      priority = (is_fp(fp_frac), time + interarrival_time)
      new_event = (priority, 'arrival')
      
      # Put new arrival into heap
      heappush(fel, new_event)

      # If queue is empty, enter service and generate a future departure event
      if num_in_queue[0] == 1:

        # Log enter service time for fastpass
        enter_service_times[0].append(time)

        # Generate new departure event
        service_time = rand_exp(service_rate)
        priority = (0, time + service_time) # its a fastpass customer
        new_event = (priority, 'departure')
        heappush(fel, new_event)

    
#---Event is departure and fastpass---------------------------------------
    # If event is departure and fastpass
    # event_priority[0] == 0 is fastpass
    elif event_type == 'departure' and event_priority[0] == 0:

      # Log fastpass departure time
      departure_times[0].append(time)
      
      # Decrement fastpass queue size
      num_in_queue[0] -= 1

      # if fastpass queue has more customers waiting
      # put the next one into service and generate a departure
      if num_in_queue[0] > 0:

        # Log enter service time
        enter_service_times[0].append(time)

        # Generate new departure event
        service_time = rand_exp(service_rate)
        priority = (0, time + service_time) # its a fastpass customer
        new_event = (priority, 'departure')
        heappush(fel, new_event)

    
#---Event is arrival and regular--------------------------------------
    # If event is arrival and regular
    # event_priority[0] == 1 is regular customer
    elif event_type == 'arrival' and event_priority[0] == 1:

      # Log regular arrival time
      arrival_times[1].append(time)

      # Increment regular queue size
      num_in_queue[1] += 1

      # Generate next arrival
      interarrival_time = rand_exp(arrival_rate)
      priority = (is_fp(fp_frac), time + interarrival_time)
      new_event = (priority, 'arrival')
      
      # Put new arrival into heap
      heappush(fel, new_event)

      # if regular queue is empty and there are no fastpasses in queue
      # enter service and generate a future departure event
      if (num_in_queue[1] == 1) and (num_in_queue[0] == 0):

        # Log enter service time
        enter_service_times[1].append(time)

        # Generate new departure event
        service_time = rand_exp(service_rate)
        priority = (1, time + service_time) # its a regular customer
        new_event = (priority, 'departure')
        heappush(fel, new_event)

    
# ---Event is departure and non-fastpass----------------------------------
    # If event is departure and regular
    # event_priority[0] == 1 is regular customer
    elif event_type == 'departure' and event_priority[0] == 1:

      # Log regular departure time
      departure_times[1].append(time)

      # Decrement regular queue size
      num_in_queue[1] -= 1

      # if more regular customers are waiting
      # put the next one into service and generate a departure
      if num_in_queue[1] > 0:

        # Log enter service time for regular customer
        enter_service_times[1].append(time)

        # Generate new departure event
        service_time = rand_exp(service_rate)
        priority = (1, time + service_time) # its a regular customer
        new_event = (priority, 'departure')
        heappush(fel, new_event)
  
  # ---End of Simulation-------------------------------------------
  # Calculate statistics
  
  # Regular customers residence times
  res_time_reg = [ departure_times[1][i] - arrival_times[1][i] for i in range(len(departure_times[1])) ]
  avg_res_time_reg = sum(res_time_reg) / len(res_time_reg)

  # Fastpass customers residence times
  if (fp_frac == 0):
    avg_res_times = (avg_res_time_reg, 0) # tuple with results
    return avg_res_times # return the average residence times
    
  res_time_fp = [ departure_times[0][i] - arrival_times[0][i] for i in range(len(departure_times[0])) ]
  avg_res_time_fp = sum(res_time_fp) / len(res_time_fp)

  avg_res_times = (avg_res_time_reg, avg_res_time_fp) # tuple with results
  return avg_res_times # return the average residence times


def simulate_and_plot_high(arrival_rate):
  """ 
  Simulate and plot residence times for different utilization levels
  lamba = (0.95 == high load) and varying values of fp_frac
  """
  fp_frac = 0.00
  high_load_residence_times_fastpass = {}
  high_load_residence_times_regular = {}

  while fp_frac <= 1.0: # all fractions
    sim_residence_times_regular = []
    sim_residence_times_fastpass = []

    for i in range(20): # all util levels
      result = simulate(arrival_rate, fp_frac)
      sim_residence_times_regular.append(result[0])
      sim_residence_times_fastpass.append(result[1])

    r_avg_regular = sum(sim_residence_times_regular) / len(
      sim_residence_times_regular)
    r_avg_fastpass = sum(sim_residence_times_fastpass) / len(
      sim_residence_times_fastpass)

    high_load_residence_times_regular[fp_frac] = r_avg_regular
    high_load_residence_times_fastpass[fp_frac] = r_avg_fastpass

    fp_frac += 0.05 # update fastpass ratio

  # plot fastpass and regular
  plt.plot(high_load_residence_times_fastpass.keys(),
         high_load_residence_times_fastpass.values(),
          color='lightblue')
  plt.plot(high_load_residence_times_regular.keys(),
         high_load_residence_times_regular.values(),
          color='green')

  # find the x-coordinate where the two lines meet
  intersection_fp_frac = min(high_load_residence_times_regular, key=lambda x: abs(high_load_residence_times_regular[x] - high_load_residence_times_fastpass[x]))

  # plot the intersection point
  plt.plot(intersection_fp_frac, high_load_residence_times_regular[intersection_fp_frac], 'bo', markersize=10)

  # labeling of graph intersection
  x_pos = intersection_fp_frac - 0.1
  y_pos = high_load_residence_times_regular[intersection_fp_frac] + 0.75
  plt.text(x_pos, y_pos, f"({intersection_fp_frac:.2f}, {high_load_residence_times_regular[intersection_fp_frac]:.2f})", fontsize=12)

  # define the x and y values for fastpass
  x1 = list(high_load_residence_times_fastpass.keys())
  y1 = list(high_load_residence_times_fastpass.values())

  # define the x and y values for regular
  x2 = list(high_load_residence_times_regular.keys())
  y2 = list(high_load_residence_times_regular.values())
  
  # starting position
  x_start = round(intersection_fp_frac, 2)

  # create an array of boolean values based on the x-values of the data
  fill_mask = [(x <= x_start) for x in x1]

  # Fill between
  plt.fill_between(x1, y1, y2, where=fill_mask, interpolate=True, color='yellow', alpha=0.2)
  
  # labeling of graph info
  plt.xlabel("Fastpass Customer Ratio")
  plt.ylabel("Avg. Residence Time (minutes)")
  plt.legend(["Fastpass", "Regular"], loc="upper right")
  # y vs. x axis
  plt.title("Avg. Residence Time Vs Fastpass Customer Ratio\nHigh Load Simulation")
  plt.savefig('Residence_Times_High_Load.pdf')
  plt.clf()


def simulate_and_plot_low(arrival_rate):
  """
  Simulate and plot residence times for different utilization levels
  lamba = (0.50 == low load) and varying values of fp_frac
  """
  fp_frac = 0.00
  low_load_residence_times_fastpass = {}
  low_load_residence_times_regular = {}

  while fp_frac <= 1.0: # all fractions
    sim_residence_times_regular = []
    sim_residence_times_fastpass = []

    for i in range(20): # all util levels
      result = simulate(arrival_rate, fp_frac)
      sim_residence_times_regular.append(result[0])
      sim_residence_times_fastpass.append(result[1])

    r_avg_regular = sum(sim_residence_times_regular) / len(
      sim_residence_times_regular)
    r_avg_fastpass = sum(sim_residence_times_fastpass) / len(
      sim_residence_times_fastpass)

    low_load_residence_times_regular[fp_frac] = r_avg_regular
    low_load_residence_times_fastpass[fp_frac] = r_avg_fastpass

    fp_frac += 0.05 # update fastpass ratio
    
  # plot fastpass and regular
  plt.plot(low_load_residence_times_fastpass.keys(),
         low_load_residence_times_fastpass.values(),
          color='lightblue')
  plt.plot(low_load_residence_times_regular.keys(),
         low_load_residence_times_regular.values(),
          color='green')

  # find the x-coordinate where the two lines meet
  intersection_fp_frac = min(low_load_residence_times_regular, key=lambda x: abs(low_load_residence_times_regular[x] - low_load_residence_times_fastpass[x]))

  # plot the intersection point
  plt.plot(intersection_fp_frac, low_load_residence_times_regular[intersection_fp_frac], 'bo', markersize=10)

  # labeling of graph intersection
  x_pos = intersection_fp_frac - 0.1
  y_pos = low_load_residence_times_regular[intersection_fp_frac] + 0.125
  plt.text(x_pos, y_pos, f"({intersection_fp_frac:.2f}, {low_load_residence_times_regular[intersection_fp_frac]:.2f})", fontsize=12)

  # define the x and y values for fastpass
  x1 = list(low_load_residence_times_fastpass.keys())
  y1 = list(low_load_residence_times_fastpass.values())

  # define the x and y values for regular
  x2 = list(low_load_residence_times_regular.keys())
  y2 = list(low_load_residence_times_regular.values())
  
  # starting position
  x_start = round(intersection_fp_frac, 2)

  # create an array of boolean values based on the x-values of the data
  fill_mask = [(x <= x_start) for x in x1]

  # Fill between
  plt.fill_between(x1, y1, y2, where=fill_mask, interpolate=True, color='yellow', alpha=0.2)

  
  plt.xlabel("Fastpass Customer Ratio")
  plt.ylabel("Avg. Residence Time (minutes)")
  plt.legend(["Fastpass", "Regular"], loc="lower right")
  # y vs. x axis
  plt.title("Avg. Residence Time Vs Fastpass Customer Ratio\nLow Load Simulation")
  plt.savefig('Residence_Times_Low_load.pdf')

#---Main
def main():
  """ 
  Run the Fastpass+ Simualtion for high and low loads
  lamba = (0.95 == high load) and varying values of fp_frac
  lamda = (0.50 == low load) and varying values of fp_frac
  """
  lamda_high = 0.95
  lamda_low = 0.5
  simulate_and_plot_high(lamda_high)
  simulate_and_plot_low(lamda_low)

#---Run Main
if __name__ == '__main__':
    main()
