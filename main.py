import csv
from collections import Counter
import random


# Function to read data from CSV file
def read_data(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        data = [row for row in reader]
    return data


# Function to extract winning numbers from the data
def extract_winning_numbers(data):
    winning_numbers = []
    powerball_numbers = []
    for row in data:
        if row[8] != '':
            for item in row[2:9]:
                number = int(item)
                winning_numbers.append(number)
            powerball_numbers.append(int(row[9]))
    return winning_numbers, powerball_numbers


# Function to calculate number frequencies
def calculate_frequencies(numbers):
    counter = Counter(numbers)
    most_common = counter.most_common(10)
    return most_common


# Read data
data = read_data('powerball.csv')

# Extract winning numbers
winning_numbers, powerball_numbers = extract_winning_numbers(data)

# Calculate frequencies
most_common = calculate_frequencies(winning_numbers)
most_common_powerball = calculate_frequencies(powerball_numbers)

print(f"Most common numbers: {most_common}")
print(f"Most common powerball numbers: {most_common_powerball}")


# Function to extract pairs of winning numbers from the data
def extract_number_pairs(data):
    pairs = []
    for row in data:
        if row[8] != '':
            for i in range(2, 8):  # For each pair of winning numbers in a row
                pair = tuple(sorted((int(row[i]), int(row[i + 1]))))  # Store pairs as sorted tuples
                pairs.append(pair)
    return pairs


# Extract pairs
pairs = extract_number_pairs(data)

# Calculate frequencies
pair_frequencies = calculate_frequencies(pairs)

print(f"Most common pairs: {pair_frequencies}")


def calculate_last_appearance(data):
    last_appearance = {}
    step = 0
    for row in data:
        if row[8] != '':
            for i in range(2, 8):
                number = int(row[i])
                if number not in last_appearance:
                    last_appearance[number] = step
        step += 1
    return last_appearance


since_last_appearance = calculate_last_appearance(data)
print("Draws since last drawn: ", since_last_appearance)


# Function to calculate hot and cold numbers
def calculate_hot_and_cold_numbers(data, draw_period=50):
    # Extract last 'draw_period' draws
    recent_data = data[:draw_period]

    # Extract winning numbers from recent data
    recent_winning_numbers, _ = extract_winning_numbers(recent_data)

    # Calculate frequencies of recent winning numbers
    recent_number_frequencies = calculate_frequencies(recent_winning_numbers)

    # Sort the number frequencies by frequency
    sorted_recent_number_frequencies = sorted(recent_number_frequencies, key=lambda x: x[1])

    # Extract hot and cold numbers
    hot_numbers = sorted_recent_number_frequencies[-5:]  # 5 most frequent numbers
    cold_numbers = sorted_recent_number_frequencies[:5]  # 5 least frequent numbers

    return hot_numbers, cold_numbers


# Calculate hot and cold numbers
hot_numbers, cold_numbers = calculate_hot_and_cold_numbers(data)

print(f"Hot numbers: {hot_numbers}")
print(f"Cold numbers: {cold_numbers}")

# Step 1: Initial weight for all numbers
weights = {i: 1 for i in range(1, 36)}

# Step 2: Adjust weights based on most common, hot, cold numbers, common pairs, and last appearance
most_common_dict = dict(most_common)
hot_numbers_dict = dict((i[0], i[1]) for i in hot_numbers)
cold_numbers_dict = dict((i[0], i[1]) for i in cold_numbers)
common_pairs_dict = dict(pair_frequencies)

# Adjust weight based on commonness
for number in weights.keys():
    freq = most_common_dict.get(number, 0)
    weights[number] *= 1 + freq / sum(most_common_dict.values())

# Adjust weight based on hotness
for number in weights.keys():
    freq = hot_numbers_dict.get(number, 0)
    weights[number] *= 1 + freq / sum(hot_numbers_dict.values())

# Adjust weight based on coldness
for number in weights.keys():
    freq = cold_numbers_dict.get(number, 0)
    weights[number] *= 1 + freq / sum(cold_numbers_dict.values())

# Adjust weight based on pairs
for pair, freq in common_pairs_dict.items():
    n1, n2 = pair
    # If number is part of a common pair, increase its weight
    weights[n1] *= 1 + freq / sum(common_pairs_dict.values())
    weights[n2] *= 1 + freq / sum(common_pairs_dict.values())

# Adjust weight based on last appearance
max_draws = max(since_last_appearance.values())
for number, last_seen in since_last_appearance.items():
    weights[number] *= 1 + (max_draws - last_seen) / max_draws  # more weight if not seen for long

# Normalize the weights
total_weight = sum(weights.values())
weights = {number: weight / total_weight for number, weight in weights.items()}

print("weights: ", weights)


# Function to pick number with weights
def pick_number_with_weights(weights):
    numbers = list(weights.keys())
    probs = list(weights.values())
    return random.choices(numbers, weights=probs, k=1)[0]

# Powerball weight calculation
powerball_weights = {i: 1 for i in range(1, 21)}
most_common_powerball_dict = dict(most_common_powerball)

for number in powerball_weights.keys():
    freq = most_common_powerball_dict.get(number, 0)
    powerball_weights[number] *= 1 + freq / sum(most_common_powerball_dict.values())

total_powerball_weight = sum(powerball_weights.values())
powerball_weights = {number: weight / total_powerball_weight for number, weight in powerball_weights.items()}

def pick_powerball_number_with_weights(powerball_weights):
    numbers = list(powerball_weights.keys())
    probs = list(powerball_weights.values())
    return random.choices(numbers, weights=probs, k=1)[0]

def generate_combination():
    # Draw 7 unique numbers for the combination
    combination = sorted(random.sample(list(weights.keys()), 7))

    # Generate a Powerball number
    powerball = pick_powerball_number_with_weights(powerball_weights)

    combination.append(powerball)

    return combination


# Generate X combinations
def generate_multiple_combinations(x):
    combinations = set()
    while len(combinations) < x:
        comb = tuple(generate_combination())
        combinations.add(comb)
    return list(combinations)


# Print 10 combinations for testing
for comb in generate_multiple_combinations(5):
    print(comb)
