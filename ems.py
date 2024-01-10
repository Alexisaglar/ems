class EnergyManagementSystem:
    def __init__(self):
        # Initialize the battery charge level (in kWh)
        self.battery_charge = 10  # Example: 10 kWh initial charge
        self.battery_capacity = 20  # Example: 20 kWh capacity

        # Example data for solar production and house load (in kWh)
        self.solar_production = [5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1, 0]  # Hourly production
        self.house_load = [2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 2, 2]  # Hourly consumption

    def simulate_one_hour(self, hour):
        solar = self.solar_production[hour]
        load = self.house_load[hour]

        net_production = solar - load  # Net solar production after household consumption

        # Charge or discharge the battery based on net production
        if net_production > 0:
            # Charge the battery
            charge_potential = self.battery_capacity - self.battery_charge
            charge_amount = min(net_production, charge_potential)
            self.battery_charge += charge_amount
        elif net_production < 0:
            # Discharge the battery
            discharge_amount = min(-net_production, self.battery_charge)
            self.battery_charge -= discharge_amount

        print(f"Hour {hour}:")
        print(f"  Solar Production: {solar} kWh, House Load: {load} kWh")
        print(f"  Battery Charge: {self.battery_charge:.2f} kWh\n")

    def run_simulation(self):
        for hour in range(12):  # Simulate for 12 hours
            self.simulate_one_hour(hour)

if __name__ == "__main__":
    ems = EnergyManagementSystem()
    ems.run_simulation()
