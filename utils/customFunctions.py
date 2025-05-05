# includes custom from the rest of the repository where I want to simpplify the code

# =======================================================================================================================
# Following functions is copied from the file Grain_size_
# =======================================================================================================================
def read_csv(path, bags):
    """
    Reads CSV files with grain size data and puts it in a dictionary of DataFrames.

    Parameters:
    - path (str or Path): Base path of CSV files.
    - bags (list of str): List of bag name strings.

    Returns:
    - df (dict): Dictionary containing DataFrames of data for each bag.
    """
    df = {}
    base_path = Path(path)
    for bag in bags:
        print(bag)
        # Define the path for the current bag using pathlib for robust path handling
        bag_path = base_path / bag
        # Find all CSV files in the directory, ensuring a consistent sorting mechanism
        files = sorted(bag_path.glob("*.csv"), key=lambda x: x.stem)
        print("# files:", len(files))

        # Initialize an empty DataFrame for aggregating data from all files for the current bag
        df_bag = pd.DataFrame()
        for i, file_path in enumerate(files):
            # Read CSV file
            new_df = pd.read_csv(file_path)
            # Assign 'crop_image' based on file order, similar to original function's intention
            new_df["crop_image"] = i
            # Concatenate the newly read DataFrame into the aggregated DataFrame
            df_bag = pd.concat([df_bag, new_df], ignore_index=True)

        # Assign the aggregated DataFrame to the corresponding bag in the output dictionary
        df[bag] = df_bag

    return df

def sizes_depth(df, list_bags):
    """
    Create a dataset of grain sizes over depth for each bag.

    Parameters:
    - df (dict): Dictionary of DataFrames with grain parameters for each bag.
    - list_bags (array-like): List of complete bags identifiers.

    Returns:
    - df_sizes (dict): Dictionary of DataFrames with grain sizes over depth data for each bag.
    """
    df_sizes = {}
    for bag in list_bags:  # Loop over bags
        print(bag)
        # Initialize DataFrame for storing results for the current bag
        columns = [
            "crop_image",
            "depth[m]",
            "equivalent_diameter[px]",
            "grain_size[px]",
            "grain_size_err[px]",
        ]
        df_sizes[bag] = pd.DataFrame(columns=columns)

        # Prepare bag identifiers for the first and second set of images
        bag_1, bag_2 = bag + "_1", bag + "_2"
        depth = [0]  # Starting depth

        # Check if bag_2 exists, otherwise use bag_1 as a fallback
        df_bag_2 = df.get(bag_2, df[bag_1])

        # Unique crop images in the first set (assuming the same for the second set if exists)
        crop_images = np.unique(df[bag_1].crop_image)

        for i, crop_image in enumerate(crop_images):  # Loop over cropped images
            # Extracting data for the current and next crop image in the sequence
            df_img1_i = df[bag_1][df[bag_1].crop_image == crop_image]
            df_img2_i = df_bag_2[
                df_bag_2.crop_image == crop_image
            ]  # Fixed syntax error

            # Loop over depth steps within the image
            for ii in range(int(len_img / step_size)):
                x_img = step_size * ii + step_size / 2
                if i != 0 and x_img < overlap:  # Handling overlap
                    continue

                depth.append(
                    depth[-1] + step_size * px_to_cm / 100
                )  # Convert step size from pixels to meters

                # Select intervals within current depth step
                df_img1_interval = df_img1_i[
                    (df_img1_i.centroid_x >= x_img - interval_half)
                    & (df_img1_i.centroid_x < x_img + interval_half)
                ]
                df_img2_interval = df_img2_i[
                    (df_img2_i.centroid_x >= x_img - interval_half)
                    & (df_img2_i.centroid_x < x_img + interval_half)
                ]

                df_img_interval = pd.concat(
                    [df_img1_interval, df_img2_interval], ignore_index=True
                )

                # Calculate mean grain size and diameter for the current interval
                new_size = np.mean(df_img_interval.area)
                new_diameter = np.mean(df_img_interval.equivalent_diameter)

                # Store the results
                new_row = {
                    "crop_image": crop_image,
                    "depth[m]": depth[-1],
                    "equivalent_diameter[px]": new_diameter,
                    "grain_size[px]": new_size,
                    "grain_size_err[px]": 0,
                }
                df_sizes[bag] = pd.concat(
                    [df_sizes[bag], pd.DataFrame([new_row])], ignore_index=True
                )

    return df_sizes

# =======================================================================================================================