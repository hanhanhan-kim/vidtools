"""
Utility functions for helping with video analyses. 
"""

def ask_yes_no(question, default="yes"):

    """
    Ask a yes/no question and return the answer.

    Parameters:
    -----------
    question (str): The question to ask the user. 
    default: The presumed answer if the user hits only <Enter>. 
        Can be either "yes", "no", or None. Default is "yes".

    Returns:
    ---------
    bool
    """

    valid = {"yes": True, "y": True,
             "no": False, "n": False}

    if default is None:
        prompt = "[y/n]\n"
    elif default == "yes":
        prompt = "[Y/n]\n"
    elif default == "no":
        prompt = "[y/N]\n"
    else:
        raise ValueError(f"invalid default answer: {default}")

    while True:

        print(f"{question} {prompt}")
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes'/'y' or 'no'/'n'. \n")


def flatten_list(list_of_lists):
    
    """
    Flatten a list of lists into a list.
    Parameters:
    -----------
    list_of_lists: A list of lists
    Returns:
    --------
    A list.
    """
    
    # Reach into each inner list and append into a new list: 
    flat_list = [item for inner_list in list_of_lists for item in inner_list]

    return flat_list