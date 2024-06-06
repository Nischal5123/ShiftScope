import json
import numpy as np
from sklearn.cluster import KMeans
from scipy.spatial import distance
import matplotlib.pyplot as plt

def get_cluster_plot(rl_data, random_data, momentum_data, user_data):
    # Extract attribute preferences into arrays
    rl_preferences = np.array(list(rl_data.values()))
    random_preferences = np.array(list(random_data.values()))
    momentum_preferences = np.array(list(momentum_data.values()))
    user_preferences = np.array(list(user_data.values()))

    # Reshape arrays to have 1 dimension
    rl_preferences = rl_preferences.flatten()
    random_preferences = random_preferences.flatten()
    momentum_preferences = momentum_preferences.flatten()
    user_preferences = user_preferences.flatten()

    # Cluster Analysis
    kmeans_rl = KMeans(n_clusters=3)  # Example: 3 clusters
    kmeans_random = KMeans(n_clusters=3)
    kmeans_momentum = KMeans(n_clusters=3)
    rl_clusters = kmeans_rl.fit_predict(rl_preferences.reshape(-1, 1))
    random_clusters = kmeans_random.fit_predict(random_preferences.reshape(-1, 1))
    momentum_clusters = kmeans_momentum.fit_predict(momentum_preferences.reshape(-1, 1))

    # User Comparison
    rl_centroids = kmeans_rl.cluster_centers_
    random_centroids = kmeans_random.cluster_centers_
    momentum_centroids = kmeans_momentum.cluster_centers_

    # Concatenate data points and cluster labels
    all_data = np.concatenate((rl_preferences, random_preferences, momentum_preferences, user_preferences), axis=0)
    all_cluster_labels = np.concatenate((rl_clusters, random_clusters, momentum_clusters, [3] * len(user_preferences)),
                                        axis=0)

    # Calculate distances between user preferences and centroids
    rl_distances = [distance.euclidean(user_preferences, centroid) for centroid in rl_centroids]
    random_distances = [distance.euclidean(user_preferences, centroid) for centroid in random_centroids]
    momentum_distances = [distance.euclidean(user_preferences, centroid) for centroid in momentum_centroids]

    # Find the minimum distance for each algorithm
    rl_distance = min(rl_distances)
    random_distance = min(random_distances)
    momentum_distance = min(momentum_distances)

    # Determine the closest algorithm to the user
    distances = {
        "RL": rl_distance,
        "Random": random_distance,
        "Momentum": momentum_distance
    }
    print("Distances:", distances)
    closest_algorithm = min(distances, key=distances.get)
    print("User is closest to:", closest_algorithm)

    # Plot clusters
    plt.figure(figsize=(10, 8))
    plt.scatter(all_data, all_data, c=all_cluster_labels, cmap='viridis', marker='o', alpha=0.5, label='Data Points')

    # Label each cluster
    for i, txt in enumerate(all_cluster_labels):
        if txt == 0:
            plt.annotate('RL', (all_data[i], all_data[i]), textcoords="offset points", xytext=(-10, -5), ha='center')
        elif txt == 1:
            plt.annotate('Random', (all_data[i], all_data[i]), textcoords="offset points", xytext=(-10, -5),
                         ha='center')
        elif txt == 2:
            plt.annotate('Momentum', (all_data[i], all_data[i]), textcoords="offset points", xytext=(-10, -5),
                         ha='center')
        elif txt == 3:
            plt.annotate('User', (all_data[i], all_data[i]), textcoords="offset points", xytext=(-10, -5), ha='center')

    plt.title('Clusters of Algorithms and User Preferences')
    plt.xlabel('Attribute')
    plt.ylabel('Attribute')
    plt.legend()
    plt.grid(True)
    plt.show()

def precision_recall(rl_attributes_history, random_attributes_history, momentum_attributes_history, user_attributes_history):
    # Convert attribute history to sets for faster membership checking
    rl_attribute_set = {tuple(attr) for attr in rl_attributes_history}
    random_attribute_set = {tuple(attr) for attr in random_attributes_history}
    momentum_attribute_set = {tuple(attr) for attr in momentum_attributes_history}
    user_attribute_set = {tuple(attr) for attr in user_attributes_history}

    # Calculate True Positives, False Positives, and False Negatives
    rl_tp = len(rl_attribute_set.intersection(user_attribute_set))
    rl_fp = len(rl_attribute_set.difference(user_attribute_set))
    rl_fn = len(user_attribute_set.difference(rl_attribute_set))

    random_tp = len(random_attribute_set.intersection(user_attribute_set))
    random_fp = len(random_attribute_set.difference(user_attribute_set))
    random_fn = len(user_attribute_set.difference(random_attribute_set))

    momentum_tp = len(momentum_attribute_set.intersection(user_attribute_set))
    momentum_fp = len(momentum_attribute_set.difference(user_attribute_set))
    momentum_fn = len(user_attribute_set.difference(momentum_attribute_set))

    # Calculate Precision and Recall
    rl_precision = rl_tp / (rl_tp + rl_fp) if rl_tp + rl_fp > 0 else 0
    rl_recall = rl_tp / (rl_tp + rl_fn) if rl_tp + rl_fn > 0 else 0

    random_precision = random_tp / (random_tp + random_fp) if random_tp + random_fp > 0 else 0
    random_recall = random_tp / (random_tp + random_fn) if random_tp + random_fn > 0 else 0

    momentum_precision = momentum_tp / (momentum_tp + momentum_fp) if momentum_tp + momentum_fp > 0 else 0
    momentum_recall = momentum_tp / (momentum_tp + momentum_fn) if momentum_tp + momentum_fn > 0 else 0

    # Plot precision-recall graph
    plt.figure(figsize=(8, 6))
    plt.plot([0, 1], [1, 0], linestyle='--', color='gray')  # Add diagonal line for reference
    plt.plot(rl_recall, rl_precision, label='RL', marker='o')
    plt.plot(random_recall, random_precision, label='Random', marker='o')
    plt.plot(momentum_recall, momentum_precision, label='Momentum', marker='o')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend()
    plt.grid(True)
    plt.show()




