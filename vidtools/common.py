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


def parse_readme_for_docstrings(readme_path):
    
    """
    Extract docstrings for functions from the `README.md` file.
    From the path to the `README.md`, returns a list of docstrings. 
    """

    with open(readme_path, "r") as f:
        readme = f.readlines()
    
    # Extract command names from README.md to use as keys:
    keys = [readme[i-2] for i, line in enumerate(readme) if line.startswith("<details><summary>")]
    keys = [key[6:-2] for key in keys]
    
    # Extract docstring start and end lines from README.md:
    start_lines = []
    end_lines = []
    for i, line in enumerate(readme):

        if line.startswith("<details>"):
            start_lines.append(i+2)

        if line.startswith("</details>"):
            end_lines.append(i-1)
    
    # Generate docstrings from start and end lines:
    docstrings = ["".join(readme[start_line:end_line+1])
                  for start_line, end_line in zip(start_lines, end_lines)] 
    docstrings = [docstring[1:] for docstring in docstrings]
    
    # Put it together to make the desired dictionary:
    cmds_docstrings = dict(zip(keys, docstrings))
    
    # # Handle the strange cases that need formatting:
    # to_reformat = cmds_docstrings["expt-pt-to-pt"]
    # idx = to_reformat.find("Initialization (homing, etc.)") - 1
    # keep_rewrapped = to_reformat[:idx]
    # not_rewrapped = to_reformat[idx:]
    # # Update dictionary with reformatted docstring:
    # cmds_docstrings["expt-pt-to-pt"] = [keep_rewrapped, not_rewrapped]
    
    return cmds_docstrings


def docstring_parameter(*sub):

    """
    Modify the __doc__ object so I can pass in variables 
    to the docsring
    """

    def dec(obj):
        obj.__doc__ = obj.__doc__.format(*sub)
        return obj
    return dec