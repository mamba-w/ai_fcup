import csv  # Import the CSV module to handle CSV file operations
import math  # Import the math module to perform mathematical operations
from collections import Counter  # Import Counter from collections module to count occurrences of elements

# Define a class for tree nodes used in the decision tree
class TreeNode:
    def __init__(self, attribute=None):
        self.attribute = attribute  # Attribute used for splitting at this node
        self.children = {}  # Dictionary to store children nodes
        self.class_label = None  # Class label for leaf nodes
        self.counter = Counter()  # Counter to keep track of class label occurrences

# Function to read CSV file and return the data as a list of dictionaries
def read_csv(file_path):
    data = []  # Initialize an empty list to store the data
    with open(file_path, 'r') as file:  # Open the CSV file in read mode
        reader = csv.DictReader(file)  # Create a CSV reader object to read the file as a dictionary
        for row in reader:  # Iterate over each row in the CSV file
            cleaned_row = {key: value for key, value in row.items() if key != 'ID'}  # Skip the 'ID' column
            data.append(cleaned_row)  # Append the cleaned row to the data list
    return data  # Return the list of dictionaries

# Function to calculate the entropy of a dataset for a given class label
def entropy(data, class_label):
    if not data:  # If data is empty, return 0
        return 0
    label_column = [row[class_label] for row in data]  # Extract the class label column
    label_counts = Counter(label_column)  # Count occurrences of each class label
    entropy_val = 0  # Initialize entropy value
    total_examples = len(data)  # Get the total number of examples in the data
    for label in label_counts:  # Iterate over each class label
        label_prob = label_counts[label] / total_examples  # Calculate the probability of the class label
        entropy_val -= label_prob * math.log2(label_prob)  # Update the entropy value
    return entropy_val  # Return the calculated entropy

# Function to calculate the information gain of an attribute
def information_gain(data, attribute, class_label):
    attribute_values = set([row[attribute] for row in data])  # Get unique values of the attribute
    total_examples = len(data)  # Get the total number of examples in the data
    attribute_entropy = 0  # Initialize the attribute entropy
    for value in attribute_values:  # Iterate over each unique value of the attribute
        subset = [row for row in data if row[attribute] == value]  # Get the subset of data with the attribute value
        subset_entropy = entropy(subset, class_label)  # Calculate the entropy of the subset
        subset_size = len(subset)  # Get the size of the subset
        attribute_entropy += (subset_size / total_examples) * subset_entropy  # Update the attribute entropy
    return entropy(data, class_label) - attribute_entropy  # Return the information gain

# Function to choose the best attribute for splitting the data
def choose_best_attribute(data, attributes, class_label):
    gains = {attr: information_gain(data, attr, class_label) for attr in attributes}  # Calculate information gain for each attribute
    best_attribute = max(gains, key=gains.get)  # Find the attribute with the maximum information gain
    return best_attribute  # Return the best attribute

# Function to build the decision tree   
def build_tree(data, attributes, class_label):
    if not data:  # If data is empty, return None
        return None

    node = TreeNode()  # Create a new tree node

    class_column = [row[class_label] for row in data]  # Extract the class label column
    if len(set(class_column)) == 1:  # If all examples have the same class label
        node.class_label = class_column[0]  # Set the class label of the node
        node.counter = Counter(class_column)  # Set the counter for the class label
        return node  # Return the node

    best_attribute = choose_best_attribute(data, attributes, class_label)  # Choose the best attribute to split on
    node.attribute = best_attribute  # Set the attribute of the node

    attribute_values = set([row[best_attribute] for row in data])  # Get unique values of the best attribute
    for value in attribute_values:  # Iterate over each unique value of the best attribute
        subset = [row for row in data if row[best_attribute] == value]  # Get the subset of data with the attribute value
        child_node = build_tree(subset, [attr for attr in attributes if attr != best_attribute], class_label)  # Build the subtree
        node.children[value] = child_node  # Add the subtree as a child of the current node

    return node  # Return the node

# Function to print the decision tree
def print_tree(node, depth=0):
    if node.class_label:  # If the node is a leaf node
        print(f"{'    ' * depth}<Leaf> {node.class_label} ({', '.join(f'{k}: {v}' for k, v in node.counter.items())})") 
    else:  # If the node is an internal node
        print(f"{'    ' * depth}<{node.attribute}>")  # Print the attribute
        for value, child_node in node.children.items():  # Iterate over each child node
            print(f"{'    ' * (depth + 1)}{value}: ", end='')  # Print the attribute value
            print_tree(child_node, depth + 2)  # Recursively print the child node

# Function to classify a new instance using the decision tree
def classify(instance, node):
    if node.class_label:  # If the node is a leaf node
        return node.class_label  # Return the class label

    attribute_value = instance.get(node.attribute)  # Get the attribute value of the instance
    if attribute_value is None or attribute_value not in node.children:  # If the attribute value is unknown
        return "Unknown"  # Return "Unknown"

    return classify(instance, node.children[attribute_value])  # Recursively classify the instance using the child node

# Main function to read data, build the decision tree, and classify a new instance
def main():
    file_path = input("Enter the path to the CSV file: ")  # Prompt user to enter the path to the CSV file
    data = read_csv(file_path)  # Read the CSV file and get the data

    attributes = list(data[0].keys())  # Extract attribute names from the header
    if 'ID' in attributes:  # If 'ID' is in the list of attributes
        attributes.remove('ID')  # Remove 'ID' from the list of attributes

    class_label = attributes[-1]  # Last remaining column is assumed to be the class label
    attributes = attributes[:-1]  # Exclude the class label column

    root_node = build_tree(data, attributes, class_label)  # Build the decision tree
    print("Decision Tree:")  # Print a message
    print_tree(root_node)  # Print the decision tree

    new_instance = {}  # Initialize an empty dictionary for the new instance
    for attribute in attributes:  # Iterate over each attribute
        value = input(f"Enter value for '{attribute}': ")  # Prompt user to enter the value for the attribute
        new_instance[attribute] = value  # Add the attribute value to the new instance

    predicted_class = classify(new_instance, root_node)  # Classify the new instance using the decision tree
    print(f"Predicted class for the new instance: {predicted_class}")  # Print the predicted class

if __name__ == "__main__":
    main()  # Execute the main function
