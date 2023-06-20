"""
Assumptions:
- EVs are charged and discharged at the same rate and have the same autonomy
- Drop in people peacefully leave when a booking starts
"""

import numpy as np
from matplotlib import pyplot as plt
np.random.seed(123)

class EV:
    def __init__(self,charge_state,booker=True):
        self.charge_state = charge_state
        self.booker = booker
        self.history = []
    def charge(self):
        self.charge_state += 1
    def discharge(self):
        self.charge_state -= 1
    def update_history(self):
        self.history.append(self.charge_state)

def main(M=5,N=10,T=500,charge_trigger=50,booking_type="random"):
    """
    M: number of charging stations
    N: number of EVs
    T: time horizon
    charge_trigger: charge level at which EVs start booking or charging
    booking_type: "random", "bookers", "dropins"
    
    """
    # Charging stations
    stations = np.zeros((M,T)) # 0 = free, number = occupied
    # EVs
    match booking_type:
        case "random":
            EVs = [EV(np.random.randint(0,100),np.random.randint(0,2)) for _ in range(N)]
        case "bookers":
            EVs = [EV(np.random.randint(0,100),1) for _ in range(N)]
        case "dropins":
            EVs = [EV(np.random.randint(0,100),0) for _ in range(N)]
    # Simulation
    dropin_blockages = np.zeros((N,T))
    booking_blockages = np.zeros((N,T))
    for t in range(T):
        print(t)
        # Booking and drop-in
        for jj in range(N):
            if (EVs[jj].charge_state <= charge_trigger) & (jj+1 not in stations[:,t]): # battery below trigger and not already charging --> drop-in
                charge_duration = np.random.randint((charge_trigger-EVs[jj].charge_state+1),(100 - EVs[jj].charge_state)) # random charge duration
                section = stations[:,t:t+charge_duration]
                if any(np.sum(section,axis=1) == 0):
                    station_to_book = np.where(np.sum(section,axis=1) == 0)[0][0]
                    stations[station_to_book,t:t+charge_duration] = jj+1
                else:
                    dropin_blockages[jj,t] = 1
                
            elif (EVs[jj].booker) & (jj+1 not in stations[:,t:]): # booker and not already charging --> booking at trigger time
                remaining_time = EVs[jj].charge_state - charge_trigger
                booking_time = t + remaining_time
                booking_duration = np.random.randint(1,(100 - charge_trigger)) # random charge duration
                section = stations[:,booking_time:booking_time+booking_duration] 
                if any(np.sum(section,axis=1) == 0):
                    station_to_book = np.where(np.sum(section,axis=1) == 0)[0][0]
                    stations[station_to_book,booking_time:booking_time+booking_duration] = jj+1 
                else:
                    booking_blockages[jj,t] = 1
                EVs[jj].discharge()
            elif jj+1 not in stations[:,t]:
                EVs[jj].discharge()
            else:
                EVs[jj].charge()
            # Update history
            EVs[jj].update_history()
    ### data extraction ###
    occupation = np.where(stations > 0.5, 1, 0)
    ### separate bookers and drop-ins to see waiting times
    all_waiting_times = []
    for ii in range(N):
        diff  =  np.diff(dropin_blockages[ii])
        waiting_start = np.where(diff == 1)
        waiting_end = np.where(diff == -1)
        unended_wait = len(waiting_start[0]) - len(waiting_end[0]) 
        if unended_wait:
            waiting_times = waiting_end[0] - waiting_start[0][:-unended_wait] # last start has no end
        else:
            waiting_times = waiting_end[0] - waiting_start[0] 
        # print(f"Average waiting time for vehicle {ii} is: ",np.mean(waiting_times))
        all_waiting_times.append(list(waiting_times))
    results = {"waiting_times":all_waiting_times,
               "dropin_blockages":dropin_blockages,
               "booking_blockages":booking_blockages,
               "occupation":occupation,
               "stations":stations,
               "EVs":EVs
               }
    return results

def analysis(results,figname):
    # unpack results
    dropin_blockages = results["dropin_blockages"]
    booking_blockages = results["booking_blockages"]
    occupation = results["occupation"]
    stations = results["stations"]
    EVs = results["EVs"]
    waiting_times = results["waiting_times"]

    # Create subplots
    fig, axs = plt.subplots(5, 1, figsize=(10, 16))

    # Plot 1 - Occupation
    axs[0].plot(np.sum(occupation, axis=0))
    axs[0].set_ylabel("Occupation")
    axs[0].set_xlabel("Time")

    # Plot 2 - Drop-in blockages
    axs[1].plot(np.sum(dropin_blockages, axis=0))
    axs[1].set_ylabel("Drop-in blockages")
    axs[1].set_xlabel("Time")

    # Plot 3 - Booking blockages
    axs[2].plot(np.sum(booking_blockages, axis=0))
    axs[2].set_ylabel("Booking blockages")
    axs[2].set_xlabel("Time")

    # Plot 4 - Free stations
    free_stations = np.sum(stations == 0, axis=0)
    axs[3].plot(free_stations)
    axs[3].set_ylabel("Free stations")
    axs[3].set_xlabel("Time")

    # Plot 5 - Total waiting times
    total_waiting_times = [sum(ii) for ii in waiting_times]
    axs[4].hist(total_waiting_times, bins=10)
    axs[4].set_ylabel("waiting times per ev")

    # Adjust spacing between subplots
    plt.tight_layout()
    # Show the figure
    plt.savefig(f"{figname}.png")
    plt.show()
    return 0


if __name__ == "__main__":
    # Number of EVs
    N = 10
    # Number of charging stations
    M = 5
    # Time horizon
    T = 500
    charge_trigger = 50
    results = main(M,N,T,charge_trigger,"random")
    analysis(results,"random")




            