def accuracy(rl_attributes_history, random_attributes_history, momentum_attributes_history, user_attributes_history):


    # Initialize counters
    rl_count, random_count, momentum_count = 0, 0, 0

    # Iterate over each user attribute history
    for user_attributes in user_attributes_history:
        # Convert user_attributes to a tuple for comparison
        user_attributes_tuple = tuple(user_attributes)

        # Check if user attributes are in RL attribute history
        if user_attributes_tuple in map(tuple, rl_attributes_history):
            rl_count += 1

        # Check if user attributes are in Random attribute history
        if user_attributes_tuple in map(tuple, random_attributes_history):
            random_count += 1

        # Check if user attributes are in Momentum attribute history
        if user_attributes_tuple in map(tuple, momentum_attributes_history):
            momentum_count += 1

    # Calculate accuracy for each algorithm
    rl_accuracy = rl_count / len(user_attributes_history)
    random_accuracy = random_count / len(user_attributes_history)
    momentum_accuracy = momentum_count / len(user_attributes_history)

    return rl_accuracy, random_accuracy, momentum_accuracy


def accuracy_over_time(rl_attributes_history, random_attributes_history, momentum_attributes_history, user_attributes_history):
    # Initialize lists to store accuracies over time
    rl_accuracies, random_accuracies, momentum_accuracies = [], [], []

    # Iterate over time steps
    for i in range(1, len(user_attributes_history) + 1):
        # Compute accuracies up to the current time step
        rl_accuracy, random_accuracy, momentum_accuracy = accuracy(rl_attributes_history[:i],
                                                                    random_attributes_history[:i],
                                                                    momentum_attributes_history[:i],
                                                                    user_attributes_history[:i])
        # Append accuracies to lists
        rl_accuracies.append(rl_accuracy)
        random_accuracies.append(random_accuracy)
        momentum_accuracies.append(momentum_accuracy)

    return rl_accuracies, random_accuracies, momentum_accuracies


if __name__ == '__main__':
    # Load JSON data for each algorithm
    with open('Greedy_distribution_map.json', 'r') as file:
        rl_data = json.load(file)

    with open('Random_distribution_map.json', 'r') as file:
        random_data = json.load(file)

    with open('Momentum_distribution_map.json', 'r') as file:
        momentum_data = json.load(file)

    with open('distribution_map.json', 'r') as file:
        user_data = json.load(file)

    # Load attribute history numpy arrays
    path = 'performance-data/'
    rl_attributes_history = np.load(path + 'rl_attributes_history.npy', allow_pickle=True)
    random_attributes_history = np.load(path + 'random_attributes_history.npy', allow_pickle=True)
    momentum_attributes_history = np.load(path + 'momentum_attributes_history.npy', allow_pickle=True)
    user_attributes_history = np.load(path + 'user_attributes_history.npy', allow_pickle=True)

    # Sort each array inside the arrays so that order doesn't matter
    rl_attributes_history = np.array([sorted(arr) for arr in rl_attributes_history])
    random_attributes_history = np.array([sorted(arr) for arr in random_attributes_history])
    momentum_attributes_history = np.array([sorted(arr) for arr in momentum_attributes_history])
    user_attributes_history = np.array([sorted(arr) for arr in user_attributes_history])

    # Convert attribute history to numpy arrays
    rl_attributes_history = np.array(rl_attributes_history)
    random_attributes_history = np.array(random_attributes_history)
    momentum_attributes_history = np.array(momentum_attributes_history)
    user_attributes_history = np.array(user_attributes_history)

    # Make sure all histories are the same length, otherwise trim the longer ones
    min_length = min(len(rl_attributes_history), len(random_attributes_history), len(momentum_attributes_history),
                     len(user_attributes_history))
    rl_attributes_history = rl_attributes_history[:min_length]
    random_attributes_history = random_attributes_history[:min_length]
    momentum_attributes_history = momentum_attributes_history[:min_length]
    user_attributes_history = user_attributes_history[:min_length]

    # rl_accuracy, random_accuracy, momentum_accuracy = accuracy(rl_attributes_history, random_attributes_history, momentum_attributes_history, user_attributes_history)
    # print("RL Accuracy:", rl_accuracy)
    # print("Random Accuracy:", random_accuracy)
    # print("Momentum Accuracy:", momentum_accuracy)

    rl_accuracies, random_accuracies, momentum_accuracies = accuracy_over_time(rl_attributes_history, random_attributes_history, momentum_attributes_history, user_attributes_history)
    #save these accuracies to a json file time:
    # Plot accuracies over time
    print(rl_accuracies)
    print(random_accuracies)
    print(momentum_accuracies)

    plt.figure(figsize=(10, 6))
    time_steps = range(1, len(user_attributes_history) + 1)
    plt.plot(time_steps, rl_accuracies, label='RL', color='blue')
    plt.plot(time_steps, random_accuracies, label='Random', color='orange')
    plt.plot(time_steps, momentum_accuracies, label='Momentum', color='green')
    plt.xlabel('Time Step')
    plt.ylabel('Accuracy')
    plt.title('Algorithm Accuracy Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()


    # Calculate precision and recall for each algorithm
    # rl_precision, rl_recall, random_precision, random_recall, momentum_precision, momentum_recall = \
    #     precision_recall(rl_attributes_history, random_attributes_history, momentum_attributes_history,
    #                      user_attributes_history)




